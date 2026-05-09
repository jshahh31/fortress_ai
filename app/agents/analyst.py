import json
import logging
from typing import Dict, Any, List
from app.agents.state import AgentState
from app.services.llm import generate
from app.services.section_utils import (
    get_section_context,
    get_related_sections,
    validate_section_references,
    format_section_reference
)

logger = logging.getLogger(__name__)

class LegalRiskAnalyst:
    async def run(self, state: AgentState) -> AgentState:
        """Analyze legal risks with document structure awareness."""
        logger.info("LegalRiskAnalyst: Analyzing risks with structure context")
        
        # Get document structure if available
        parsed_doc = state.get("parsed_document")
        context = state.get("merged_context", "")
        research = state.get("research_report", "")
        query = state.get("original_query", "")
        
        # Build structure-aware prompt
        if parsed_doc:
            prompt = self._build_structure_aware_prompt(state, parsed_doc)
        else:
            # Fallback to basic prompt if no structure available
            prompt = self._build_basic_prompt(query, research, context)
        
        response = await generate(
            prompt,
            system_prompt="You are a meticulous Legal Risk Analyst. Return JSON only with specific section references."
        )
        
        # Parse and validate response
        risk_analysis = self._parse_and_validate_response(response, parsed_doc)
        
        return {
            **state,
            "risk_analysis": risk_analysis
        }
    
    def _build_structure_aware_prompt(self, state: AgentState, parsed_doc) -> str:
        """Build prompt requiring structure-aware analysis."""
        query = state.get("original_query", "")
        research = state.get("research_report", "")
        context = state.get("merged_context", "")
        
        # Build document overview
        doc_overview = self._build_document_overview(parsed_doc)
        
        # Get key clauses summary
        key_clauses_text = self._format_key_clauses(parsed_doc)
        
        return f"""
You are a Senior Legal Risk Analyst analyzing a contract with full document structure awareness.

{doc_overview}

{key_clauses_text}

QUERY: {query}

RESEARCH FINDINGS:
{research[:2000] if research else "No external research available"}

DOCUMENT CONTEXT:
{context[:3000]}

CRITICAL REQUIREMENTS - YOU MUST FOLLOW THESE:

1. **SECTION REFERENCES ARE MANDATORY**
   - Every finding MUST reference the exact section number (e.g., "3.2", "7.1")
   - Include the PAGE NUMBER where the section appears
   - Quote SPECIFIC contract language being analyzed

2. **RISK JUSTIFICATION REQUIRED**
   - Explain WHY you assigned each risk level (High/Medium/Low)
   - Compare to industry standards when applicable
   - Reference specific contract terms that create the risk

3. **ACTIONABLE RECOMMENDATIONS**
   - Provide PRECISE revision suggestions tailored to the exact contract language
   - Don't use generic advice like "review with counsel"
   - Suggest specific alternative wording when possible

4. **NO DUPLICATES**
   - Each section should appear only once
   - If multiple issues in one section, combine them into a single comprehensive finding

5. **PRIORITIZATION**
   - Assign priority 1-5 (1 = most urgent)
   - Consider: risk level, business impact, ease of remediation

OUTPUT FORMAT (JSON):
{{
  "findings": [
    {{
      "section": "3.2",
      "page": 5,
      "title": "Payment Terms Issue",
      "risk": "High",
      "justification": "60-day payment term exceeds industry standard of 30 days, creating cash flow risk. No late payment penalties specified, removing incentive for timely payment.",
      "contract_text": "Client shall pay within sixty (60) days of receipt of invoice. No late fees shall apply.",
      "recommendation": "Revise to 'thirty (30) days' to match standard B2B terms. Add clause: 'Late payments shall incur 1.5% monthly interest.'",
      "priority": 1,
      "related_sections": ["7.1", "9.2"],
      "clause_type": "payment"
    }}
  ]
}}

REMEMBER: Generic findings without section references will be rejected. Be specific and actionable.
"""
    
    def _build_basic_prompt(self, query: str, research: str, context: str) -> str:
        """Fallback prompt when no document structure is available."""
        return f"""
You are a Senior Legal Risk Analyst analyzing a contract.

QUERY: {query}

RESEARCH FINDINGS:
{research[:2000] if research else "No external research available"}

DOCUMENT CONTEXT:
{context[:3000]}

INSTRUCTIONS:
1. Identify Red Flags: Points of high risk or potential legal violation
2. Identify Penalties: Possible fines or legal consequences
3. Identify Obligations: Key actions required for compliance
4. Categorize each risk as High, Medium, or Low
5. Reference page numbers and section headers when available

OUTPUT FORMAT:
Return ONLY a JSON object with this structure:
{{
    "red_flags": [
        {{"issue": "...", "severity": "High/Med/Low", "description": "..."}}
    ],
    "penalties": [
        {{"type": "...", "severity": "High/Med/Low", "impact": "..."}}
    ],
    "obligations": [
        {{"task": "...", "deadline": "...", "description": "..."}}
    ],
    "summary": "..."
}}
"""
    
    def _build_document_overview(self, parsed_doc) -> str:
        """Build document overview section."""
        if not parsed_doc:
            return ""
        
        structure = parsed_doc.structure if hasattr(parsed_doc, 'structure') else {}
        key_clauses = structure.get("key_clauses", {})
        
        overview = [
            "DOCUMENT OVERVIEW:",
            f"- Total Pages: {parsed_doc.page_count}",
            f"- Total Sections: {len(parsed_doc.sections)}",
            f"- Key Clause Types: {', '.join(key_clauses.keys()) if key_clauses else 'None identified'}"
        ]
        
        return "\n".join(overview)
    
    def _format_key_clauses(self, parsed_doc) -> str:
        """Format key clauses for prompt context."""
        if not parsed_doc or not hasattr(parsed_doc, 'structure'):
            return ""
        
        key_clauses = parsed_doc.structure.get("key_clauses", {})
        if not key_clauses:
            return ""
        
        lines = ["KEY CLAUSES TO ANALYZE:"]
        for clause_type, sections in key_clauses.items():
            lines.append(f"\n{clause_type.upper()}:")
            for sec_ref in sections[:3]:  # Show first 3 of each type
                lines.append(f"  - {sec_ref}")
            if len(sections) > 3:
                lines.append(f"  - ... and {len(sections) - 3} more")
        
        return "\n".join(lines)
    
    def _format_related_sections(self, sections: List[Dict]) -> str:
        """Format related sections for prompt context."""
        if not sections:
            return "None"
        
        return "\n".join([
            f"- {sec['number']} {sec['title']} (Page {sec['page']}) [{sec.get('relationship', 'related')}]"
            for sec in sections
        ])
    
    def _parse_and_validate_response(self, response: str, parsed_doc) -> Dict:
        """Parse response and validate section references."""
        try:
            # Clean response
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:-3].strip()
            elif clean_response.startswith("```"):
                clean_response = clean_response[3:-3].strip()
            
            analysis = json.loads(clean_response)
            
            # Validate section references if document structure available
            if parsed_doc and "findings" in analysis:
                errors = validate_section_references(analysis, parsed_doc)
                if errors:
                    analysis["validation_errors"] = errors
                    logger.warning(f"Section reference validation errors: {errors}")
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analysis JSON: {e}")
            return {
                "error": "Failed to parse analysis",
                "raw_output": response,
                "findings": [],
                "red_flags": [],
                "penalties": [],
                "obligations": [],
                "summary": "Analysis failed to format correctly."
            }
