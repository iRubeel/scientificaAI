"""
Synthesizer component for combining findings into final review.
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid

from app.core.gemini import GeminiClient
from app.core.state import AgentState
from app.models.review_models import Review, ReviewSection


class Synthesizer:
    """Synthesizes findings into a coherent review."""
    
    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize synthesizer.
        
        Args:
            gemini_client: Gemini API client
        """
        self.gemini = gemini_client
        
    async def synthesize_section(
        self,
        section_name: str,
        state: AgentState
    ) -> ReviewSection:
        """
        Synthesize findings for a specific section.
        
        Args:
            section_name: Name of the section
            state: Current agent state
            
        Returns:
            Complete ReviewSection
        """
        # Get claims for this section
        section_claims = state.get_claims_by_section(section_name)
        
        # Get relevant reasoning steps and critiques
        relevant_reasoning = [
            step for step in state.reasoning_history
            if any(claim.claim_id in step.description for claim in section_claims)
        ]
        
        relevant_critiques = [
            critique for critique in state.critiques
            if any(critique.target_id == claim.claim_id for claim in section_claims)
        ]
        
        # Generate section summary and assessment
        prompt = f"""You are synthesizing findings for the "{section_name}" section of a paper review.

Claims Analyzed ({len(section_claims)}):
{self._format_claims(section_claims)}

Reasoning Steps ({len(relevant_reasoning)}):
{self._format_reasoning(relevant_reasoning)}

Critiques Raised ({len(relevant_critiques)}):
{self._format_critiques(relevant_critiques)}

Provide:
1. A comprehensive summary of findings for this section
2. An overall assessment: strong/acceptable/weak/flawed

Respond with JSON:
{{
    "summary": "<detailed summary>",
    "overall_assessment": "<strong|acceptable|weak|flawed>"
}}"""

        schema = {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "overall_assessment": {
                    "type": "string",
                    "enum": ["strong", "acceptable", "weak", "flawed"]
                }
            }
        }
        
        response = await self.gemini.generate_structured_output(prompt, schema, temperature=0.4)
        
        return ReviewSection(
            section_name=section_name,
            claims_analyzed=section_claims,
            reasoning_steps=relevant_reasoning,
            critiques=relevant_critiques,
            summary=response["summary"],
            overall_assessment=response["overall_assessment"]
        )
    
    async def synthesize_final_review(
        self,
        state: AgentState
    ) -> Review:
        """
        Synthesize all findings into a final review.
        
        Args:
            state: Current agent state with all findings
            
        Returns:
            Complete Review object
        """
        # Generate final recommendation and summary
        prompt = f"""You are writing the final review for a mathematical/statistical paper.

Paper: {state.paper.title}

Sections Reviewed ({len(state.sections)}):
{self._format_sections(state.sections)}

Overall Critiques ({len(state.critiques)}):
{self._format_critiques(state.critiques)}

Total Claims Analyzed: {len(state.claims)}
Total Reasoning Steps: {len(state.reasoning_history)}

Provide:
1. Final recommendation: accept/minor_revision/major_revision/reject
2. Confidence in recommendation (0.0-1.0)
3. Overall summary (2-3 paragraphs)
4. Key strengths (list)
5. Key weaknesses (list)

Respond with JSON:
{{
    "final_recommendation": "<accept|minor_revision|major_revision|reject>",
    "confidence": <float>,
    "summary": "<summary>",
    "strengths": [<list of strings>],
    "weaknesses": [<list of strings>]
}}"""

        schema = {
            "type": "object",
            "properties": {
                "final_recommendation": {
                    "type": "string",
                    "enum": ["accept", "minor_revision", "major_revision", "reject"]
                },
                "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "summary": {"type": "string"},
                "strengths": {"type": "array", "items": {"type": "string"}},
                "weaknesses": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        response = await self.gemini.generate_structured_output(prompt, schema, temperature=0.4)
        
        # Create final review
        review = state.to_review(
            review_id=str(uuid.uuid4()),
            final_recommendation=response["final_recommendation"],
            confidence=response["confidence"],
            summary=response["summary"],
            strengths=response["strengths"],
            weaknesses=response["weaknesses"]
        )
        
        return review
    
    def _format_claims(self, claims: List) -> str:
        """Format claims for prompt."""
        if not claims:
            return "No claims"
        
        lines = []
        for claim in claims[:10]:  # Limit to first 10
            lines.append(f"- [{claim.claim_type}] {claim.content[:100]}...")
            lines.append(f"  Confidence: {claim.epistemic_state.confidence:.2f}")
        
        if len(claims) > 10:
            lines.append(f"... and {len(claims) - 10} more")
        
        return "\n".join(lines)
    
    def _format_reasoning(self, steps: List) -> str:
        """Format reasoning steps for prompt."""
        if not steps:
            return "No reasoning steps"
        
        lines = []
        for step in steps[:5]:  # Limit to first 5
            lines.append(f"{step.step_number}. {step.description}")
            lines.append(f"   Conclusion: {step.intermediate_conclusion[:100]}...")
        
        if len(steps) > 5:
            lines.append(f"... and {len(steps) - 5} more")
        
        return "\n".join(lines)
    
    def _format_critiques(self, critiques: List) -> str:
        """Format critiques for prompt."""
        if not critiques:
            return "No critiques"
        
        lines = []
        for critique in critiques[:10]:  # Limit to first 10
            lines.append(f"- [{critique.severity}] {critique.critique_type}: {critique.description[:100]}...")
        
        if len(critiques) > 10:
            lines.append(f"... and {len(critiques) - 10} more")
        
        return "\n".join(lines)
    
    def _format_sections(self, sections: List[ReviewSection]) -> str:
        """Format review sections for prompt."""
        if not sections:
            return "No sections"
        
        lines = []
        for section in sections:
            lines.append(f"- {section.section_name}: {section.overall_assessment}")
            lines.append(f"  {section.summary[:150]}...")
        
        return "\n".join(lines)
