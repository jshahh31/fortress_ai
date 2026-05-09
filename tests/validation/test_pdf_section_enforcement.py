"""
Test PDF Section Enforcement - Verify that all section references come from the actual PDF document structure
"""

import json
import pytest
from unittest.mock import MagicMock, patch
from app.agents.analyst import LegalRiskAnalyst
from app.services.section_utils import validate_section_references

class MockSection:
    """Mock section for testing."""
    def __init__(self, number, title, page_num, content="", clause_type="general"):
        self.number = number
        self.title = title
        self.page_num = page_num
        self.content = content
        self.clause_type = clause_type
        self.start_block_index = 0
        self.end_block_index = 0

class MockParsedDocument:
    """Mock parsed document with section structure for testing."""
    def __init__(self, sections=None):
        self.sections = sections or [
            MockSection("1.1", "Introduction", 1, "Intro text"),
            MockSection("2.1", "Payment Terms", 2, "Payment within 30 days"),
            MockSection("3.1", "Termination", 3, "60 days notice required"),
        ]
        self.section_map = {sec.number: sec for sec in self.sections}
        self.page_count = 5

@pytest.fixture
def mock_parsed_doc():
    """Fixture for mock parsed document."""
    return MockParsedDocument()

@pytest.fixture
def analyst():
    """Fixture for analyst instance."""
    return LegalRiskAnalyst()

def test_pdf_section_enforcement(mock_parsed_doc):
    """Test that only PDF-extracted sections are allowed."""
    # Create findings with valid and invalid sections
    findings = [
        {
            "section": "2.1",  # Valid - exists in PDF
            "page": 2,
            "title": "Valid Payment Terms",
            "risk": "High",
            "contract_text": "Payment within 30 days",
            "priority": 1
        },
        {
            "section": "9.9",  # Invalid - doesn't exist in PDF
            "page": 9,
            "title": "Invalid Section",
            "risk": "High",
            "contract_text": "Some text",
            "priority": 1
        },
        {
            "title": "Missing Section",  # Missing section entirely
            "risk": "Medium",
            "description": "Generic warning"
        }
    ]

    analysis = {"findings": findings}

    # Test validation
    errors = validate_section_references(analysis, mock_parsed_doc)

    # Should have errors for invalid and missing sections
    assert len(errors) == 2
    assert any("9.9" in error for error in errors)
    assert any("missing section reference" in error.lower() for error in errors)

def test_contract_text_must_match_pdf(mock_parsed_doc):
    """Test that contract text must come from the PDF section."""
    findings = [
        {
            "section": "2.1",  # Valid section
            "page": 2,
            "title": "Payment Terms",
            "risk": "High",
            "contract_text": "WRONG TEXT NOT FROM PDF",  # Doesn't match PDF content
            "priority": 1
        }
    ]

    analysis = {"findings": findings}

    # Test validation
    errors = validate_section_references(analysis, mock_parsed_doc)

    # Should have error about contract text mismatch
    assert len(errors) == 1
    assert any("contract text mismatch" in error.lower() for error in errors)

def test_page_number_must_match_pdf(mock_parsed_doc):
    """Test that page numbers must match the PDF structure."""
    findings = [
        {
            "section": "2.1",  # Valid section
            "page": 99,  # Wrong page number
            "title": "Payment Terms",
            "risk": "High",
            "contract_text": "Payment within 30 days",  # Matches PDF content
            "priority": 1
        }
    ]

    analysis = {"findings": findings}

    # Test validation
    errors = validate_section_references(analysis, mock_parsed_doc)

    # Should have error about page number mismatch
    assert len(errors) == 1
    assert any("page mismatch" in error.lower() for error in errors)

@patch('app.agents.analyst.generate')
def test_analyst_rejects_invalid_sections(mock_generate, analyst, mock_parsed_doc):
    """Test that analyst rejects findings with invalid PDF sections."""
    # Mock LLM response with invalid sections
    response = """
    {
        "findings": [
            {
                "section": "9.9",  # Invalid section
                "page": 9,
                "title": "Invalid Section Finding",
                "risk": "High",
                "contract_text": "Some text",
                "priority": 1
            }
        ]
    }
    """

    mock_generate.return_value = response
    state = {
        "parsed_document": mock_parsed_doc,
        "original_query": "Analyze contract",
        "merged_context": "Contract text",
        "research_report": "Research findings"
    }

    # Run analyst
    result = analyst.run(state)
    analysis = result["risk_analysis"]

    # Should have validation errors
    assert "validation_errors" in analysis
    assert any("9.9" in error for error in analysis["validation_errors"])

    # Should have NO valid findings (all filtered out)
    assert len(analysis.get("findings", [])) == 0

@patch('app.agents.analyst.generate')
def test_analyst_accepts_valid_pdf_sections(mock_generate, analyst, mock_parsed_doc):
    """Test that analyst accepts findings with valid PDF sections."""
    # Mock LLM response with valid sections
    response = """
    {
        "findings": [
            {
                "section": "2.1",  # Valid section from PDF
                "page": 2,
                "title": "Valid Payment Terms",
                "risk": "High",
                "contract_text": "Payment within 30 days",  # Matches PDF content
                "priority": 1
            }
        ]
    }
    """

    mock_generate.return_value = response
    state = {
        "parsed_document": mock_parsed_doc,
        "original_query": "Analyze contract",
        "merged_context": "Contract text",
        "research_report": "Research findings"
    }

    # Run analyst
    result = analyst.run(state)
    analysis = result["risk_analysis"]

    # Should have NO validation errors
    assert "validation_errors" not in analysis or not analysis["validation_errors"]

    # Should have valid findings
    assert len(analysis.get("findings", [])) == 1
    assert analysis["findings"][0]["section"] == "2.1"


