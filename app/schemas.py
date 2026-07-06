from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class ArchitectureComponent(BaseModel):
    id: str
    name: str
    provider: Optional[str] = None
    service_type: Optional[str] = None
    category: Optional[str] = None
    confidence: float = Field(ge=0, le=1)
    description: Optional[str] = None


class ArchitectureRelationship(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str
    description: Optional[str] = None


class SourceArchitecture(BaseModel):
    provider: str
    summary: str
    components: list[ArchitectureComponent]
    relationships: list[ArchitectureRelationship]
    assumptions: list[str] = []
    missing_information: list[str] = []


class ServiceMapping(BaseModel):
    source_service: str
    target_service: str
    target_provider: str = "aws"
    reasoning: str
    confidence: float = Field(ge=0, le=1)
    alternatives: list[str] = []


class TargetArchitecture(BaseModel):
    provider: str = "aws"
    summary: str
    components: list[ArchitectureComponent]
    relationships: list[ArchitectureRelationship]
    design_notes: list[str] = []


class MigrationRisk(BaseModel):
    title: str
    severity: Literal["low", "medium", "high", "critical"]
    description: str
    mitigation: str


class MigrationPhase(BaseModel):
    phase: str
    goals: list[str]
    activities: list[str]
    deliverables: list[str]
    risks: list[str]
    success_criteria: list[str]


class FinalVerdict(BaseModel):
    recommendation: Literal[
        "recommended",
        "conditionally_recommended",
        "not_recommended",
    ]
    reasoning: str
    confidence: float = Field(ge=0, le=1)


class MigrationAssessmentReport(BaseModel):
    executive_summary: str
    source_architecture: SourceArchitecture
    service_mappings: list[ServiceMapping]
    required_changes: list[str]
    target_architecture: TargetArchitecture
    mermaid_diagram: str
    migration_strategy: list[MigrationPhase]
    benefits: list[str]
    drawbacks: list[str]
    risks: list[MigrationRisk]
    assumptions: list[str]
    final_verdict: FinalVerdict
    markdown_report: str
    analysis_metadata: dict[str, Any] = {}


class DiagramIngestionResult(BaseModel):
    filename: str
    content_type: str | None = None
    file_kind: Literal["image", "pdf", "unknown"]
    text: str = ""
    image_base64: str | None = None
    image_mime_type: str | None = None
    metadata: dict[str, Any] = {}


class AnalyzeMigrationResponse(BaseModel):
    markdown_report: str
    mermaid_diagram: str
    source_architecture: SourceArchitecture
    target_architecture: TargetArchitecture
    service_mappings: list[ServiceMapping]
    required_changes: list[str] = []
    migration_strategy: list[MigrationPhase] = []
    benefits: list[str] = []
    drawbacks: list[str] = []
    risks: list[MigrationRisk] = []
    assumptions: list[str] = []
    final_verdict: FinalVerdict
    analysis_metadata: dict[str, Any] = {}
    assessment_insights: dict[str, Any] = {}


class RebuildAssessmentRequest(BaseModel):
    source_architecture: SourceArchitecture
    source_provider: str = "auto"
    target_provider: str = "aws"
    migration_intent: str | None = None
    goals: list[str] = []
    architecture_variant: str = "balanced"


class AnalyzeMigrationJsonRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=240)
    content_type: str | None = None
    file_base64: str = Field(min_length=1)
    source_provider: str = "auto"
    target_provider: str = "aws"
    migration_intent: str | None = None
    goals: str | None = None


class PdfReportRequest(BaseModel):
    markdown_report: str = Field(min_length=1)
    filename: str = "migration-assessment.pdf"
    source_provider: str | None = None
    target_provider: str | None = None
    target_architecture: TargetArchitecture | None = None
    include_rendered_diagram: bool = True
    include_mermaid_diagram: bool = False
    mermaid_diagram_png_base64: str | None = None


class DiagramImageRequest(BaseModel):
    target_architecture: TargetArchitecture
    filename: str = "aws-architecture.png"


class DemoSampleMetadata(BaseModel):
    id: str = Field(min_length=1, max_length=120)
    filename: str = Field(min_length=1, max_length=240)
    title: str = Field(min_length=1, max_length=160)
    source_provider: Literal["aws", "azure", "gcp"]
    target_provider: Literal["aws", "azure", "gcp"]
    route_label: str = Field(min_length=1, max_length=80)
    architecture_pattern: str = Field(min_length=1, max_length=120)
    architecture_variant: str = Field(default="balanced", max_length=120)
    pattern_label: str = Field(min_length=1, max_length=160)
    migration_intent: str = Field(min_length=1, max_length=500)
    goals: list[str] = []
    image_url: str | None = None


class MigrationChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class MigrationAgentChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    assessment: AnalyzeMigrationResponse | None = None
    chat_history: list[MigrationChatMessage] = []
    active_tab: str | None = None
    reviewer_notes: str | None = None


class MigrationAgentChatResponse(BaseModel):
    answer: str
    suggested_questions: list[str] = []
    used_assessment_context: bool = False
    model_used: str | None = None


class AssessmentComparisonItem(BaseModel):
    title: str = Field(default="Migration assessment", min_length=1, max_length=240)
    status: str | None = Field(default=None, max_length=120)
    reviewer: str | None = Field(default=None, max_length=160)
    updated_at: str | None = Field(default=None, max_length=80)
    assessment: AnalyzeMigrationResponse
    metadata: dict[str, Any] = {}


class AssessmentComparisonRequest(BaseModel):
    baseline: AssessmentComparisonItem
    current: AssessmentComparisonItem
    focus: str | None = Field(default=None, max_length=500)


class AssessmentComparisonDelta(BaseModel):
    area: str = Field(min_length=1, max_length=120)
    baseline: str = Field(min_length=1, max_length=500)
    current: str = Field(min_length=1, max_length=500)
    impact: str = Field(min_length=1, max_length=700)
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    owner: str = Field(default="Architecture review board", max_length=160)


class AssessmentComparisonResponse(BaseModel):
    executive_summary: str
    decision: str
    model_used: str | None = None
    generated_at: str
    source: Literal["llm", "offline", "llm_fallback"] = "offline"
    comparison_confidence: float = Field(default=0.7, ge=0, le=1)
    baseline_readiness: int = Field(default=0, ge=0, le=100)
    current_readiness: int = Field(default=0, ge=0, le=100)
    readiness_delta: int = Field(default=0, ge=-100, le=100)
    verdict_delta: str
    business_impact: list[str] = []
    architecture_deltas: list[AssessmentComparisonDelta] = []
    mapping_deltas: list[AssessmentComparisonDelta] = []
    risk_deltas: list[AssessmentComparisonDelta] = []
    governance_actions: list[str] = []
    recommended_next_steps: list[str] = []
    assumptions: list[str] = []


class PersistAssessmentRequest(BaseModel):
    title: str = Field(default="Migration assessment", min_length=1, max_length=240)
    project_name: str | None = Field(default=None, max_length=240)
    reviewer: str | None = Field(default=None, max_length=160)
    status: str = Field(default="needs_review", max_length=80)
    assessment: AnalyzeMigrationResponse
    review_state: dict[str, Any] = {}
    cost_model: dict[str, Any] | None = None


class PersistAssessmentResponse(BaseModel):
    assessment_id: str
    version: int
    saved_at: str


class AssessmentSummary(BaseModel):
    assessment_id: str
    title: str
    project_name: str | None = None
    source_provider: str | None = None
    target_provider: str | None = None
    status: str
    reviewer: str | None = None
    version: int
    created_by: str | None = None
    created_at: str
    updated_at: str


class AssessmentRecord(AssessmentSummary):
    assessment: AnalyzeMigrationResponse
    review_state: dict[str, Any] = {}
    cost_model: dict[str, Any] | None = None


class ReviewStateUpdateRequest(BaseModel):
    status: str = Field(default="needs_review", max_length=80)
    reviewer: str | None = Field(default=None, max_length=160)
    review_state: dict[str, Any] = {}


class EvidenceCreateRequest(BaseModel):
    gate_key: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=240)
    evidence_type: Literal[
        "note",
        "document",
        "link",
        "cost_model",
        "test_result",
        "runbook",
        "screenshot",
    ] = "note"
    content: str = Field(min_length=1, max_length=8000)
    file_name: str | None = Field(default=None, max_length=240)
    content_type: str | None = Field(default=None, max_length=120)


class EvidenceRecord(BaseModel):
    evidence_id: str
    assessment_id: str
    gate_key: str
    title: str
    evidence_type: str
    content: str
    file_name: str | None = None
    content_type: str | None = None
    uploaded_by: str | None = None
    created_at: str


class CostModelInput(BaseModel):
    source_monthly_baseline: float = Field(default=0, ge=0)
    compute_instances: int = Field(default=0, ge=0)
    avg_compute_monthly: float = Field(default=0, ge=0)
    storage_gb: float = Field(default=0, ge=0)
    storage_per_gb_month: float = Field(default=0.023, ge=0)
    requests_million: float = Field(default=0, ge=0)
    request_cost_per_million: float = Field(default=0.4, ge=0)
    data_transfer_gb: float = Field(default=0, ge=0)
    data_transfer_per_gb: float = Field(default=0.09, ge=0)
    database_monthly: float = Field(default=0, ge=0)
    licensing_monthly: float = Field(default=0, ge=0)
    support_monthly: float = Field(default=0, ge=0)
    observability_monthly: float = Field(default=0, ge=0)
    discount_percent: float = Field(default=0, ge=0, le=100)
    migration_months: int = Field(default=2, ge=0, le=36)
    notes: str | None = Field(default=None, max_length=2000)


class CostModelResponse(BaseModel):
    assessment_id: str
    input: CostModelInput
    monthly_target_estimate: float
    source_monthly_baseline: float
    estimated_monthly_savings: float
    estimated_annual_savings: float
    dual_run_reserve: float
    calculation_breakdown: dict[str, float]
    saved_at: str


class AuditEventRecord(BaseModel):
    audit_id: int
    assessment_id: str | None = None
    actor: str | None = None
    actor_role: str | None = None
    action: str
    details: dict[str, Any] = {}
    created_at: str


class SsoReadinessResponse(BaseModel):
    enabled: bool
    provider: str
    required_environment: list[str]
    redirect_uri: str
    notes: list[str]


UserRole = Literal["admin", "architect", "reviewer", "viewer"]


class AuthLoginRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    email: str | None = Field(default=None, max_length=180)
    requested_role: Literal["reviewer", "viewer"] = "reviewer"
    admin_password: str | None = Field(default=None, max_length=200)


class AuthUser(BaseModel):
    display_name: str
    email: str | None = None
    primary_role: UserRole
    roles: list[UserRole]
    permissions: dict[str, bool]


class AuthSessionResponse(BaseModel):
    user: AuthUser
