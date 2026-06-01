"""FastAPI application for AI-powered cloud migration assessment."""

from __future__ import annotations

import asyncio
import base64
import binascii
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from app.agents.migration_graph import run_migration_assessment
from app.config import get_settings
from app.schemas import (
    AnalyzeMigrationResponse,
    AuthLoginRequest,
    AuthSessionResponse,
    AuthUser,
    DiagramImageRequest,
    MigrationAssessmentReport,
    MigrationAgentChatRequest,
    MigrationAgentChatResponse,
    PdfReportRequest,
    RebuildAssessmentRequest,
    SourceArchitecture,
)
from app.services.auth import (
    SESSION_COOKIE_NAME,
    authenticate_user,
    create_session_token,
    get_current_user,
    require_permission,
    session_max_age_seconds,
)
from app.services.architecture_generator import generate_target_architecture
from app.services.assessment_insights import build_assessment_insights
from app.services.aws_diagram_generator import generate_aws_diagram_png
from app.services.cloud_mapping import map_services
from app.services.mermaid_generator import generate_mermaid_diagram
from app.services.migration_strategy import (
    generate_benefits,
    generate_drawbacks,
    generate_final_verdict,
    generate_migration_strategy,
    generate_required_changes,
    generate_risks,
)
from app.services.migration_chat import answer_migration_question
from app.services.pdf_generator import markdown_to_pdf_bytes
from app.services.report_generator import build_report


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Cloud Migration Assessment Agent",
    version="0.1.0",
    description="Analyze cloud architecture diagrams and generate migration assessments.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8001",
        "http://localhost:8000",
        "http://localhost:8001",
        "null",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def ui() -> RedirectResponse:
    return RedirectResponse(url="/static/index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/login", response_model=AuthSessionResponse)
async def login(request: AuthLoginRequest, response: Response) -> AuthSessionResponse:
    return _create_session_response(request, response)


@app.post("/api/session", response_model=AuthSessionResponse)
async def create_session(request: AuthLoginRequest, response: Response) -> AuthSessionResponse:
    return _create_session_response(request, response)


def _create_session_response(request: AuthLoginRequest, response: Response) -> AuthSessionResponse:
    settings = get_settings()
    user = authenticate_user(request, settings=settings)
    token = create_session_token(user, settings=settings)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=session_max_age_seconds(settings),
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return AuthSessionResponse(user=user)


@app.post("/auth/logout")
async def logout(response: Response) -> dict[str, str]:
    return _delete_session_response(response)


@app.delete("/api/session")
async def delete_session(response: Response) -> dict[str, str]:
    return _delete_session_response(response)


def _delete_session_response(response: Response) -> dict[str, str]:
    response.delete_cookie(key=SESSION_COOKIE_NAME, samesite="lax", secure=False)
    return {"status": "signed_out"}


@app.get("/auth/me", response_model=AuthSessionResponse)
async def me(user: Annotated[AuthUser, Depends(get_current_user)]) -> AuthSessionResponse:
    return AuthSessionResponse(user=user)


@app.get("/api/session", response_model=AuthSessionResponse)
async def current_session(
    user: Annotated[AuthUser, Depends(get_current_user)],
) -> AuthSessionResponse:
    return AuthSessionResponse(user=user)


@app.post("/analyze-migration", response_model=AnalyzeMigrationResponse)
async def analyze_migration(
    file: Annotated[UploadFile, File(description="Architecture diagram image or PDF")],
    source_provider: Annotated[str, Form()] = "auto",
    target_provider: Annotated[str, Form()] = "aws",
    migration_intent: Annotated[str | None, Form()] = None,
    goals: Annotated[str | None, Form()] = None,
    _user: AuthUser = Depends(require_permission("can_assess")),
) -> AnalyzeMigrationResponse:
    settings = get_settings()
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(file_bytes) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Uploaded file exceeds size limit.")

    try:
        report = await run_migration_assessment(
            file_bytes=file_bytes,
            filename=file.filename or "architecture-diagram",
            content_type=file.content_type,
            source_provider=source_provider,
            target_provider=target_provider,
            migration_intent=migration_intent,
            goals=_parse_goals(goals),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Migration analysis failed: {exc}",
        ) from exc

    return _response_from_report(report, goals=_parse_goals(goals))


@app.post("/rebuild-assessment", response_model=AnalyzeMigrationResponse)
async def rebuild_assessment(
    request: RebuildAssessmentRequest,
    _user: AuthUser = Depends(require_permission("can_assess")),
) -> AnalyzeMigrationResponse:
    """Rebuild mappings, target architecture, report, and insights after user edits."""

    try:
        goals = _goals_with_variant(request.goals, request.architecture_variant)
        source_architecture = _source_with_provider_hint(
            request.source_architecture,
            request.source_provider,
        )
        report = _build_report_from_source(
            source_architecture=source_architecture,
            source_provider=request.source_provider,
            target_provider=request.target_provider,
            migration_intent=request.migration_intent,
            goals=goals,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Assessment rebuild failed: {exc}",
        ) from exc

    return _response_from_report(report, goals=goals)


@app.post("/download-report-pdf")
async def download_report_pdf(
    request: PdfReportRequest,
    _user: AuthUser = Depends(require_permission("can_view")),
) -> Response:
    rendered_diagram_png: bytes | None = None
    rendered_diagram_title = "Generated Architecture Diagram"
    mermaid_diagram_png = None
    if request.include_mermaid_diagram:
        mermaid_diagram_png = _decode_optional_base64_png(
            request.mermaid_diagram_png_base64,
            field_name="mermaid_diagram_png_base64",
        )
    if request.include_rendered_diagram and request.target_architecture is not None:
        try:
            rendered_diagram_png = await asyncio.wait_for(
                asyncio.to_thread(generate_aws_diagram_png, request.target_architecture),
                timeout=35,
            )
            rendered_diagram_title = (
                f"Generated {request.target_architecture.provider.upper()} Architecture Diagram"
            )
        except asyncio.TimeoutError:
            rendered_diagram_png = None
        except RuntimeError as exc:
            raise HTTPException(status_code=501, detail=str(exc)) from exc
    target_provider_for_report = request.target_provider
    if not target_provider_for_report and request.target_architecture is not None:
        target_provider_for_report = request.target_architecture.provider

    try:
        pdf_bytes = await asyncio.wait_for(
            asyncio.to_thread(
                markdown_to_pdf_bytes,
                request.markdown_report,
                include_mermaid_diagram=request.include_mermaid_diagram,
                mermaid_diagram_png=mermaid_diagram_png,
                mermaid_diagram_title="Rendered Mermaid Architecture Diagram",
                rendered_diagram_png=rendered_diagram_png,
                rendered_diagram_title=rendered_diagram_title,
                source_provider=request.source_provider,
                target_provider=target_provider_for_report,
            ),
            timeout=45,
        )
    except asyncio.TimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail="PDF generation timed out while building the report document.",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc

    filename = _safe_pdf_filename(request.filename)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/download-aws-diagram")
async def download_aws_diagram(
    request: DiagramImageRequest,
    _user: AuthUser = Depends(require_permission("can_view")),
) -> Response:
    try:
        png_bytes = generate_aws_diagram_png(request.target_architecture)
    except RuntimeError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc

    filename = _safe_png_filename(request.filename)
    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/ask-migration-agent", response_model=MigrationAgentChatResponse)
async def ask_migration_agent(
    request: MigrationAgentChatRequest,
    _user: AuthUser = Depends(require_permission("can_view")),
) -> MigrationAgentChatResponse:
    try:
        return await answer_migration_question(request)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Migration agent chat failed: {exc}",
        ) from exc


def _parse_goals(goals: str | None) -> list[str]:
    if not goals:
        return []
    return [goal.strip() for goal in goals.split(",") if goal.strip()]


def _goals_with_variant(goals: list[str], architecture_variant: str) -> list[str]:
    variant = (architecture_variant or "balanced").strip().lower()
    result = list(goals or [])
    if variant and variant != "balanced":
        result.append(f"architecture variant: {variant}")
    return result


def _source_with_provider_hint(
    source_architecture: SourceArchitecture,
    source_provider: str,
) -> SourceArchitecture:
    provider = (source_provider or "auto").strip()
    if provider.lower() == "auto":
        return source_architecture
    return source_architecture.model_copy(update={"provider": provider})


def _build_report_from_source(
    *,
    source_architecture: SourceArchitecture,
    source_provider: str,
    target_provider: str,
    migration_intent: str | None,
    goals: list[str],
) -> MigrationAssessmentReport:
    service_mappings = map_services(
        source_architecture=source_architecture,
        target_provider=target_provider,
        migration_intent=migration_intent,
        goals=goals,
    )
    target_architecture = generate_target_architecture(
        source_architecture=source_architecture,
        service_mappings=service_mappings,
        target_provider=target_provider,
        goals=goals,
    )
    required_changes = generate_required_changes(
        source_architecture=source_architecture,
        target_architecture=target_architecture,
        service_mappings=service_mappings,
    )
    mermaid_diagram = generate_mermaid_diagram(target_architecture)
    migration_strategy = generate_migration_strategy(
        source_architecture=source_architecture,
        target_architecture=target_architecture,
        service_mappings=service_mappings,
        goals=goals,
    )
    benefits = generate_benefits(
        target_architecture=target_architecture,
        service_mappings=service_mappings,
    )
    drawbacks = generate_drawbacks(
        source_architecture=source_architecture,
        service_mappings=service_mappings,
    )
    risks = generate_risks(
        source_architecture=source_architecture,
        service_mappings=service_mappings,
    )
    assumptions = [
        *source_architecture.assumptions,
        *source_architecture.missing_information,
    ]
    final_verdict = generate_final_verdict(
        source_architecture=source_architecture,
        service_mappings=service_mappings,
        risks=risks,
        benefits=benefits,
        drawbacks=drawbacks,
    )
    return build_report(
        source_architecture=source_architecture,
        service_mappings=service_mappings,
        required_changes=required_changes,
        target_architecture=target_architecture,
        mermaid_diagram=mermaid_diagram,
        migration_strategy=migration_strategy,
        benefits=benefits,
        drawbacks=drawbacks,
        risks=risks,
        assumptions=assumptions,
        final_verdict=final_verdict,
        analysis_metadata={
            "detection_mode": "user_edited_rebuild",
            "source_provider_hint": source_provider,
        },
    )


def _response_from_report(
    report: MigrationAssessmentReport,
    goals: list[str] | None = None,
) -> AnalyzeMigrationResponse:
    return AnalyzeMigrationResponse(
        markdown_report=report.markdown_report,
        mermaid_diagram=report.mermaid_diagram,
        source_architecture=report.source_architecture,
        target_architecture=report.target_architecture,
        service_mappings=report.service_mappings,
        required_changes=report.required_changes,
        migration_strategy=report.migration_strategy,
        benefits=report.benefits,
        drawbacks=report.drawbacks,
        risks=report.risks,
        assumptions=report.assumptions,
        final_verdict=report.final_verdict,
        analysis_metadata=report.analysis_metadata,
        assessment_insights=build_assessment_insights(report, goals=goals or []),
    )


def _safe_pdf_filename(filename: str) -> str:
    safe = "".join(char for char in filename if char.isalnum() or char in {"-", "_", "."})
    if not safe:
        safe = "migration-assessment.pdf"
    if not safe.lower().endswith(".pdf"):
        safe += ".pdf"
    return safe


def _decode_optional_base64_png(value: str | None, *, field_name: str) -> bytes | None:
    if not value:
        return None
    payload = value.strip()
    if payload.lower().startswith("data:") and "," in payload:
        payload = payload.split(",", 1)[1]
    try:
        return base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}.") from exc


def _safe_png_filename(filename: str) -> str:
    safe = "".join(char for char in filename if char.isalnum() or char in {"-", "_", "."})
    if not safe:
        safe = "aws-architecture.png"
    if not safe.lower().endswith(".png"):
        safe += ".png"
    return safe
