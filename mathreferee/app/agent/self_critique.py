"    old_conf = state.epistemic_ledger.current_claims[claim_id].confidence
                
                # Only lower confidence (self-critique should be conservative)
                if new_conf < old_conf:
                    state.update_claim(claim_id, {"confidence": float(new_conf)})
                    adjustments_made += 1
        
        # Create issues for missed aspects
        for aspect in response.get("missed_aspects", []):
            issue = ReviewIssue(
                issue_id=f"self_critique_{len(state.issues_found)}",
                severity=Severity.MODERATE,
                issue_type="insufficient_evidence",
                description=f"Self-critique identified gap: {aspect}",
                location="overall review",
                suggested_resolution="Investigate this aspect more thoroughly",
                affects_validity=False,
                confidence_in_issue=0.7
            )
            state.add_issue(issue)
        
        return {
            "missed_aspects": response.get("missed_aspects", []),
            "overconfident_claims": response.get("overconfident_claims", []),
            "confidence_adjustments_made": adjustments_made,
            "additional_concerns": response.get("additional_concerns", []),
            "self_assessment": response.get("self_assessment", "")
        }
    
    def _format_claims(self, state: AgentState, limit: int = 5) -> str:
        """Format recent claims for prompt."""
        claims = list(state.epistemic_ledger.current_claims.values())[-limit:]
        if not claims:
            return "No claims yet"
        return "\n".join([
            f"- {c.claim_id}: {c.content[:100]} (confidence: {c.confidence:.2f})"
            for c in claims
        ])
    
    def _format_issues(self, state: AgentState, limit: int = 5) -> str:
        """Format recent issues for prompt."""
        if not state.issues_found:
            return "No issues found"
        return "\n".join([
            f"- {i.severity.value}: {i.description[:100]}"
            for i in state.issues_found[-limit:]
        ])


class AdversarialReviewer:
    """
    Acts as an adversarial reviewer trying to find flaws.
    Actively tries to reject the paper and lower confidence.
    """
    
    def __init__(self, gemini: GeminiClient):
        self.gemini = gemini
    
    async def adversarial_review(
        self,
        state: AgentState
    ) -> Dict[str, Any]:
        """
        Perform adversarial review trying to find flaws.
        
        Args:
            state: Current agent state
            
        Returns:
            Adversarial review results
        """
        summary = state.get_summary()
        
        prompt = f"""You are now an ADVERSARIAL REVIEWER. Your job is to find flaws and reject this paper.

Paper: {state.paper.title}
Abstract: {state.paper.abstract}

Current Review State:
- Claims: {summary['claims_count']}
- Issues: {summary['issues_found']}

Claims:
{self._format_claims(state)}

Issues Already Found:
{self._format_issues(state)}

**Your adversarial goal: Find reasons to REJECT this paper.**

Look for:
1. Fatal flaws in proofs or methodology
2. Overclaimed results
3. Missing baselines or comparisons
4. Insufficient novelty
5. Questionable assumptions
6. Statistical issues
7. Reproducibility concerns

Be aggressive. What are the STRONGEST arguments for rejection?

Respond with JSON:
{{
    "fatal_flaws": ["flaw1", "flaw2"],
    "overclaimed_results": ["claim_id1", "claim_id2"],
    "missing_elements": ["element1", "element2"],
    "recommended_action": "reject/major_revision/minor_revision",
    "adversarial_confidence": 0.0-1.0,
    "strongest_rejection_argument": "the most compelling reason to reject"
}}"""
        
        schema = {
            "type": "object",
            "properties": {
                "fatal_flaws": {"type": "array", "items": {"type": "string"}},
                "overclaimed_results": {"type": "array", "items": {"type": "string"}},
                "missing_elements": {"type": "array", "items": {"type": "string"}},
                "recommended_action": {"type": "string"},
                "adversarial_confidence": {"type": "number"},
                "strongest_rejection_argument": {"type": "string"}
            }
        }
        
        response = await self.gemini.generate_structured_output(
            prompt, schema, thinking_level="high"
        )
        
        # Create critical issues for fatal flaws
        for flaw in response.get("fatal_flaws", []):
            issue = ReviewIssue(
                issue_id=f"adversarial_{len(state.issues_found)}",
                severity=Severity.CRITICAL,
                issue_type="logical_gap",
                description=f"Adversarial review found: {flaw}",
                location="overall paper",
                suggested_resolution="Address this critical flaw",
                affects_validity=True,
                confidence_in_issue=response.get("adversarial_confidence", 0.8)
            )
            state.add_issue(issue)
        
        # Lower confidence for overclaimed results
        for claim_id in response.get("overclaimed_results", []):
            if claim_id in state.epistemic_ledger.current_claims:
                current = state.epistemic_ledger.current_claims[claim_id]
                # Significantly lower confidence
                new_conf = current.confidence * 0.5
                state.update_claim(claim_id, {
                    "confidence": new_conf,
                    "status": ClaimStatus.QUESTIONED
                })
        
        return {
            "fatal_flaws": response.get("fatal_flaws", []),
            "overclaimed_results": response.get("overclaimed_results", []),
            "missing_elements": response.get("missing_elements", []),
            "adversarial_recommendation": response.get("recommended_action", "major_revision"),
            "adversarial_confidence": response.get("adversarial_confidence", 0.8),
            "strongest_argument": response.get("strongest_rejection_argument", "")
        }
    
    def _format_claims(self, state: AgentState) -> str:
        """Format all claims for adversarial review."""
        claims = list(state.epistemic_ledger.current_claims.values())
        if not claims:
            return "No claims extracted"
        return "\n".join([
            f"- {c.claim_id} ({c.claim_type}): {c.content[:150]} [confidence: {c.confidence:.2f}]"
            for c in claims[:10]  # Limit to 10 most important
        ])
    
    def _format_issues(self, state: AgentState) -> str:
        """Format all issues for adversarial review."""
        if not state.issues_found:
            return "No issues found yet"
        return "\n".join([
            f"- {i.severity.value}: {i.description[:100]}"
            for i in state.issues_found[:10]
        ])


class ConfidenceRecalibrator:
    """
    Recalibrates confidence scores based on evidence and critique.
    Ensures confidence reflects true uncertainty.
    """
    
    def __init__(self, gemini: GeminiClient):
        self.gemini = gemini
    
    async def recalibrate_confidence(
        self,
        state: AgentState,
        self_review_results: Dict[str, Any],
        adversarial_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recalibrate all confidence scores based on critique.
        
        Args:
            state: Current agent state
            self_review_results: Results from self-review
            adversarial_results: Results from adversarial review
            
        Returns:
            Recalibration results
        """
        claims = list(state.epistemic_ledger.current_claims.values())
        
        recalibrations = []
        
        for claim in claims:
            # Calculate recalibrated confidence
            new_conf = await self._recalibrate_single_claim(
                claim, state, self_review_results, adversarial_results
            )
            
            if abs(new_conf - claim.epistemic_state.confidence) > 0.05:
                old_conf = claim.epistemic_state.confidence
                state.update_claim(claim.claim_id, {"confidence": new_conf})
                
                recalibrations.append({
                    "claim_id": claim.claim_id,
                    "old_confidence": old_conf,
                    "new_confidence": new_conf,
                    "change": new_conf - old_conf
                })
        
        # Global confidence adjustment based on critique severity
        global_adjustment = self._calculate_global_adjustment(
            self_review_results, adversarial_results
        )
        
        return {
            "recalibrations": recalibrations,
            "total_claims_adjusted": len(recalibrations),
            "global_adjustment_factor": global_adjustment,
            "average_confidence_change": sum(r["change"] for r in recalibrations) / len(recalibrations) if recalibrations else 0
        }
    
    async def _recalibrate_single_claim(
        self,
        claim: Claim,
        state: AgentState,
        self_review: Dict[str, Any],
        adversarial: Dict[str, Any]
    ) -> float:
        """Recalibrate confidence for a single claim."""
        base_conf = claim.epistemic_state.confidence
        
        # Factor 1: Self-review identified as overconfident
        if claim.claim_id in self_review.get("overconfident_claims", []):
            base_conf *= 0.7
        
        # Factor 2: Adversarial review flagged as overclaimed
        if claim.claim_id in adversarial.get("overclaimed_results", []):
            base_conf *= 0.5
        
        # Factor 3: Number of issues affecting this claim
        related_issues = [
            i for i in state.issues_found
            if i.claim_id == claim.claim_id
        ]
        if related_issues:
            # Each issue lowers confidence
            issue_penalty = 0.1 * len(related_issues)
            base_conf *= (1 - min(issue_penalty, 0.5))
        
        # Factor 4: Evidence quality
        evidence_multiplier = {
            "strong": 1.0,
            "moderate": 0.9,
            "weak": 0.7,
            "none": 0.5
        }
        base_conf *= evidence_multiplier.get(claim.epistemic_state.evidence_quality, 0.8)
        
        # Factor 5: Uncertainty sources
        if len(claim.epistemic_state.uncertainty_sources) > 2:
            base_conf *= 0.8
        
        # Ensure confidence stays in [0, 1]
        return max(0.0, min(1.0, base_conf))
    
    def _calculate_global_adjustment(
        self,
        self_review: Dict[str, Any],
        adversarial: Dict[str, Any]
    ) -> float:
        """Calculate global confidence adjustment factor."""
        # Start at 1.0 (no adjustment)
        adjustment = 1.0
        
        # Reduce based on missed aspects
        missed_count = len(self_review.get("missed_aspects", []))
        if missed_count > 0:
            adjustment *= (1 - 0.05 * missed_count)
        
        # Reduce based on fatal flaws
        flaw_count = len(adversarial.get("fatal_flaws", []))
        if flaw_count > 0:
            adjustment *= (1 - 0.1 * flaw_count)
        
        # Reduce based on adversarial confidence
        adv_conf = adversarial.get("adversarial_confidence", 0.5)
        if adv_conf > 0.7:
            adjustment *= 0.85
        
        return max(0.5, adjustment)  # Never reduce below 0.5


class CritiqueIntegrator:
    """
    Integrates self-critique and adversarial review into final recommendation.
    Ensures critique meaningfully affects the output.
    """
    
    def __init__(self, gemini: GeminiClient):
        self.gemini = gemini
    
    async def integrate_critique(
        self,
        state: AgentState,
        initial_recommendation: str,
        initial_confidence: float,
        self_review: Dict[str, Any],
        adversarial: Dict[str, Any],
        recalibration: Dict[str, Any]
    ) -> Tuple[str, float, str]:
        """
        Integrate critique into final recommendation.
        
        Args:
            state: Current agent state
            initial_recommendation: Initial recommendation before critique
            initial_confidence: Initial confidence before critique
            self_review: Self-review results
            adversarial: Adversarial review results
            recalibration: Recalibration results
            
        Returns:
            (final_recommendation, final_confidence, justification)
        """
        summary = state.get_summary()
        
        prompt = f"""Integrate self-critique and adversarial review into final recommendation.

Initial Assessment:
- Recommendation: {initial_recommendation}
- Confidence: {initial_confidence:.2f}

Self-Critique Found:
- Missed aspects: {len(self_review.get('missed_aspects', []))}
- Overconfident claims: {len(self_review.get('overconfident_claims', []))}
- Assessment: {self_review.get('self_assessment', 'N/A')}

Adversarial Review Found:
- Fatal flaws: {len(adversarial.get('fatal_flaws', []))}
- Adversarial recommendation: {adversarial.get('adversarial_recommendation', 'N/A')}
- Strongest argument: {adversarial.get('strongest_argument', 'N/A')}

Confidence Recalibration:
- Claims adjusted: {recalibration.get('total_claims_adjusted', 0)}
- Average change: {recalibration.get('average_confidence_change', 0):.2f}

Current Issues: {summary['issues_found']}

Should the recommendation change based on critique?
Should confidence be lowered?

Respond with JSON:
{{
    "final_recommendation": "accept/minor_revision/major_revision/reject",
    "final_confidence": 0.0-1.0,
    "changed_from_initial": true/false,
    "justification": "why this is the final decision",
    "critique_impact": "how critique affected the decision"
}}"""
        
        schema = {
            "type": "object",
            "properties": {
                "final_recommendation": {"type": "string"},
                "final_confidence": {"type": "number"},
                "changed_from_initial": {"type": "boolean"},
                "justification": {"type": "string"},
                "critique_impact": {"type": "string"}
            }
        }
        
        response = await self.gemini.generate_structured_output(
            prompt, schema, thinking_level="high"
        )
        
        final_rec = response.get("final_recommendation", initial_recommendation)
        final_conf = response.get("final_confidence", initial_confidence)
        
        # Ensure confidence is lowered if critique found issues
        if (len(adversarial.get("fatal_flaws", [])) > 0 or 
            len(self_review.get("missed_aspects", [])) > 2):
            # Force confidence reduction
            final_conf = min(final_conf, initial_confidence * 0.8)
        
        justification = f"{response.get('justification', '')} | Critique impact: {response.get('critique_impact', '')}"
        
        return final_rec, final_conf, justification