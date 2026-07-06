import asyncio

from app.config import Settings
from app.schemas import (
    AnalyzeMigrationResponse,
    ArchitectureComponent,
    AssessmentComparisonItem,
    AssessmentComparisonRequest,
    FinalVerdict,
    MigrationRisk,
    ServiceMapping,
    SourceArchitecture,
    TargetArchitecture,
)
from app.services.assessment_comparison import _parse_llm_response, generate_assessment_comparison


def _assessment(*, target_provider: str, readiness: int, risk_title: str) -> AnalyzeMigrationResponse:
    return AnalyzeMigrationResponse(
        markdown_report="# Report",
        mermaid_diagram="graph TD\nA-->B",
        source_architecture=SourceArchitecture(
            provider="aws",
            summary="AWS source architecture.",
            components=[
                ArchitectureComponent(
                    id="api",
                    name="API service",
                    provider="aws",
                    category="compute",
                    confidence=0.86,
                )
            ],
            relationships=[],
        ),
        target_architecture=TargetArchitecture(
            provider=target_provider,
            summary=f"{target_provider} target architecture.",
            components=[
                ArchitectureComponent(
                    id="target_api",
                    name="Managed API",
                    provider=target_provider,
                    category="compute",
                    confidence=0.84,
                )
            ],
            relationships=[],
        ),
        service_mappings=[
            ServiceMapping(
                source_service="API service",
                target_service="Managed API",
                target_provider=target_provider,
                reasoning="Managed target runtime.",
                confidence=0.8,
            )
        ],
        risks=[
            MigrationRisk(
                title=risk_title,
                severity="high",
                description="Needs validation.",
                mitigation="Attach migration evidence.",
            )
        ],
        final_verdict=FinalVerdict(
            recommendation="conditionally_recommended",
            reasoning="Proceed after review.",
            confidence=0.76,
        ),
        assessment_insights={
            "scores": {
                "overall_readiness": {
                    "value": readiness,
                }
            }
        },
    )


def test_assessment_comparison_falls_back_without_llm_key(monkeypatch):
    monkeypatch.setattr(
        "app.services.assessment_comparison.get_settings",
        lambda: Settings(openai_api_key=None),
    )
    request = AssessmentComparisonRequest(
        baseline=AssessmentComparisonItem(
            title="Baseline AWS to Azure",
            assessment=_assessment(target_provider="azure", readiness=52, risk_title="Data cutover"),
        ),
        current=AssessmentComparisonItem(
            title="Current AWS to GCP",
            assessment=_assessment(target_provider="gcp", readiness=68, risk_title="IAM redesign"),
        ),
    )

    comparison = asyncio.run(generate_assessment_comparison(request))

    assert comparison.source == "offline"
    assert comparison.baseline_readiness == 52
    assert comparison.current_readiness == 68
    assert comparison.readiness_delta == 16
    assert comparison.architecture_deltas
    assert comparison.risk_deltas
    assert comparison.governance_actions


def test_assessment_comparison_timeout_fallback_keeps_model_reachable_label(monkeypatch):
    class SlowComparisonModel:
        async def ainvoke(self, _messages):
            raise asyncio.TimeoutError()

    monkeypatch.setattr(
        "app.services.assessment_comparison.get_settings",
        lambda: Settings(openai_api_key="test-key", model_name="gpt-5.2"),
    )
    monkeypatch.setattr(
        "app.services.assessment_comparison.build_chat_openai",
        lambda **_kwargs: SlowComparisonModel(),
    )
    request = AssessmentComparisonRequest(
        baseline=AssessmentComparisonItem(
            title="Baseline AWS to Azure",
            assessment=_assessment(target_provider="azure", readiness=52, risk_title="Data cutover"),
        ),
        current=AssessmentComparisonItem(
            title="Current AWS to GCP",
            assessment=_assessment(target_provider="gcp", readiness=68, risk_title="IAM redesign"),
        ),
    )

    comparison = asyncio.run(generate_assessment_comparison(request))

    assert comparison.source == "llm_fallback"
    assert comparison.model_used == "gpt-5.2 fallback (timeout)"
    assert "unavailable" not in comparison.model_used.lower()
    assert comparison.baseline_readiness == 52
    assert comparison.current_readiness == 68


def test_assessment_comparison_parser_accepts_fenced_json_with_trailing_commas():
    comparison = _parse_llm_response(
        """```json
        {
          "executive_summary": "The current run improves the target operating model.",
          "decision": "Merge useful deltas and continue architecture review.",
          "comparison_confidence": 0.82,
          "verdict_delta": "Verdict is unchanged.",
          "business_impact": ["Improves review readiness",],
          "governance_actions": ["Validate cost model",],
          "recommended_next_steps": ["Approve after evidence review",],
        }
        ```"""
    )

    assert comparison.source == "llm"
    assert comparison.comparison_confidence == 0.82
    assert comparison.business_impact == ["Improves review readiness"]
    assert comparison.governance_actions == ["Validate cost model"]


def test_assessment_comparison_parser_accepts_openai_content_blocks():
    comparison = _parse_llm_response(
        [
            {
                "type": "text",
                "text": '{"executive_summary":"Current design is directionally stronger.",'
                '"decision":"Promote current with review gates.",'
                '"comparison_confidence":0.74,'
                '"verdict_delta":"Verdict improved.",'
                '"business_impact":["Better modernization path"]}',
            }
        ]
    )

    assert comparison.source == "llm"
    assert comparison.decision == "Promote current with review gates."
    assert comparison.business_impact == ["Better modernization path"]
