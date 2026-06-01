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
