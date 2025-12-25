"""
Critic component for self-critique and epistemic reasoning.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from app.core.gemini import GeminiClient
from app.core.state import AgentState
from app.models.review_models import (
    Critique, Claim, ReasoningStep, EpistemicState, ClaimStatus
)


class Critic:
    """Performs self-critique and epistemic tracking."""
    
    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize critic.
        
        Args:
            gemini_client: Gemini API client
        """
        self.gemini = gemini_client
        
    async def critique_claim(
        self,
        claim: Claim,
        state: AgentState
    ) -> List[Critique]:
        """
        Critique a specific claim.
        
        Args:
            claim: Claim to critique
            state: Current agent state
            
        Returns:
            List of critiques
        """
        prompt = f"""You are a rigorous mathematical and statistical critic reviewing a claim from a research paper.

Claim Type: {claim.claim_type}
Claim: {claim.content}
Section: {claim.section}

Current Epistemic State:
- Confidence: {claim.epistemic_state.confidence}
- Evidence Quality: {claim.epistemic_state.evidence_quality}
- Uncertainty Sources: {', '.join(claim.epistemic_state.uncertainty_sources) if claim.epistemic_state.uncertainty_sources else 'None identified'}

Analyze this claim critically using the following criteria:
1. Logical Consistency: Look for logical gaps, circular reasoning, contradictions, or non-sequiturs.
2. Assumption Validity: Identify unstated, overly strong, or violated assumptions.
3. Methodological Soundness: Check for inappropriate methods, incorrect implementation, missing baselines, or overfitting.
4. Evidence Sufficiency: Assess if there is insufficient data, biased sampling, or weak evidence.
5. Statistical Rigor: Guard against p-hacking, misinterpretation of p-values, and violated statistical assumptions.
6. Clarity & Notation: Flag ambiguous notation, vague definitions, or poor structure.

For each issue found, provide:
- critique_type: one of [logical_gap, circular_reasoning, contradiction, assumption_violation, methodological_flaw, insufficient_evidence, statistical_error, notation_ambiguity]
- severity: one of [critical, major, minor, informational]
- description: detailed explanation of the issue
- suggested_revision: specific steps to address the issue (optional)

Respond with a JSON array of critiques."""

        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "critique_type": {
                        "type": "string",
                        "enum": [
                            "logical_gap", "circular_reasoning", "contradiction", 
                            "assumption_violation", "methodological_flaw", 
                            "insufficient_evidence", "statistical_error", "notation_ambiguity"
                        ]
                    },
                    "severity": {"type": "string", "enum": ["critical", "major", "minor", "informational"]},
                    "description": {"type": "string"},
                    "suggested_revision": {"type": "string"}
                }
            }
        }
        
        response = await self.gemini.generate_structured_output(prompt, schema, temperature=0.3)
        
        critiques = []
        for critique_data in response:
            critique = Critique(
                target_id=claim.claim_id,
                critique_type=critique_data["critique_type"],
                severity=critique_data["severity"],
                description=critique_data["description"],
                suggested_revision=critique_data.get("suggested_revision")
            )
            critiques.append(critique)
        
        return critiques
    
    async def recalibrate_claim_confidence(
        self,
        claim: Claim,
        critiques: List[Critique],
        state: AgentState
    ) -> None:
        """
        Recalibrate claim confidence based on critiques.
        
        Args:
            claim: Claim to recalibrate
            critiques: Critiques found for this claim
            state: Agent state to update
        """
        if not critiques:
            return
            
        base_confidence = claim.epistemic_state.confidence
        
        # Calculate reduction based on critique severity
        reduction = 0.0
        for critique in critiques:
            if critique.severity == "critical":
                reduction += 0.4
            elif critique.severity == "major":
                reduction += 0.2
            elif critique.severity == "minor":
                reduction += 0.05
                
        new_confidence = max(0.0, min(base_confidence, base_confidence - reduction))
        
        # Only update if confidence actually changes
        if new_confidence < base_confidence:
            state.update_claim(claim.claim_id, {
                "confidence": new_confidence,
                "status": ClaimStatus.QUESTIONED if reduction > 0.1 else claim.status
            })
    
    async def critique_reasoning(
        self,
        reasoning_step: ReasoningStep,
        state: AgentState
    ) -> List[Critique]:
        """
        Critique a reasoning step.
        
        Args:
            reasoning_step: Reasoning step to critique
            state: Current agent state
            
        Returns:
            List of critiques
        """
        prompt = f"""You are critiquing a reasoning step in a paper review.

Step {reasoning_step.step_number}: {reasoning_step.description}

Reasoning: {reasoning_step.reasoning}

Intermediate Conclusion: {reasoning_step.intermediate_conclusion}
Confidence: {reasoning_step.confidence}

Tool Calls Made:
{self._format_tool_calls(reasoning_step.tool_calls)}

Critically evaluate this reasoning step. Check for:
1. Logical validity and consistency of the reasoning.
2. Proper use of tools and interpretation of results.
3. Unjustified confidence levels.
4. Missing considerations or alternative explanations.
5. Adherence to mathematical/statistical review standards.

For each issue found, provide:
- critique_type: one of [logical_gap, circular_reasoning, contradiction, assumption_violation, methodological_flaw, insufficient_evidence, statistical_error, notation_ambiguity]
- severity: one of [critical, major, minor, informational]
- description: detailed explanation
- suggested_revision: how to address the issue (optional)

Respond with a JSON array of critiques (may be empty if no issues found)."""

        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "critique_type": {
                        "type": "string",
                        "enum": [
                            "logical_gap", "circular_reasoning", "contradiction", 
                            "assumption_violation", "methodological_flaw", 
                            "insufficient_evidence", "statistical_error", "notation_ambiguity"
                        ]
                    },
                    "severity": {"type": "string", "enum": ["critical", "major", "minor", "informational"]},
                    "description": {"type": "string"},
                    "suggested_revision": {"type": "string"}
                }
            }
        }
        
        response = await self.gemini.generate_structured_output(prompt, schema, temperature=0.3)
        
        critiques = []
        for critique_data in response:
            critique = Critique(
                target_id=f"step_{reasoning_step.step_number}",
                critique_type=critique_data["critique_type"],
                severity=critique_data["severity"],
                description=critique_data["description"],
                suggested_revision=critique_data.get("suggested_revision")
            )
            critiques.append(critique)
        
        return critiques
    
    async def assess_epistemic_state(
        self,
        claim: Claim,
        evidence: List[Dict[str, Any]],
        state: AgentState
    ) -> EpistemicState:
        """
        Assess the epistemic state of a claim based on evidence.
        
        Args:
            claim: Claim to assess
            evidence: Evidence gathered (e.g., tool results, literature)
            state: Current agent state
            
        Returns:
            Updated EpistemicState
        """
        prompt = f"""You are assessing the epistemic state of a mathematical/statistical claim.

Claim: {claim.content}

Evidence Gathered:
{self._format_evidence(evidence)}

Assess:
1. Confidence level (0.0 to 1.0) based on the strength of evidence
2. Quality of evidence (strong/moderate/weak/none)
3. Sources of uncertainty
4. Whether further verification is needed

Respond with JSON matching this structure:
{{
    "confidence": <float 0.0-1.0>,
    "evidence_quality": "<strong|moderate|weak|none>",
    "uncertainty_sources": [<list of strings>],
    "requires_verification": <boolean>
}}"""

        schema = {
            "type": "object",
            "properties": {
                "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "evidence_quality": {"type": "string", "enum": ["strong", "moderate", "weak", "none"]},
                "uncertainty_sources": {"type": "array", "items": {"type": "string"}},
                "requires_verification": {"type": "boolean"}
            }
        }
        
        response = await self.gemini.generate_structured_output(prompt, schema, temperature=0.2)
        
        return EpistemicState(
            confidence=response["confidence"],
            evidence_quality=response["evidence_quality"],
            uncertainty_sources=response["uncertainty_sources"],
            requires_verification=response["requires_verification"]
        )
    
    def _format_tool_calls(self, tool_calls: List) -> str:
        """Format tool calls for prompt."""
        if not tool_calls:
            return "No tool calls"
        
        lines = []
        for tc in tool_calls:
            lines.append(f"- {tc.tool_name}: {'Success' if tc.success else 'Failed'}")
            if not tc.success and tc.error_message:
                lines.append(f"  Error: {tc.error_message}")
        return "\n".join(lines)
    
    def _format_evidence(self, evidence: List[Dict[str, Any]]) -> str:
        """Format evidence for prompt."""
        if not evidence:
            return "No evidence provided"
        
        lines = []
        for i, ev in enumerate(evidence, 1):
            lines.append(f"{i}. {ev.get('type', 'Unknown')}: {ev.get('summary', str(ev))}")
        return "\n".join(lines)
    
    async def perform_self_critique(self, state: AgentState) -> List[Critique]:
        """
        Perform overall self-critique of the review so far.
        
        Args:
            state: Current agent state
            
        Returns:
            List of overall critiques
        """
        prompt = f"""You are performing a meta-level critique of an ongoing paper review.

Review Progress:
- Claims analyzed: {len(state.claims)}
- Reasoning steps: {len(state.reasoning_history)}
- Existing critiques: {len(state.critiques)}
- Sections completed: {len(state.sections)}

Consider:
1. Are there gaps in the analysis?
2. Have all major claims been examined?
3. Is the reasoning chain coherent?
4. Are there contradictions in the findings?
5. Has sufficient evidence been gathered?

Respond with a JSON array of high-level critiques about the review process itself."""

        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "critique_type": {
                        "type": "string",
                        "enum": ["logical_gap", "assumption_violation", "insufficient_evidence", "alternative_interpretation"]
                    },
                    "severity": {"type": "string", "enum": ["critical", "major", "minor"]},
                    "description": {"type": "string"},
                    "suggested_revision": {"type": "string"}
                }
            }
        }
        
        response = await self.gemini.generate_structured_output(prompt, schema, temperature=0.3)
        
        critiques = []
        for critique_data in response:
            critique = Critique(
                target_id="overall_review",
                critique_type=critique_data["critique_type"],
                severity=critique_data["severity"],
                description=critique_data["description"],
                suggested_revision=critique_data.get("suggested_revision")
            )
            critiques.append(critique)
        
        return critiques

    async def get_adaptive_recommendations(
        self,
        critiques: List[Critique]
    ) -> List[str]:
        """
        Analyze critiques and generate actionable recommendations for the planner.
        
        Args:
            critiques: List of identified critiques
            
        Returns:
            List of recommended tasks for the planner
        """
        if not critiques:
            return []
            
        critique_summaries = "\n".join([
            f"- [{c.critique_type}] {c.description} (Severity: {c.severity})"
            for c in critiques
        ])
        
        prompt = f"""You are an adaptive planning assistant for a scientific paper review agent.
Review the following critiques identified during the self-critique phase:

{critique_summaries}

Based on these critiques, what specific investigative or verification tasks should the agent perform next?
Tasks should be actionable and aimed at resolving the identified issues or clarifying uncertainties.

Respond with a JSON array of task descriptions (strings)."""

        schema = {
            "type": "array",
            "items": {"type": "string"}
        }
        
        response = await self.gemini.generate_structured_output(prompt, schema, temperature=0.2)
        return response
