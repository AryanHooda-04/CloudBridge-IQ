"""SQLite persistence, audit, evidence, and cost model helpers.

The app deliberately uses SQLite here so the enterprise workflow can run on a
free Render instance or local laptop without operating a separate database.
The service boundary is narrow enough to swap this module for PostgreSQL or a
managed database later.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator

from app.config import Settings, get_settings
from app.schemas import (
    AssessmentRecord,
    AssessmentSummary,
    AuditEventRecord,
    AuthUser,
    CostModelInput,
    CostModelResponse,
    EvidenceCreateRequest,
    EvidenceRecord,
    PersistAssessmentRequest,
    PersistAssessmentResponse,
    ReviewStateUpdateRequest,
)


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def resolve_database_path(settings: Settings | None = None) -> Path:
    settings = settings or get_settings()
    configured = Path(settings.database_path)
    if configured.is_absolute():
        return configured
    return Path(__file__).resolve().parents[2] / configured


def initialize_enterprise_store(settings: Settings | None = None) -> None:
    path = resolve_database_path(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(settings) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS assessments (
                assessment_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                project_name TEXT,
                source_provider TEXT,
                target_provider TEXT,
                status TEXT NOT NULL,
                reviewer TEXT,
                version INTEGER NOT NULL,
                created_by TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                assessment_json TEXT NOT NULL,
                review_json TEXT NOT NULL,
                cost_model_json TEXT
            );

            CREATE TABLE IF NOT EXISTS audit_events (
                audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id TEXT,
                actor TEXT,
                actor_role TEXT,
                action TEXT NOT NULL,
                details_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS evidence_items (
                evidence_id TEXT PRIMARY KEY,
                assessment_id TEXT NOT NULL,
                gate_key TEXT NOT NULL,
                title TEXT NOT NULL,
                evidence_type TEXT NOT NULL,
                content TEXT NOT NULL,
                file_name TEXT,
                content_type TEXT,
                uploaded_by TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id)
            );

            CREATE TABLE IF NOT EXISTS cost_models (
                assessment_id TEXT PRIMARY KEY,
                input_json TEXT NOT NULL,
                result_json TEXT NOT NULL,
                updated_by TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id)
            );

            CREATE INDEX IF NOT EXISTS idx_audit_assessment ON audit_events(assessment_id);
            CREATE INDEX IF NOT EXISTS idx_evidence_assessment ON evidence_items(assessment_id);
            CREATE INDEX IF NOT EXISTS idx_assessments_updated ON assessments(updated_at);
            """
        )


def save_assessment(
    request: PersistAssessmentRequest,
    *,
    user: AuthUser,
    assessment_id: str | None = None,
    settings: Settings | None = None,
) -> PersistAssessmentResponse:
    initialize_enterprise_store(settings)
    now = utc_now()
    actor = _actor(user)
    payload = request.assessment.model_dump(mode="json")
    source_provider = request.assessment.source_architecture.provider
    target_provider = request.assessment.target_architecture.provider
    record_id = assessment_id or str(uuid.uuid4())

    with _connect(settings) as conn:
        existing = conn.execute(
            "SELECT version, created_at, created_by FROM assessments WHERE assessment_id = ?",
            (record_id,),
        ).fetchone()
        if existing:
            version = int(existing["version"]) + 1
            created_at = str(existing["created_at"])
            created_by = str(existing["created_by"] or actor)
        else:
            version = 1
            created_at = now
            created_by = actor

        conn.execute(
            """
            INSERT INTO assessments (
                assessment_id, title, project_name, source_provider, target_provider,
                status, reviewer, version, created_by, created_at, updated_at,
                assessment_json, review_json, cost_model_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(assessment_id) DO UPDATE SET
                title = excluded.title,
                project_name = excluded.project_name,
                source_provider = excluded.source_provider,
                target_provider = excluded.target_provider,
                status = excluded.status,
                reviewer = excluded.reviewer,
                version = excluded.version,
                updated_at = excluded.updated_at,
                assessment_json = excluded.assessment_json,
                review_json = excluded.review_json,
                cost_model_json = excluded.cost_model_json
            """,
            (
                record_id,
                request.title,
                request.project_name or request.title,
                source_provider,
                target_provider,
                request.status,
                request.reviewer,
                version,
                created_by,
                created_at,
                now,
                _json(payload),
                _json(request.review_state),
                _json(request.cost_model) if request.cost_model is not None else None,
            ),
        )
        _write_audit(
            conn,
            assessment_id=record_id,
            user=user,
            action="assessment.saved",
            details={
                "title": request.title,
                "status": request.status,
                "version": version,
                "source_provider": source_provider,
                "target_provider": target_provider,
            },
        )

    return PersistAssessmentResponse(assessment_id=record_id, version=version, saved_at=now)


def list_assessments(
    *,
    limit: int = 25,
    settings: Settings | None = None,
) -> list[AssessmentSummary]:
    initialize_enterprise_store(settings)
    with _connect(settings) as conn:
        rows = conn.execute(
            """
            SELECT assessment_id, title, project_name, source_provider, target_provider,
                   status, reviewer, version, created_by, created_at, updated_at
            FROM assessments
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (max(1, min(limit, 100)),),
        ).fetchall()
    return [_summary_from_row(row) for row in rows]


def get_assessment(
    assessment_id: str,
    *,
    settings: Settings | None = None,
) -> AssessmentRecord:
    initialize_enterprise_store(settings)
    with _connect(settings) as conn:
        row = conn.execute(
            "SELECT * FROM assessments WHERE assessment_id = ?",
            (assessment_id,),
        ).fetchone()
    if row is None:
        raise KeyError(assessment_id)
    data = _summary_from_row(row).model_dump()
    data.update(
        {
            "assessment": _loads(row["assessment_json"]),
            "review_state": _loads(row["review_json"]),
            "cost_model": _loads(row["cost_model_json"]) if row["cost_model_json"] else None,
        }
    )
    return AssessmentRecord.model_validate(data)


def update_review_state(
    assessment_id: str,
    request: ReviewStateUpdateRequest,
    *,
    user: AuthUser,
    settings: Settings | None = None,
) -> AssessmentRecord:
    initialize_enterprise_store(settings)
    now = utc_now()
    with _connect(settings) as conn:
        row = conn.execute(
            "SELECT review_json FROM assessments WHERE assessment_id = ?",
            (assessment_id,),
        ).fetchone()
        if row is None:
            raise KeyError(assessment_id)
        review_state = _loads(row["review_json"])
        review_state.update(request.review_state)
        conn.execute(
            """
            UPDATE assessments
            SET status = ?, reviewer = ?, review_json = ?, updated_at = ?
            WHERE assessment_id = ?
            """,
            (
                request.status,
                request.reviewer,
                _json(review_state),
                now,
                assessment_id,
            ),
        )
        _write_audit(
            conn,
            assessment_id=assessment_id,
            user=user,
            action="review.updated",
            details={"status": request.status, "reviewer": request.reviewer},
        )
    return get_assessment(assessment_id, settings=settings)


def add_evidence(
    assessment_id: str,
    request: EvidenceCreateRequest,
    *,
    user: AuthUser,
    settings: Settings | None = None,
) -> EvidenceRecord:
    initialize_enterprise_store(settings)
    evidence_id = str(uuid.uuid4())
    now = utc_now()
    with _connect(settings) as conn:
        _ensure_assessment_exists(conn, assessment_id)
        conn.execute(
            """
            INSERT INTO evidence_items (
                evidence_id, assessment_id, gate_key, title, evidence_type,
                content, file_name, content_type, uploaded_by, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evidence_id,
                assessment_id,
                request.gate_key,
                request.title,
                request.evidence_type,
                request.content,
                request.file_name,
                request.content_type,
                _actor(user),
                now,
            ),
        )
        _write_audit(
            conn,
            assessment_id=assessment_id,
            user=user,
            action="evidence.added",
            details={
                "gate_key": request.gate_key,
                "title": request.title,
                "evidence_type": request.evidence_type,
            },
        )
    return EvidenceRecord(
        evidence_id=evidence_id,
        assessment_id=assessment_id,
        gate_key=request.gate_key,
        title=request.title,
        evidence_type=request.evidence_type,
        content=request.content,
        file_name=request.file_name,
        content_type=request.content_type,
        uploaded_by=_actor(user),
        created_at=now,
    )


def list_evidence(
    assessment_id: str,
    *,
    settings: Settings | None = None,
) -> list[EvidenceRecord]:
    initialize_enterprise_store(settings)
    with _connect(settings) as conn:
        _ensure_assessment_exists(conn, assessment_id)
        rows = conn.execute(
            """
            SELECT evidence_id, assessment_id, gate_key, title, evidence_type,
                   content, file_name, content_type, uploaded_by, created_at
            FROM evidence_items
            WHERE assessment_id = ?
            ORDER BY created_at DESC
            """,
            (assessment_id,),
        ).fetchall()
    return [EvidenceRecord.model_validate(dict(row)) for row in rows]


def save_cost_model(
    assessment_id: str,
    cost_input: CostModelInput,
    *,
    user: AuthUser,
    settings: Settings | None = None,
) -> CostModelResponse:
    initialize_enterprise_store(settings)
    result = calculate_cost_model(assessment_id, cost_input)
    now = result.saved_at
    with _connect(settings) as conn:
        _ensure_assessment_exists(conn, assessment_id)
        conn.execute(
            """
            INSERT INTO cost_models (assessment_id, input_json, result_json, updated_by, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(assessment_id) DO UPDATE SET
                input_json = excluded.input_json,
                result_json = excluded.result_json,
                updated_by = excluded.updated_by,
                updated_at = excluded.updated_at
            """,
            (
                assessment_id,
                cost_input.model_dump_json(),
                result.model_dump_json(),
                _actor(user),
                now,
            ),
        )
        conn.execute(
            "UPDATE assessments SET cost_model_json = ?, updated_at = ? WHERE assessment_id = ?",
            (result.model_dump_json(), now, assessment_id),
        )
        _write_audit(
            conn,
            assessment_id=assessment_id,
            user=user,
            action="cost_model.saved",
            details={
                "monthly_target_estimate": result.monthly_target_estimate,
                "estimated_monthly_savings": result.estimated_monthly_savings,
            },
        )
    return result


def calculate_cost_model(assessment_id: str, cost_input: CostModelInput) -> CostModelResponse:
    compute = cost_input.compute_instances * cost_input.avg_compute_monthly
    storage = cost_input.storage_gb * cost_input.storage_per_gb_month
    requests = cost_input.requests_million * cost_input.request_cost_per_million
    transfer = cost_input.data_transfer_gb * cost_input.data_transfer_per_gb
    subtotal = (
        compute
        + storage
        + requests
        + transfer
        + cost_input.database_monthly
        + cost_input.licensing_monthly
        + cost_input.support_monthly
        + cost_input.observability_monthly
    )
    discount = subtotal * (cost_input.discount_percent / 100)
    target = max(0.0, subtotal - discount)
    savings = max(0.0, cost_input.source_monthly_baseline - target)
    dual_run = (cost_input.source_monthly_baseline + target) * max(cost_input.migration_months, 0)
    return CostModelResponse(
        assessment_id=assessment_id,
        input=cost_input,
        monthly_target_estimate=round(target, 2),
        source_monthly_baseline=round(cost_input.source_monthly_baseline, 2),
        estimated_monthly_savings=round(savings, 2),
        estimated_annual_savings=round(savings * 12, 2),
        dual_run_reserve=round(dual_run, 2),
        calculation_breakdown={
            "compute": round(compute, 2),
            "storage": round(storage, 2),
            "requests": round(requests, 2),
            "data_transfer": round(transfer, 2),
            "database": round(cost_input.database_monthly, 2),
            "licensing": round(cost_input.licensing_monthly, 2),
            "support": round(cost_input.support_monthly, 2),
            "observability": round(cost_input.observability_monthly, 2),
            "discount": round(discount, 2),
        },
        saved_at=utc_now(),
    )


def list_audit_events(
    assessment_id: str | None = None,
    *,
    limit: int = 100,
    settings: Settings | None = None,
) -> list[AuditEventRecord]:
    initialize_enterprise_store(settings)
    params: tuple[Any, ...]
    where = ""
    if assessment_id:
        where = "WHERE assessment_id = ?"
        params = (assessment_id, max(1, min(limit, 250)))
    else:
        params = (max(1, min(limit, 250)),)
    with _connect(settings) as conn:
        rows = conn.execute(
            f"""
            SELECT audit_id, assessment_id, actor, actor_role, action, details_json, created_at
            FROM audit_events
            {where}
            ORDER BY audit_id DESC
            LIMIT ?
            """,
            params,
        ).fetchall()
    return [
        AuditEventRecord(
            audit_id=int(row["audit_id"]),
            assessment_id=row["assessment_id"],
            actor=row["actor"],
            actor_role=row["actor_role"],
            action=row["action"],
            details=_loads(row["details_json"]),
            created_at=row["created_at"],
        )
        for row in rows
    ]


def write_audit_event(
    *,
    user: AuthUser | None,
    action: str,
    assessment_id: str | None = None,
    details: dict[str, Any] | None = None,
    settings: Settings | None = None,
) -> None:
    initialize_enterprise_store(settings)
    with _connect(settings) as conn:
        _write_audit(
            conn,
            assessment_id=assessment_id,
            user=user,
            action=action,
            details=details or {},
        )


@contextmanager
def _connect(settings: Settings | None = None) -> Iterator[sqlite3.Connection]:
    path = resolve_database_path(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _summary_from_row(row: sqlite3.Row) -> AssessmentSummary:
    return AssessmentSummary(
        assessment_id=row["assessment_id"],
        title=row["title"],
        project_name=row["project_name"],
        source_provider=row["source_provider"],
        target_provider=row["target_provider"],
        status=row["status"],
        reviewer=row["reviewer"],
        version=int(row["version"]),
        created_by=row["created_by"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _ensure_assessment_exists(conn: sqlite3.Connection, assessment_id: str) -> None:
    exists = conn.execute(
        "SELECT 1 FROM assessments WHERE assessment_id = ?",
        (assessment_id,),
    ).fetchone()
    if exists is None:
        raise KeyError(assessment_id)


def _write_audit(
    conn: sqlite3.Connection,
    *,
    assessment_id: str | None,
    user: AuthUser | None,
    action: str,
    details: dict[str, Any],
) -> None:
    conn.execute(
        """
        INSERT INTO audit_events (assessment_id, actor, actor_role, action, details_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            assessment_id,
            _actor(user) if user else None,
            user.primary_role if user else None,
            action,
            _json(details),
            utc_now(),
        ),
    )


def _actor(user: AuthUser) -> str:
    return user.email or user.display_name


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _loads(value: str | None) -> Any:
    if not value:
        return {}
    return json.loads(value)
