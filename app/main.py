"""FastAPI application for AI-powered cloud migration assessment."""

from __future__ import annotations

import asyncio
import base64
import binascii
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Cookie, Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from app.agents.migration_graph import run_migration_assessment
from app.config import get_settings
from app.schemas import (
    AnalyzeMigrationJsonRequest,
    AnalyzeMigrationResponse,
    AssessmentComparisonRequest,
    AssessmentComparisonResponse,
    AssessmentRecord,
    AssessmentSummary,
    AuditEventRecord,
    AuthLoginRequest,
    AuthSessionResponse,
    AuthUser,
    CostModelInput,
    CostModelResponse,
    DiagramImageRequest,
    DemoSampleMetadata,
    EvidenceCreateRequest,
    EvidenceRecord,
    MigrationAssessmentReport,
    MigrationAgentChatRequest,
    MigrationAgentChatResponse,
    PdfReportRequest,
    PersistAssessmentRequest,
    PersistAssessmentResponse,
    RebuildAssessmentRequest,
    ReviewStateUpdateRequest,
    SsoReadinessResponse,
    SourceArchitecture,
)
from app.services.auth import (
    SESSION_COOKIE_NAME,
    authenticate_user,
    create_session_token,
    get_current_user,
    require_permission,
    session_max_age_seconds,
    user_from_session_token,
)
from app.services.architecture_generator import generate_target_architecture
from app.services.assessment_comparison import generate_assessment_comparison
from app.services.assessment_insights import build_assessment_insights
from app.services.aws_diagram_generator import generate_aws_diagram_png
from app.services.cloud_mapping import map_services
from app.services.enterprise_store import (
    add_evidence,
    initialize_enterprise_store,
    list_assessments,
    list_audit_events,
    list_evidence,
    save_assessment,
    save_cost_model,
    update_review_state,
    write_audit_event,
    get_assessment as load_assessment_record,
)
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
SAMPLE_DIAGRAM_DIR = BASE_DIR.parent / "samples" / "architecture_diagrams"
SAMPLE_METADATA_FILE = SAMPLE_DIAGRAM_DIR / "metadata.json"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    initialize_enterprise_store()
    yield


app = FastAPI(
    title="Cloud Migration Assessment Agent",
    version="0.1.0",
    description="Analyze cloud architecture diagrams and generate migration assessments.",
    lifespan=lifespan,
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


@app.middleware("http")
async def prevent_stale_static_assets(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@app.get("/", include_in_schema=False)
async def ui() -> RedirectResponse:
    return RedirectResponse(url="/static/index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/login", response_model=AuthSessionResponse)
async def login(request: AuthLoginRequest, response: Response) -> AuthSessionResponse:
    return _create_session_response(request, response)


@app.post("/api/session", response_model=None)
async def create_session_or_command(
    request: dict,
    response: Response,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> object:
    action = str(request.get("action") or "login").strip().lower()
    if action in {"assessment", "analyze", "run_assessment"}:
        user = _user_from_optional_session(session_token)
        _ensure_permission(user, "can_assess")
        payload = AnalyzeMigrationJsonRequest.model_validate(request)
        result = await _run_assessment_from_json_payload(payload)
        write_audit_event(
            user=user,
            action="assessment.generated",
            details={
                "filename": payload.filename,
                "source_provider": result.source_architecture.provider,
                "target_provider": result.target_architecture.provider,
                "mappings": len(result.service_mappings),
                "verdict": result.final_verdict.recommendation,
            },
        )
        return result
    if action in {"rebuild", "rebuild_assessment"}:
        user = _user_from_optional_session(session_token)
        _ensure_permission(user, "can_assess")
        payload = RebuildAssessmentRequest.model_validate(request)
        result = _rebuild_assessment_result(payload)
        write_audit_event(
            user=user,
            action="assessment.rebuilt",
            details={
                "source_provider": result.source_architecture.provider,
                "target_provider": result.target_architecture.provider,
                "mappings": len(result.service_mappings),
                "verdict": result.final_verdict.recommendation,
            },
        )
        return result
    if action in {"diagram_png", "download_diagram"}:
        user = _user_from_optional_session(session_token)
        _ensure_permission(user, "can_view")
        payload = DiagramImageRequest.model_validate(request)
        return _diagram_png_response(payload)
    if action in {"report_pdf", "download_pdf"}:
        user = _user_from_optional_session(session_token)
        _ensure_permission(user, "can_view")
        payload = PdfReportRequest.model_validate(request)
        return await _pdf_report_response(payload)
    if action in {"agent_ask", "ask_agent"}:
        user = _user_from_optional_session(session_token)
        _ensure_permission(user, "can_view")
        payload = MigrationAgentChatRequest.model_validate(request)
        return await _agent_chat_response(payload)
    if action in {"compare_assessments", "assessment_compare"}:
        user = _user_from_optional_session(session_token)
        _ensure_permission(user, "can_view")
        payload = AssessmentComparisonRequest.model_validate(request)
        result = await _assessment_compare_response(payload)
        write_audit_event(
            user=user,
            action="assessment.compared",
            details={
                "baseline_title": payload.baseline.title,
                "current_title": payload.current.title,
                "source": result.source,
                "readiness_delta": result.readiness_delta,
            },
        )
        return result
    if action in {"save_assessment", "persist_assessment"}:
        user = _user_from_optional_session(session_token)
        _ensure_permission(user, "can_review")
        payload = PersistAssessmentRequest.model_validate(request)
        return save_assessment(payload, user=user, assessment_id=request.get("assessment_id"))
    if action in {"save_cost_model", "cost_model"}:
        user = _user_from_optional_session(session_token)
        _ensure_permission(user, "can_review")
        assessment_id = str(request.get("assessment_id") or "").strip()
        if not assessment_id:
            raise HTTPException(status_code=400, detail="assessment_id is required.")
        payload = CostModelInput.model_validate(request.get("cost_model") or request)
        try:
            return save_cost_model(assessment_id, payload, user=user)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Assessment not found.") from exc
    if action in {"add_evidence", "evidence"}:
        user = _user_from_optional_session(session_token)
        _ensure_permission(user, "can_review")
        assessment_id = str(request.get("assessment_id") or "").strip()
        if not assessment_id:
            raise HTTPException(status_code=400, detail="assessment_id is required.")
        payload = EvidenceCreateRequest.model_validate(request.get("evidence") or request)
        try:
            return add_evidence(assessment_id, payload, user=user)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Assessment not found.") from exc

    login_request = AuthLoginRequest.model_validate(request)
    return _create_session_response(login_request, response)


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


@app.get("/api/sso/readiness", response_model=SsoReadinessResponse)
async def sso_readiness() -> SsoReadinessResponse:
    settings = get_settings()
    return SsoReadinessResponse(
        enabled=settings.sso_enabled,
        provider=settings.sso_provider,
        redirect_uri=settings.sso_redirect_uri,
        required_environment=[
            "SSO_ENABLED=true",
            "SSO_PROVIDER=microsoft_entra_id",
            "SSO_TENANT_ID=<tenant-id>",
            "SSO_CLIENT_ID=<app-registration-client-id>",
            "SSO_CLIENT_SECRET=<client-secret>",
            "SSO_REDIRECT_URI=<public-url>/auth/sso/callback",
        ],
        notes=[
            "Create an app registration in Microsoft Entra ID.",
            "Add the redirect URI shown here as a Web redirect URI.",
            "Add a client secret and store it as an environment variable.",
            "Map group or email claims to CloudBridge IQ roles.",
            "Keep local signed-cookie auth enabled as a break-glass fallback until SSO is verified.",
        ],
    )


@app.get("/api/demo-samples", response_model=list[DemoSampleMetadata])
async def demo_samples() -> list[DemoSampleMetadata]:
    return _load_demo_samples()


@app.get("/api/demo-samples/{sample_id}/image")
async def demo_sample_image(sample_id: str) -> FileResponse:
    sample = _demo_sample_by_id(sample_id)
    image_path = _demo_sample_image_path(sample)
    return FileResponse(
        image_path,
        media_type="image/png",
        filename=sample.filename,
    )


@app.post("/api/assessments", response_model=PersistAssessmentResponse)
async def persist_assessment(
    request: PersistAssessmentRequest,
    user: AuthUser = Depends(require_permission("can_review")),
) -> PersistAssessmentResponse:
    return save_assessment(request, user=user)


@app.get("/api/assessments", response_model=list[AssessmentSummary])
async def saved_assessments(
    _user: AuthUser = Depends(require_permission("can_view")),
) -> list[AssessmentSummary]:
    return list_assessments()


@app.get("/api/assessments/{assessment_id}", response_model=AssessmentRecord)
async def saved_assessment(
    assessment_id: str,
    _user: AuthUser = Depends(require_permission("can_view")),
) -> AssessmentRecord:
    try:
        return load_assessment_record(assessment_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Assessment not found.") from exc


@app.post("/api/assessments/{assessment_id}/review", response_model=AssessmentRecord)
async def persist_review_state(
    assessment_id: str,
    request: ReviewStateUpdateRequest,
    user: AuthUser = Depends(require_permission("can_review")),
) -> AssessmentRecord:
    try:
        return update_review_state(assessment_id, request, user=user)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Assessment not found.") from exc


@app.post("/api/assessments/{assessment_id}/evidence", response_model=EvidenceRecord)
async def persist_evidence(
    assessment_id: str,
    request: EvidenceCreateRequest,
    user: AuthUser = Depends(require_permission("can_review")),
) -> EvidenceRecord:
    try:
        return add_evidence(assessment_id, request, user=user)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Assessment not found.") from exc


@app.get("/api/assessments/{assessment_id}/evidence", response_model=list[EvidenceRecord])
async def saved_evidence(
    assessment_id: str,
    _user: AuthUser = Depends(require_permission("can_view")),
) -> list[EvidenceRecord]:
    try:
        return list_evidence(assessment_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Assessment not found.") from exc


@app.post("/api/assessments/{assessment_id}/cost-model", response_model=CostModelResponse)
async def persist_cost_model(
    assessment_id: str,
    request: CostModelInput,
    user: AuthUser = Depends(require_permission("can_review")),
) -> CostModelResponse:
    try:
        return save_cost_model(assessment_id, request, user=user)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Assessment not found.") from exc


@app.get("/api/assessments/{assessment_id}/audit", response_model=list[AuditEventRecord])
async def saved_audit_events(
    assessment_id: str,
    _user: AuthUser = Depends(require_permission("can_view")),
) -> list[AuditEventRecord]:
    return list_audit_events(assessment_id)


@app.get("/api/audit", response_model=list[AuditEventRecord])
async def enterprise_audit_events(
    _user: AuthUser = Depends(require_permission("can_admin")),
) -> list[AuditEventRecord]:
    return list_audit_events()


@app.post("/api/assessment", response_model=AnalyzeMigrationResponse)
@app.post("/analyze-migration", response_model=AnalyzeMigrationResponse)
async def analyze_migration(
    file: Annotated[UploadFile, File(description="Architecture diagram image or PDF")],
    source_provider: Annotated[str, Form()] = "auto",
    target_provider: Annotated[str, Form()] = "aws",
    migration_intent: Annotated[str | None, Form()] = None,
    goals: Annotated[str | None, Form()] = None,
    _user: AuthUser = Depends(require_permission("can_assess")),
) -> AnalyzeMigrationResponse:
    file_bytes = await file.read()
    return await _run_assessment_from_upload(
        file_bytes=file_bytes,
        filename=file.filename or "architecture-diagram",
        content_type=file.content_type,
        source_provider=source_provider,
        target_provider=target_provider,
        migration_intent=migration_intent,
        goals=goals,
    )


@app.post("/api/assessment-json", response_model=AnalyzeMigrationResponse)
async def analyze_migration_json(
    request: AnalyzeMigrationJsonRequest,
    _user: AuthUser = Depends(require_permission("can_assess")),
) -> AnalyzeMigrationResponse:
    return await _run_assessment_from_json_payload(request)


async def _run_assessment_from_json_payload(
    request: AnalyzeMigrationJsonRequest,
) -> AnalyzeMigrationResponse:
    try:
        encoded = request.file_base64.split(",", 1)[1] if "," in request.file_base64 else request.file_base64
        file_bytes = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Uploaded file payload is not valid base64.") from exc

    return await _run_assessment_from_upload(
        file_bytes=file_bytes,
        filename=request.filename,
        content_type=request.content_type,
        source_provider=request.source_provider,
        target_provider=request.target_provider,
        migration_intent=request.migration_intent,
        goals=request.goals,
    )


def _user_from_optional_session(session_token: str | None) -> AuthUser:
    if not session_token:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return user_from_session_token(session_token)


def _ensure_permission(user: AuthUser, permission: str) -> None:
    if not user.permissions.get(permission, False):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to perform this action.",
        )


def _load_demo_samples() -> list[DemoSampleMetadata]:
    try:
        raw_samples = json.loads(SAMPLE_METADATA_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Demo sample metadata was not found.") from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Demo sample metadata is invalid JSON.") from exc

    if not isinstance(raw_samples, list):
        raise HTTPException(status_code=500, detail="Demo sample metadata must be a list.")

    samples: list[DemoSampleMetadata] = []
    for raw_sample in raw_samples:
        sample = DemoSampleMetadata.model_validate(raw_sample)
        image_path = _demo_sample_image_path(sample)
        samples.append(
            sample.model_copy(
                update={"image_url": f"/api/demo-samples/{sample.id}/image"},
            ),
        )
        if not image_path.is_file():
            raise HTTPException(status_code=500, detail=f"Demo sample image is missing: {sample.filename}")
    return samples


def _demo_sample_by_id(sample_id: str) -> DemoSampleMetadata:
    for sample in _load_demo_samples():
        if sample.id == sample_id:
            return sample
    raise HTTPException(status_code=404, detail="Demo sample was not found.")


def _demo_sample_image_path(sample: DemoSampleMetadata) -> Path:
    image_path = (SAMPLE_DIAGRAM_DIR / sample.filename).resolve()
    sample_dir = SAMPLE_DIAGRAM_DIR.resolve()
    if sample_dir not in image_path.parents or image_path.suffix.lower() != ".png":
        raise HTTPException(status_code=400, detail="Demo sample filename is invalid.")
    return image_path


async def _run_assessment_from_upload(
    *,
    file_bytes: bytes,
    filename: str,
    content_type: str | None,
    source_provider: str,
    target_provider: str,
    migration_intent: str | None,
    goals: str | None,
) -> AnalyzeMigrationResponse:
    settings = get_settings()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(file_bytes) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Uploaded file exceeds size limit.")

    try:
        report = await run_migration_assessment(
            file_bytes=file_bytes,
            filename=filename or "architecture-diagram",
            content_type=content_type,
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


@app.post("/api/assessment/rebuild", response_model=AnalyzeMigrationResponse)
@app.post("/rebuild-assessment", response_model=AnalyzeMigrationResponse)
async def rebuild_assessment(
    request: RebuildAssessmentRequest,
    _user: AuthUser = Depends(require_permission("can_assess")),
) -> AnalyzeMigrationResponse:
    """Rebuild mappings, target architecture, report, and insights after user edits."""

    return _rebuild_assessment_result(request)


def _rebuild_assessment_result(request: RebuildAssessmentRequest) -> AnalyzeMigrationResponse:
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


@app.post("/api/report/pdf")
@app.post("/download-report-pdf")
async def download_report_pdf(
    request: PdfReportRequest,
    _user: AuthUser = Depends(require_permission("can_view")),
) -> Response:
    return await _pdf_report_response(request)


async def _pdf_report_response(request: PdfReportRequest) -> Response:
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
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed while formatting the assessment report: {exc}",
        ) from exc

    filename = _safe_pdf_filename(request.filename)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/diagram/png")
@app.post("/download-aws-diagram")
async def download_aws_diagram(
    request: DiagramImageRequest,
    _user: AuthUser = Depends(require_permission("can_view")),
) -> Response:
    return _diagram_png_response(request)


def _diagram_png_response(request: DiagramImageRequest) -> Response:
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


@app.post("/api/agent/ask", response_model=MigrationAgentChatResponse)
@app.post("/ask-migration-agent", response_model=MigrationAgentChatResponse)
async def ask_migration_agent(
    request: MigrationAgentChatRequest,
    _user: AuthUser = Depends(require_permission("can_view")),
) -> MigrationAgentChatResponse:
    return await _agent_chat_response(request)


async def _agent_chat_response(request: MigrationAgentChatRequest) -> MigrationAgentChatResponse:
    try:
        return await answer_migration_question(request)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Migration agent chat failed: {exc}",
        ) from exc


@app.post("/api/assessments/compare", response_model=AssessmentComparisonResponse)
async def compare_assessments(
    request: AssessmentComparisonRequest,
    user: AuthUser = Depends(require_permission("can_view")),
) -> AssessmentComparisonResponse:
    result = await _assessment_compare_response(request)
    write_audit_event(
        user=user,
        action="assessment.compared",
        details={
            "baseline_title": request.baseline.title,
            "current_title": request.current.title,
            "source": result.source,
            "readiness_delta": result.readiness_delta,
        },
    )
    return result


async def _assessment_compare_response(
    request: AssessmentComparisonRequest,
) -> AssessmentComparisonResponse:
    try:
        return await generate_assessment_comparison(request)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Assessment comparison failed: {exc}",
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
