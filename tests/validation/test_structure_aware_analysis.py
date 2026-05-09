"""
Validation tests for Phase 2 structure-aware analysis.
Tests section referencing, deduplication, and validation logic.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.agents.analyst import LegalRiskAnalyst
from app.agents.auditor import FinalAuditor
from app.services.document_parser import ParsedDocument, DocumentBlock
from app.services.document_structure import Section
from app.services.section_utils import (
    validate_section_references,
    get_related_sections,
    calculate_coverage_metrics
)
from app.services.analysis import _deduplicate_findings, _compare_risk_level


@pytest.fixture
def mock_parsed_document():
    """Create a mock parsed document with sections."""
    doc = MagicMock(spec=ParsedDocument)
    
    # Create mock sections
    sections = [
        Section(
            number="1",
            title="Definitions",
            page_num=1,
            level=1,
            clause_type="general",
            content="This section defines key terms used throughout the agreement."
        ),
        Section(
            number="3.2",
            title="Payment Terms",
            page_num=3,
            level=2,
            clause_type="payment",
            content="Client shall pay within sixty (60) days of receipt of invoice."
        ),
        Section(
            number="7.1",
            title="Indemnification",
            page_num=7,
            level=2,
            clause_type="liability",
            content="Client shall indemnify Provider from any and all claims."
        ),
        Section(
            number="9.2",
            title="Termination for Cause",
            page_num=9,
            level=2,
            clause_type="termination",
            content="Either party may terminate upon 30 days written notice."
        )
    ]
    
    doc.sections = sections
    doc.section_map = {
        "1": sections[0],
        "3.2": sections[1],
        "7.1": sections[2],
        "9.2": sections[3]
    }
    doc.structure = {
        "key_clauses": {
            "payment": ["3.2 Payment Terms (p.3)"],
            "liability": ["7.1 Indemnification (p.7)"],
            "termination": ["9.2 Termination for Cause (p.9)"]
        },
        "hierarchy": []
    }
    doc.page_count = 10
    doc.blocks = []
    
    return doc


@pytest.mark.asyncio
async def test_analyst_requires_section_references(mock_parsed_document):
    """Test that analyst generates findings with section references."""
    analyst = LegalRiskAnalyst()
    
    # Mock the LLM response
    mock_response = """{
        "findings": [
            {
                "section": "3.2",
                "page": 3,
                "title": "Payment Terms Issue",
                "risk": "High",
                "justification": "60-day payment term exceeds standard",
                "contract_text": "Client shall pay within sixty (60) days",
                "recommendation": "Reduce to 30 days",
                "priority": 1,
                "related_sections": ["7.1"],
                "clause_type": "payment"
            }
        ]
    }"""
    
    with patch('app.agents.analyst.generate', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        state = {
            "query": "Analyze contract",
            "original_query": "Full audit",
            "merged_context": "Sample contract text",
            "research_report": "Research findings",
            "parsed_document": mock_parsed_document
        }
        
        result = await analyst.run(state)
        
        # Verify findings have required fields
        assert "risk_analysis" in result
        assert "findings" in result["risk_analysis"]
        
        findings = result["risk_analysis"]["findings"]
        assert len(findings) > 0
        
        for finding in findings:
            assert "section" in finding, "Finding must have section reference"
            assert "page" in finding, "Finding must have page number"
            assert "title" in finding, "Finding must have title"
            assert "risk" in finding, "Finding must have risk level"
            assert "justification" in finding, "Finding must have justification"


@pytest.mark.asyncio
async def test_auditor_validates_section_references(mock_parsed_document):
    """Test that auditor validates section references."""
    auditor = FinalAuditor()
    
    # Mock LLM responses
    with patch('app.agents.auditor.generate', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = "Validation complete"
        
        state = {
            "query": "Analyze contract",
            "risk_analysis": {
                "findings": [
                    {
                        "section": "3.2",
                        "page": 3,
                        "title": "Valid Finding",
                        "risk": "High"
                    },
                    {
                        "section": "99.9",  # Invalid section
                        "page": 99,
                        "title": "Invalid Finding",
                        "risk": "Medium"
                    }
                ]
            },
            "parsed_document": mock_parsed_document,
            "research_report": "",
            "sources": []
        }
        
        result = await auditor.run(state)
        
        # Should have validation errors
        assert "structure_validation" in result
        assert "errors" in result["structure_validation"]
        
        errors = result["structure_validation"]["errors"]
        assert len(errors) > 0
        assert any("99.9" in error for error in errors)


def test_section_reference_validation(mock_parsed_document):
    """Test section reference validation utility."""
    analysis = {
        "findings": [
            {"section": "3.2", "page": 3, "risk": "High"},
            {"section": "99.9", "page": 99, "risk": "Medium"},  # Invalid
            {"section": "1", "page": 1, "risk": "Low"}
        ]
    }
    
    errors = validate_section_references(analysis, mock_parsed_document)
    
    assert len(errors) == 1
    assert "99.9" in errors[0]


def test_deduplication_same_section_same_title():
    """Test that duplicate findings for same section are removed."""
    doc = MagicMock(spec=ParsedDocument)
    doc.section_map = {"3.2": "test"}
    
    findings = [
        {
            "section": "3.2",
            "title": "Payment Terms Issue",
            "risk": "High",
            "contract_text": "Version 1"
        },
        {
            "section": "3.2",
            "title": "payment terms issue",  # Same title, different case
            "risk": "Medium",  # Lower risk
            "contract_text": "Version 2"
        }
    ]
    
    deduplicated = _deduplicate_findings(findings, doc)
    
    # Should keep only the High risk version
    assert len(deduplicated) == 1
    assert deduplicated[0]["risk"] == "High"


def test_deduplication_same_section_different_titles():
    """Test that different issues in same section are kept."""
    doc = MagicMock(spec=ParsedDocument)
    doc.section_map = {"3.2": "test"}
    
    findings = [
        {
            "section": "3.2",
            "title": "Payment Terms Issue",
            "risk": "High"
        },
        {
            "section": "3.2",
            "title": "Late Fee Missing",  # Different issue
            "risk": "Medium"
        }
    ]
    
    deduplicated = _deduplicate_findings(findings, doc)
    
    # Should keep both
    assert len(deduplicated) == 2


def test_deduplication_keeps_higher_risk():
    """Test that higher risk version is kept when deduplicating."""
    doc = MagicMock(spec=ParsedDocument)
    doc.section_map = {"3.2": "test"}
    
    findings = [
        {
            "section": "3.2",
            "title": "Issue",
            "risk": "Medium"
        },
        {
            "section": "3.2",
            "title": "Issue",
            "risk": "Critical"  # Higher risk
        },
        {
            "section": "3.2",
            "title": "Issue",
            "risk": "Low"
        }
    ]
    
    deduplicated = _deduplicate_findings(findings, doc)
    
    assert len(deduplicated) == 1
    assert deduplicated[0]["risk"] == "Critical"


def test_risk_level_comparison():
    """Test risk level comparison logic."""
    assert _compare_risk_level("Critical", "High") > 0
    assert _compare_risk_level("High", "Medium") > 0
    assert _compare_risk_level("Medium", "Low") > 0
    assert _compare_risk_level("Low", "High") < 0
    assert _compare_risk_level("Medium", "Medium") == 0


def test_get_related_sections(mock_parsed_document):
    """Test finding related sections."""
    related = get_related_sections(mock_parsed_document, "3.2", "payment")
    
    # Should find sections with same clause type
    assert isinstance(related, list)
    # Payment section should not include itself
    assert not any(sec["number"] == "3.2" for sec in related)


def test_calculate_coverage_metrics(mock_parsed_document):
    """Test coverage calculation."""
    analysis = {
        "findings": [
            {"section": "3.2", "risk": "High"},
            {"section": "7.1", "risk": "Medium"}
        ]
    }
    
    metrics = calculate_coverage_metrics(analysis, mock_parsed_document)
    
    assert "total_sections" in metrics
    assert "analyzed_sections" in metrics
    assert "section_coverage_pct" in metrics
    assert "key_clause_coverage_pct" in metrics
    assert "missing_key_clauses" in metrics
    
    # Should have analyzed 2 out of 4 sections
    assert metrics["analyzed_sections"] == 2
    assert metrics["total_sections"] == 4
    assert metrics["section_coverage_pct"] == 50


def test_coverage_identifies_missing_key_clauses(mock_parsed_document):
    """Test that coverage identifies unanalyzed key clauses."""
    analysis = {
        "findings": [
            {"section": "3.2", "risk": "High"}  # Only payment analyzed
        ]
    }
    
    metrics = calculate_coverage_metrics(analysis, mock_parsed_document)
    
    missing = metrics.get("missing_key_clauses", [])
    
    # Should identify liability and termination as missing
    assert len(missing) >= 2
    assert any(c["type"] == "liability" for c in missing)
    assert any(c["type"] == "termination" for c in missing)


@pytest.mark.asyncio
async def test_analyst_fallback_without_structure():
    """Test that analyst works without document structure."""
    analyst = LegalRiskAnalyst()
    
    mock_response = """{
        "red_flags": [{"issue": "Test", "severity": "High", "description": "Test issue"}],
        "penalties": [],
        "obligations": [],
        "summary": "Test summary"
    }"""
    
    with patch('app.agents.analyst.generate', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        state = {
            "query": "Analyze contract",
            "original_query": "Full audit",
            "merged_context": "Sample text",
            "research_report": ""
        }
        
        result = await analyst.run(state)
        
        # Should still work without parsed_document
        assert "risk_analysis" in result
        assert "red_flags" in result["risk_analysis"]


def test_deduplication_preserves_findings_without_sections():
    """Test that findings without section references are preserved."""
    doc = MagicMock(spec=ParsedDocument)
    doc.section_map = {}
    
    findings = [
        {
            "title": "General Issue",
            "risk": "Medium"
            # No section field
        },
        {
            "section": "3.2",
            "title": "Specific Issue",
            "risk": "High"
        }
    ]
    
    deduplicated = _deduplicate_findings(findings, doc)
    
    # Should keep both
    assert len(deduplicated) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
