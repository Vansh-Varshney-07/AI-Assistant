"""
wayfinder/workers/W09_source_verifier/tests.py
----------------------------------------------
Offline contract tests for W09 Source Verifier.
"""
import pytest
from wayfinder.workers.schemas import (
    VerificationResult, EvidenceVerdict, EvidenceItem
)


def make_verification(**overrides) -> VerificationResult:
    defaults = dict(
        verification_id="test-w09-001",
        claim="asyncio is built into Python 3.4+",
        cited_url="https://docs.python.org/3/library/asyncio.html",
        verdict=EvidenceVerdict.SUPPORTED,
        evidence=[
            EvidenceItem(
                source_url="https://docs.python.org/3/library/asyncio.html",
                excerpt="asyncio was introduced in Python 3.4 as a provisional module.",
                supports_claim=True,
                freshness_date="2024-01-01",
            )
        ],
        confidence=0.94,
        reasoning="The Python official documentation explicitly states asyncio was introduced in 3.4.",
    )
    defaults.update(overrides)
    return VerificationResult(**defaults)


class TestVerificationResultSchema:
    def test_supported_verdict_passes(self):
        result = make_verification()
        assert result.validate() == []

    def test_unverified_with_evidence_fails(self):
        result = make_verification(
            verdict=EvidenceVerdict.UNVERIFIED,
            evidence=[EvidenceItem(
                source_url="https://example.com",
                excerpt="Some text",
                supports_claim=True,
            )],
        )
        errors = result.validate()
        assert any("UNVERIFIED" in e for e in errors)

    def test_unverified_without_evidence_passes(self):
        result = make_verification(
            verdict=EvidenceVerdict.UNVERIFIED,
            evidence=[],
            confidence=0.1,
            reasoning="The cited URL returned 404 and no independent sources found.",
        )
        assert result.validate() == []

    def test_empty_reasoning_fails(self):
        result = make_verification(reasoning="")
        errors = result.validate()
        assert any("reasoning" in e for e in errors)

    def test_confidence_out_of_range(self):
        result = make_verification(confidence=1.2)
        errors = result.validate()
        assert any("confidence" in e for e in errors)

    def test_contradicted_verdict(self):
        result = make_verification(
            verdict=EvidenceVerdict.CONTRADICTED,
            evidence=[
                EvidenceItem(
                    source_url="https://independent-source.com",
                    excerpt="This claim is factually incorrect according to PEP 3156.",
                    supports_claim=False,
                    contradicts_claim=True,
                )
            ],
            confidence=0.82,
            reasoning="Independent sources directly contradict the claim.",
        )
        assert result.validate() == []
        assert result.evidence[0].contradicts_claim is True

    def test_partially_supported_verdict(self):
        result = make_verification(
            verdict=EvidenceVerdict.PARTIALLY_SUPPORTED,
            evidence=[
                EvidenceItem(
                    source_url="https://docs.python.org",
                    excerpt="asyncio was added in 3.4 as provisional.",
                    supports_claim=True,
                ),
                EvidenceItem(
                    source_url="https://other.com",
                    excerpt="Some nuance not covered by the claim.",
                    supports_claim=False,
                    contradicts_claim=False,
                ),
            ],
            confidence=0.65,
            reasoning="Partially supported: claim is correct but omits important nuance.",
        )
        assert result.validate() == []


class TestVerificationProcedure:
    """Tests to verify the procedure structure in the definition."""
    def test_definition_exists(self):
        from pathlib import Path
        assert Path("wayfinder/workers/W09_source_verifier/definition.yaml").exists()

    def test_tavily_extract_allowed(self):
        import yaml
        from pathlib import Path
        d = yaml.safe_load(
            Path("wayfinder/workers/W09_source_verifier/definition.yaml").read_text()
        )
        assert "tavily_extract" in d["capabilities"]

    def test_tavily_research_denied(self):
        import yaml
        from pathlib import Path
        d = yaml.safe_load(
            Path("wayfinder/workers/W09_source_verifier/definition.yaml").read_text()
        )
        denied = d.get("denied_capabilities", [])
        assert "tavily_research" in denied
