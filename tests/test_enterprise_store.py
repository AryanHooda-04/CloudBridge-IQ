import sqlite3

import pytest

from app.config import Settings
from app.schemas import (
    AnalyzeMigrationResponse,
    ArchitectureComponent,
    AuthLoginRequest,
    CostModelInput,
    EvidenceCreateRequest,
    FinalVerdict,
    PersistAssessmentRequest,
    ReviewStateUpdateRequest,
    SourceArchitecture,
    TargetArchitecture,
)
from app.services.auth import authenticate_user
from app.services.enterprise_store import (
    add_evidence,
    calculate_cost_model,
    delete_assessment,
    get_assessment,
    list_audit_events,
    save_assessment,
    save_cost_model,
    update_review_state,
)


def _settings(tmp_path):
    return Settings(database_path=str(tmp_path / "cloudbridge-test.sqlite3"))


def _user():
    return authenticate_user(
        request=AuthLoginRequest(display_name="Aryan", requested_role="reviewer"),
        settings=Settings(auth_admin_password=None),
    )


def _assessment():
    source = SourceArchitecture(
        provider="AWS",
        summary="AWS source",
        components=[
            ArchitectureComponent(
                id="s3",
                name="Amazon S3",
                provider="aws",
                category="storage",
                confidence=0.9,
            )
        ],
        relationships=[],
    )
    target = TargetArchitecture(
        provider="azure",
        summary="Azure target",
        components=[
            ArchitectureComponent(
                id="blob",
                name="Azure Blob Storage",
                provider="azure",
                category="storage",
                confidence=0.9,
            )
        ],
        relationships=[],
    )
    return AnalyzeMigrationResponse(
        markdown_report="# Report",
        mermaid_diagram="graph TD\ns3-->blob",
        source_architecture=source,
        target_architecture=target,
        service_mappings=[],
        final_verdict=FinalVerdict(
            recommendation="conditionally_recommended",
            reasoning="Needs review",
            confidence=0.78,
        ),
    )


def test_save_assessment_audit_evidence_and_review(tmp_path):
    settings = _settings(tmp_path)
    user = _user()
    saved = save_assessment(
        PersistAssessmentRequest(
            title="AWS to Azure",
            project_name="Migration",
            reviewer="Aryan",
            status="needs_review",
            assessment=_assessment(),
            review_state={"notes": "initial"},
        ),
        user=user,
        settings=settings,
    )

    record = get_assessment(saved.assessment_id, settings=settings)
    assert record.title == "AWS to Azure"
    assert record.version == 1

    updated = update_review_state(
        saved.assessment_id,
        ReviewStateUpdateRequest(status="reviewed", reviewer="Aryan", review_state={"notes": "done"}),
        user=user,
        settings=settings,
    )
    assert updated.status == "reviewed"
    assert updated.review_state["notes"] == "done"

    evidence = add_evidence(
        saved.assessment_id,
        EvidenceCreateRequest(
            gate_key="cost_model_prepared",
            title="Cost model",
            evidence_type="cost_model",
            content="Calculator attached.",
        ),
        user=user,
        settings=settings,
    )
    assert evidence.gate_key == "cost_model_prepared"

    events = list_audit_events(saved.assessment_id, settings=settings)
    assert [event.action for event in events][:3] == [
        "evidence.added",
        "review.updated",
        "assessment.saved",
    ]


def test_cost_model_calculation_and_save(tmp_path):
    settings = _settings(tmp_path)
    user = _user()
    saved = save_assessment(
        PersistAssessmentRequest(title="Cost test", assessment=_assessment()),
        user=user,
        settings=settings,
    )
    cost_input = CostModelInput(
        source_monthly_baseline=10000,
        compute_instances=4,
        avg_compute_monthly=500,
        storage_gb=1000,
        data_transfer_gb=100,
        database_monthly=1500,
        support_monthly=300,
        discount_percent=10,
        migration_months=2,
    )
    calculated = calculate_cost_model(saved.assessment_id, cost_input)
    assert calculated.monthly_target_estimate > 0
    assert calculated.estimated_monthly_savings > 0

    persisted = save_cost_model(saved.assessment_id, cost_input, user=user, settings=settings)
    assert persisted.dual_run_reserve > 0
    assert get_assessment(saved.assessment_id, settings=settings).cost_model is not None


def test_delete_assessment_removes_related_records_and_audits(tmp_path):
    settings = _settings(tmp_path)
    user = _user()
    saved = save_assessment(
        PersistAssessmentRequest(title="Delete me", assessment=_assessment()),
        user=user,
        settings=settings,
    )
    add_evidence(
        saved.assessment_id,
        EvidenceCreateRequest(
            gate_key="rollback_plan_documented",
            title="Rollback plan",
            evidence_type="runbook",
            content="Rollback steps attached.",
        ),
        user=user,
        settings=settings,
    )
    save_cost_model(
        saved.assessment_id,
        CostModelInput(source_monthly_baseline=5000, compute_instances=2, avg_compute_monthly=250),
        user=user,
        settings=settings,
    )

    delete_assessment(saved.assessment_id, user=user, settings=settings)

    with pytest.raises(KeyError):
        get_assessment(saved.assessment_id, settings=settings)

    with sqlite3.connect(settings.database_path) as conn:
        evidence_count = conn.execute(
            "SELECT COUNT(*) FROM evidence_items WHERE assessment_id = ?",
            (saved.assessment_id,),
        ).fetchone()[0]
        cost_count = conn.execute(
            "SELECT COUNT(*) FROM cost_models WHERE assessment_id = ?",
            (saved.assessment_id,),
        ).fetchone()[0]

    assert evidence_count == 0
    assert cost_count == 0
    assert list_audit_events(saved.assessment_id, settings=settings)[0].action == "assessment.deleted"
