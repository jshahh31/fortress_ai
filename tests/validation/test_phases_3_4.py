"""
Test Phases 3 and 4: Analysis Logic Improvements and Section Referencing System
"""

import json
import pytest
from unittest.mock import MagicMock, patch
from app.agents.analyst import LegalRiskAnalyst
from app.services.analysis import _deduplicate_findings
from app.services.section_utils import validate_section_references

class MockParsedDocument:
    """Mock parsed document with section structure for testing."""

    def __init__(self, sections=None):
        self.sections = sections or [
            {"number": "1.1", "title": "Introduction", "page": 1, "content": "Intro text"},
            {"number": "2.1", "title": "Payment Terms", "page": 2, "content": "Payment text"},
            {"number": "3.1", "title": "Termination", "page": 3, "content": "Termination text"},
        ]
        self.section_map = {sec["number"]: sec for sec in self.sections}
        self.page_count = 5

@pytest.fixture
def mock_parsed_doc():
    """Fixture for mock parsed document."""
    return MockParsedDocument()

@pytest.fixture
def analyst():
    """Fixture for analyst instance."""
    return LegalRiskAnalyst()

def test_phase_3_deduplication_with_section_enforcement(mock_parsed_doc):
    """Test that deduplication enforces section references."""
    findings = [
        {
            "section": "2.1",
            "page": 2,
            "title": "Payment Terms Issue",
            "risk": "High",
            "justification": "60-day term exceeds standard",
            "contract_text": "Payment within 60 days",
            "priority": 1
        },
        {
            "title": "Generic Finding Without Section",  # Missing section - should be filtered
            "risk": "Medium",
            "description": "Generic warning"
        },
        {
            "section": "2.1",  # Duplicate section - should be deduplicated
            "page": 2,
            "title": "Payment Terms Issue",
            "risk": "Low",  # Lower risk - should be replaced
            "justification": "Mild concern",
            "contract_text": "Payment within 60 days",
            "priority": 3
        },
        {
            "section": "9.9",  # Invalid section - should be marked
            "page": 9,
            "title": "Invalid Section Finding",
            "risk": "High",
            "justification": "Test",
            "contract_text": "Test text",
            "priority": 1
        }
    ]

    # Apply deduplication with section enforcement
    result = _deduplicate_findings(findings, mock_parsed_doc)

    # Should have 2 valid findings (1 valid + 1 invalid but marked)
    assert len(result) == 2

    # Generic finding without section should be filtered out
    assert not any(f.get("title") == "Generic Finding Without Section" for f in result)

    # High risk finding should be kept over low risk duplicate
    assert result[0]["risk"] == "High"
    assert result[0]["section"] == "2.1"

    # Invalid section should be marked with validation error
    invalid_finding = next(f for f in result if f.get("section") == "9.9")
    assert "validation_errors" in invalid_finding
    assert "Section 9.9 not found in document" in invalid_finding["validation_errors"]

@patch('app.agents.analyst.generate')
def test_phase_4_section_reference_enforcement(mock_generate, analyst, mock_parsed_doc):
    """Test that analyst enforces section references in responses."""
    # Mock LLM response with and without section references
    response_with_sections = """
    {
        "findings": [
            {
                "section": "2.1",
                "page": 2,
                "title": "Valid Payment Terms Issue",
                "risk": "High",
                "justification": "60-day term exceeds standard",
                "contract_text": "Payment within 60 days",
                "priority": 1
            }
        ]
    }
    """

    response_without_sections = """
    {
        "findings": [
            {
                "title": "Generic Finding Without Section",
                "risk": "Medium",
                "description": "Generic warning"
            }
        ]
    }
    """

    # Test 1: Response with valid sections should pass through
    mock_generate.return_value = response_with_sections
    state = {
        "parsed_document": mock_parsed_doc,
        "original_query": "Analyze contract",
        "merged_context": "Contract text",
        "research_report": "Research findings"
    }

    result = analyst.run(state)
    analysis = result["risk_analysis"]
    assert len(analysis["findings"]) == 1
    assert analysis["findings"][0]["section"] == "2.1"

    # Test 2: Response without sections should be filtered
    mock_generate.return_value = response_without_sections
    result = analyst.run(state)
    analysis = result["risk_analysis"]

    # Should have no valid findings (filtered out due to missing section)
    assert len(analysis.get("findings", [])) == 0
    # Should have validation errors
    assert "validation_errors" in analysis
    assert any("missing section reference" in err.lower() for err in analysis["validation_errors"])

def test_section_reference_validation(mock_parsed_doc):
    """Test the section reference validation utility."""
    findings = [
        {
            "section": "2.1",  # Valid section
            "title": "Valid Finding",
            "risk": "High"
        },
        {
            "section": "9.9",  # Invalid section
            "title": "Invalid Section Finding",
            "risk": "High"
        },
        {
            "title": "Missing Section Finding",  # No section
            "risk": "Medium"
        }
    ]

    analysis = {"findings": findings}
    errors = validate_section_references(analysis, mock_parsed_doc)

    # Should have 2 errors (invalid section + missing section)
    assert len(errors) == 2
    assert any("9.9" in error for error in errors)
    assert any("missing section reference" in error.lower() for error in errors)

def test_contract_text_enforcement():
    """Test that contract text is enforced when section references exist."""
    analyst = LegalRiskAnalyst()
    findings = [
        {
            "section": "2.1",
            "page": 2,
            "title": "Finding Without Contract Text",
            "risk": "High"
            # Missing contract_text
        }
    ]

    mock_parsed_doc = MockParsedDocument()
    result = analyst._parse_and_validate_response(
        json.dumps({"findings": findings}),
        mock_parsed_doc
    )

    # Should have validation error for missing contract text
    assert "validation_errors" in result
    assert any("missing specific contract language" in err.lower() for err in result["validation_errors"])


