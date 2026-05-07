import logging
from app.agents.state import AgentState
from app.services.llm import generate

logger = logging.getLogger(__name__)

class FinalAuditor:
    async def run(self, state: AgentState) -> AgentState:
        """Audit the risk analysis and generate the final report."""
        logger.info("FinalAuditor: Auditing findings")

        research = state.get("research_report", "")
        risk_analysis = state.get("risk_analysis", {})
        sources = state.get("sources", [])

        # Step 1: Reflection/Audit
        audit_prompt = f"""
        You are a Senior Legal Editor and Auditor. Review the following Risk Analysis against the Research Findings.
        
        RESEARCH FINDINGS:
        {research}
        
        RISK ANALYSIS:
        {risk_analysis}
        
        TASK:
        1. Check for hallucinations: Does the Risk Analysis claim anything not supported by the Research or Document?
        2. Check for missing details: Did the Analyst overlook a key penalty or obligation mentioned in the research?
        3. Provide a 'Reflection' on the accuracy of the analysis.
        """
        
        audit_reflection = await generate(audit_prompt, system_prompt="You are a critical Legal Auditor.")

        # Step 2: Final Report Generation
        report_prompt = f"""
        You are a Legal Reporting Expert. Synthesize the final legal audit report based on the findings and the auditor's reflection.
        
        AUDITOR REFLECTION:
        {audit_reflection}
        
        RISK ANALYSIS:
        {risk_analysis}
        
        SOURCES:
        {sources}
        
        INSTRUCTIONS:
        - Use professional, clear Markdown.
        - Include a 'Verdict' section (e.g., Compliant, Conditional, High Risk).
        - List Red Flags, Penalties, and Obligations clearly.
        - List all sources at the end.
        - Do not include internal reflection notes in the final report.
        """

        final_report = await generate(report_prompt, system_prompt="You are a professional legal reporter.")

        return {
            **state,
            "audit_report": audit_reflection,
            "final_report_md": final_report
        }
