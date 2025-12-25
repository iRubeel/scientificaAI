"""
Review Logic Modules - Deep analysis components for paper review.

Each module accepts AgentState, performs analysis, and updates state with
claims, issues, and confidence scores.
"""

from typing import List, Dict, Any, Optional, Set
from datetime import datetime

from app.core.gemini import GeminiClient
from app.core.state import AgentState, Belief
from app.models.review_models import (
    Claim, ReviewIssue, ClaimStatus, Severity, ReasoningStep, ToolCall
)


class ClaimExtractor:
    """
    Extracts and tracks mathematical/statistical claims from papers.
    Updates confidence scores based on evidence and dependencies.
    """
    
    def __init__(self, gemini: GeminiClient):
        self.gemini = gemini
    
    async def extract_claims(
        self,
        state: AgentState,
        section: str = "all"
    ) -> List[Claim]:
        """
        Extract claims from paper with dependency tracking.
        
        Args:
            state: Current agent state
            section: Section to analyze
            
        Returns:
            List of extracted claims
        """
        text = self._get_text_for_section(state.paper, section)
        
        prompt = f"""Extract mathematical and statistical claims from this paper.

Paper: {state.paper.title}
Section: {section}
Text: {text[:3000]}

For each claim, identify:
1. The claim content
2. Type (theorem/lemma/proposition/assumption/result/methodology)
3. Dependencies on other claims
4. Initial confidence (0.0-1.0) based on:
   - Clarity of statement
   - Presence of proof/evidence
   - Strength of assumptions

Respond with JSON:
{{
    "claims": [
        {{
            "claim_id": "unique_id",
            "content": "the claim",
            "claim_type": "theorem/lemma/...",
            "section": "section name",
            "page_number": null or number,
            "dependencies": ["claim_id1", "claim_id2"],
            "initial_confidence": 0.0-1.0,
            "evidence_quality": "strong/moderate/weak/none",
            "uncertainty_sources": ["source1", "source2"]
        }}
    ]
}}"""
        
        schema = {
            "type": "object",
            "properties": {
                "claims": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "claim_id": {"type": "string"},
                            "content": {"type": "string"},
                            "claim_type": {"type": "string"},
                            "section": {"type": "string"},
                            "page_number": {"type": ["integer", "null"]},
                            "dependencies": {"type": "array", "items": {"type": "string"}},
                            "initial_confidence": {"type": "number"},
                            "evidence_quality": {"type": "string"},
                            "uncertainty_sources": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            }
        }
        
        response = await self.gemini.generate_structured_output(
            prompt, schema, thinking_level="high"
        )
        
        claims = []
        for claim_data in response["claims"]:
            claim = Claim(
                claim_id=claim_data["claim_id"],
                content=claim_data["content"],
                claim_type=claim_data["claim_type"],
                section=claim_data["section"],
                page_number=claim_data.get("page_number"),
                status=ClaimStatus.IDENTIFIED,
                confidence=claim_data["initial_confidence"],
                evidence_quality=claim_data["evidence_quality"],
                uncertainty_sources=claim_data["uncertainty_sources"],
                dependencies=claim_data["dependencies"]
            )
            
            # Add to state
            state.add_claim(claim)
            claims.append(claim)
        
        return claims
    
    def _get_text_for_section(self, paper, section: str) -> str:
        """Get text for specific section."""
        if section == "all":
            return paper.full_text if paper.full_text else paper.abstract
        # Simplified - in production, parse sections from full_text
        return paper.abstract


class ProofDependencyAnalyzer:
    """
    Analyzes proof dependencies and propagates confidence through claim graph.
    Detects circular dependencies and unsupported claims.
    """
    
    def __init__(self, gemini: GeminiClient):
        self.gemini = gemini
    
    async def analyze_dependencies(
        self,
        state: AgentState
    ) -> List[ReviewIssue]:
        """
        Analyze proof dependencies and update confidence scores.
        
        Args:
            state: Current agent state
            
        Returns:
            List of issues found
        """
        issues = []
        claims = list(state.epistemic_ledger.current_claims.values())
        
        if not claims:
            return issues
        
        # Build dependency graph
        dep_graph = self._build_dependency_graph(claims)
        
        # Check for circular dependencies
        circular = self._detect_circular_dependencies(dep_graph)
        if circular:
            issue = ReviewIssue(
                issue_id=f"dep_circular_{len(state.issues_found)}",
                severity=Severity.CRITICAL,
                issue_type="logical_gap",
                description=f"Circular dependency detected: {' -> '.join(circular)}",
                location="proof structure",
                affects_validity=True,
                confidence_in_issue=0.95
            )
            issues.append(issue)
            state.add_issue(issue)
        
        # Check for unsupported claims
        unsupported = self._find_unsupported_claims(claims, dep_graph)
        for claim_id in unsupported:
            issue = ReviewIssue(
                issue_id=f"dep_unsupported_{len(state.issues_found)}",
                claim_id=claim_id,
                severity=Severity.MAJOR,
                issue_type="insufficient_evidence",
                description=f"Claim {claim_id} has no supporting evidence or dependencies",
                location=f"claim {claim_id}",
                affects_validity=True,
                confidence_in_issue=0.85
            )
            issues.append(issue)
            state.add_issue(issue)
            
            # Lower confidence for unsupported claims
            state.update_claim(claim_id, {"confidence": 0.3})
        
        # Propagate confidence through dependency graph
        await self._propagate_confidence(state, dep_graph)
        
        return issues
    
    def _build_dependency_graph(self, claims: List[Claim]) -> Dict[str, Set[str]]:
        """Build dependency graph from claims."""
        graph = {}
        for claim in claims:
            graph[claim.claim_id] = set(claim.dependencies)
        return graph
    
    def _detect_circular_dependencies(self, graph: Dict[str, Set[str]]) -> Optional[List[str]]:
        """Detect circular dependencies using DFS."""
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    result = dfs(neighbor, path + [neighbor])
                    if result:
                        return result
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
            
            rec_stack.remove(node)
            return None
        
        for node in graph:
            if node not in visited:
                cycle = dfs(node, [node])
                if cycle:
                    return cycle
        
        return None
    
    def _find_unsupported_claims(
        self,
        claims: List[Claim],
        graph: Dict[str, Set[str]]
    ) -> List[str]:
        """Find claims with no evidence or dependencies."""
        unsupported = []
        for claim in claims:
            # Check if claim has dependencies or is an assumption
            if not claim.dependencies and claim.claim_type not in ["assumption"]:
                # Check if it has weak evidence
                if claim.epistemic_state.evidence_quality in ["weak", "none"]:
                    unsupported.append(claim.claim_id)
        return unsupported
    
    async def _propagate_confidence(
        self,
        state: AgentState,
        graph: Dict[str, Set[str]]
    ) -> None:
        """Propagate confidence through dependency graph."""
        claims = state.epistemic_ledger.current_claims
        
        # Topological sort to process in dependency order
        sorted_claims = self._topological_sort(graph)
        
        for claim_id in sorted_claims:
            if claim_id not in claims:
                continue
            
            claim = claims[claim_id]
            
            # If claim has dependencies, adjust confidence based on them
            if claim.dependencies:
                dep_confidences = [
                    claims[dep_id].confidence
                    for dep_id in claim.dependencies
                    if dep_id in claims
                ]
                
                if dep_confidences:
                    # Confidence is limited by weakest dependency
                    min_dep_confidence = min(dep_confidences)
                    avg_dep_confidence = sum(dep_confidences) / len(dep_confidences)
                    
                    # New confidence is weighted combination
                    new_confidence = 0.3 * claim.epistemic_state.confidence + 0.5 * avg_dep_confidence + 0.2 * min_dep_confidence
                    
                    # Only update if confidence changed significantly
                    if abs(new_confidence - claim.epistemic_state.confidence) > 0.05:
                        state.update_claim(claim_id, {"confidence": new_confidence})
    
    def _topological_sort(self, graph: Dict[str, Set[str]]) -> List[str]:
        """Topological sort of dependency graph."""
        in_degree = {node: 0 for node in graph}
        for node in graph:
            for neighbor in graph[node]:
                if neighbor in in_degree:
                    in_degree[neighbor] += 1
        
        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for neighbor in graph.get(node, set()):
                if neighbor in in_degree:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        return result


class AssumptionAuditor:
    """
    Audits mathematical and statistical assumptions.
    Flags unstated, violated, or questionable assumptions.
    """
    
    def __init__(self, gemini: GeminiClient):
        self.gemini = gemini
    
    async def audit_assumptions(
        self,
        state: AgentState
    ) -> List[ReviewIssue]:
        """
        Audit assumptions in claims and methodology.
        
        Args:
            state: Current agent state
            
        Returns:
            List of assumption-related issues
        """
        issues = []
        claims = list(state.epistemic_ledger.current_claims.values())
        
        # Extract assumption claims
        assumption_claims = [c for c in claims if c.claim_type == "assumption"]
        result_claims = [c for c in claims if c.claim_type in ["theorem", "result"]]
        
        # Check for unstated assumptions
        for claim in result_claims:
            unstated = await self._check_unstated_assumptions(claim, state)
            if unstated:
                issue = ReviewIssue(
                    issue_id=f"assume_unstated_{len(state.issues_found)}",
                    claim_id=claim.claim_id,
                    severity=Severity.MAJOR,
                    issue_type="assumption_violation",
                    description=f"Claim may rely on unstated assumptions: {', '.join(unstated)}",
                    location=claim.section,
                    suggested_resolution="Explicitly state all assumptions",
                    affects_validity=True,
                    confidence_in_issue=0.75
                )
                issues.append(issue)
                state.add_issue(issue)
                
                # Lower confidence
                state.update_claim(claim.claim_id, {
                    "confidence": claim.epistemic_state.confidence * 0.8,
                    "uncertainty_sources": claim.epistemic_state.uncertainty_sources + ["unstated assumptions"]
                })
        
        # Check statistical assumptions
        stats_issues = await self._audit_statistical_assumptions(state)
        issues.extend(stats_issues)
        
        return issues
    
    async def _check_unstated_assumptions(
        self,
        claim: Claim,
        state: AgentState
    ) -> List[str]:
        """Check for unstated assumptions in a claim."""
        prompt = f"""Analyze this mathematical/statistical claim for unstated assumptions.

Claim: {claim.content}
Type: {claim.claim_type}

What assumptions might this claim rely on that are not explicitly stated?
Consider:
- Regularity conditions
- Domain restrictions
- Statistical assumptions (normality, independence, etc.)
- Existence/uniqueness assumptions

Respond with JSON:
{{
    "unstated_assumptions": ["assumption1", "assumption2", ...]
}}"""
        
        schema = {
            "type": "object",
            "properties": {
                "unstated_assumptions": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        response = await self.gemini.generate_structured_output(
            prompt, schema, thinking_level="high"
        )
        
        return response["unstated_assumptions"]
    
    async def _audit_statistical_assumptions(
        self,
        state: AgentState
    ) -> List[ReviewIssue]:
        """Audit statistical assumptions using stats tool."""
        issues = []
        
        # Check if paper uses statistical methods
        paper_text = state.paper.abstract.lower()
        has_stats = any(word in paper_text for word in [
            "statistical", "hypothesis", "regression", "correlation",
            "p-value", "significance", "test", "sample"
        ])
        
        if not has_stats:
            return issues
        
        # Use stats tool to audit
        # Simplified - in production, extract actual test parameters
        from app.tools.stats import StatisticalTool
        stats_tool = StatisticalTool()
        
        audit_result = await stats_tool.audit_statistical_test(
            test_type="t-test",  # Would extract from paper
            sample_size=50,  # Would extract from paper
            assumptions=["normality", "independence"],
            p_value=0.045
        )
        
        if not audit_result.get("success"):
            return issues
        
        # Create issues for violations
        for violation in audit_result.get("violations", []):
            issue = ReviewIssue(
                issue_id=f"stats_assume_{len(state.issues_found)}",
                severity=Severity.MAJOR if violation["severity"] == "high" else Severity.MODERATE,
                issue_type="statistical_error",
                description=violation["message"],
                location="statistical analysis",
                affects_validity=True,
                confidence_in_issue=0.85
            )
            issues.append(issue)
            state.add_issue(issue)
        
        return issues


class BoundaryTester:
    """
    Tests boundary cases and edge conditions.
    Identifies potential counterexamples and failure modes.
    """
    
    def __init__(self, gemini: GeminiClient):
        self.gemini = gemini
    
    async def test_boundaries(
        self,
        state: AgentState
    ) -> List[ReviewIssue]:
        """
        Test boundary cases for claims.
        
        Args:
            state: Current agent state
            
        Returns:
            List of boundary-related issues
        """
        issues = []
        claims = list(state.epistemic_ledger.current_claims.values())
        
        for claim in claims:
            if claim.claim_type in ["theorem", "result"]:
                # Identify boundary cases
                boundaries = await self._identify_boundary_cases(claim)
                
                # Test each boundary
                for boundary in boundaries:
                    counterexample = await self._test_boundary(claim, boundary, state)
                    
                    if counterexample:
                        issue = ReviewIssue(
                            issue_id=f"boundary_{len(state.issues_found)}",
                            claim_id=claim.claim_id,
                            severity=Severity.CRITICAL,
                            issue_type="alternative_interpretation",
                            description=f"Potential counterexample at boundary: {boundary}",
                            location=claim.section,
                            suggested_resolution=f"Check boundary case: {counterexample}",
                            affects_validity=True,
                            confidence_in_issue=0.7
                        )
                        issues.append(issue)
                        state.add_issue(issue)
                        
                        # Significantly lower confidence
                        state.update_claim(claim.claim_id, {
                            "confidence": 0.2,
                            "status": ClaimStatus.QUESTIONED
                        })
        
        return issues
    
    async def _identify_boundary_cases(self, claim: Claim) -> List[str]:
        """Identify boundary cases for a claim."""
        prompt = f"""Identify boundary cases and edge conditions for this claim.

Claim: {claim.content}

What are the boundary cases where this claim might fail?
Consider:
- Zero/infinity
- Empty sets
- Degenerate cases
- Limit cases
- Domain boundaries

Respond with JSON:
{{
    "boundary_cases": ["case1", "case2", ...]
}}"""
        
        schema = {
            "type": "object",
            "properties": {
                "boundary_cases": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        response = await self.gemini.generate_structured_output(
            prompt, schema, thinking_level="high"
        )
        
        return response["boundary_cases"][:3]  # Limit to 3 most important
    
    async def _test_boundary(
        self,
        claim: Claim,
        boundary: str,
        state: AgentState
    ) -> Optional[str]:
        """Test a specific boundary case."""
        # Use symbolic tool if claim contains equations
        if any(char in claim.content for char in ["=", "<", ">"]):
            from app.tools.symbolic import SymbolicMathTool
            symbolic_tool = SymbolicMathTool()
            
            # Try to find counterexample
            # Simplified - would extract actual variables and expressions
            result = await symbolic_tool.find_counterexample(
                claim="x**2 > 0",  # Would extract from claim
                variables=["x"],
                domain="integers"
            )
            
            if result.get("counterexample_found"):
                return str(result["counterexamples"][0])
        
        return None


class NoveltySkeptic:
    """
    Applies skepticism to novelty claims.
    Searches literature and assesses true contribution.
    """
    
    def __init__(self, gemini: GeminiClient):
        self.gemini = gemini
    
    async def assess_novelty(
        self,
        state: AgentState
    ) -> List[ReviewIssue]:
        """
        Assess novelty of contributions with skepticism.
        
        Args:
            state: Current agent state
            
        Returns:
            List of novelty-related issues
        """
        issues = []
        claims = list(state.epistemic_ledger.current_claims.values())
        
        # Focus on result claims
        result_claims = [c for c in claims if c.claim_type in ["result", "theorem"]]
        
        for claim in result_claims:
            # Search literature
            novelty_assessment = await self._deep_novelty_check(claim, state)
            
            if novelty_assessment["novelty_level"] == "low":
                issue = ReviewIssue(
                    issue_id=f"novelty_{len(state.issues_found)}",
                    claim_id=claim.claim_id,
                    severity=Severity.MAJOR,
                    issue_type="insufficient_evidence",
                    description=f"Low novelty: {novelty_assessment['explanation']}",
                    location=claim.section,
                    suggested_resolution="Clarify novel contribution vs. existing work",
                    affects_validity=False,
                    confidence_in_issue=novelty_assessment["confidence"]
                )
                issues.append(issue)
                state.add_issue(issue)
                
                # Lower confidence for low-novelty claims
                state.update_claim(claim.claim_id, {
                    "confidence": claim.epistemic_state.confidence * 0.6
                })
            
            elif novelty_assessment["novelty_level"] == "moderate":
                # Create belief about incremental contribution
                belief = Belief(
                    belief_id=f"novelty_belief_{len(state.beliefs)}",
                    content=f"Claim {claim.claim_id} appears to be incremental: {novelty_assessment['explanation']}",
                    confidence=0.7,
                    supporting_evidence=[f"Found {novelty_assessment['similar_papers_count']} similar papers"]
                )
                state.add_belief(belief)
        
        return issues
    
    async def _deep_novelty_check(
        self,
        claim: Claim,
        state: AgentState
    ) -> Dict[str, Any]:
        """Perform deep novelty check using literature tool."""
        from app.tools.literature import LiteratureTool
        lit_tool = LiteratureTool()
        
        # Search for similar work
        result = await lit_tool.assess_novelty(
            claim=claim.content,
            context=state.paper.abstract
        )
        
        if not result.get("success"):
            return {
                "novelty_level": "unknown",
                "confidence": 0.5,
                "explanation": "Could not assess novelty",
                "similar_papers_count": 0
            }
        
        # Enhanced skepticism - be more critical
        novelty_level = result["novelty_level"]
        similar_count = result["similar_papers_count"]
        
        # Apply skeptical adjustment
        if similar_count > 3:
            novelty_level = "low"
        elif similar_count > 1 and novelty_level == "high":
            novelty_level = "moderate"
        
        return {
            "novelty_level": novelty_level,
            "confidence": result["confidence"],
            "explanation": result["explanation"],
            "similar_papers_count": similar_count
        }


class ReviewerSmellDetector:
    """
    Detects "reviewer smells" - red flags in papers.
    Patterns that suggest problems with rigor, honesty, or quality.
    """
    
    def __init__(self, gemini: GeminiClient):
        self.gemini = gemini
    
    async def detect_smells(
        self,
        state: AgentState
    ) -> List[ReviewIssue]:
        """
        Detect reviewer smells in paper.
        
        Args:
            state: Current agent state
            
        Returns:
            List of smell-related issues
        """
        issues = []
        
        # Check for various smells
        smells = []
        
        # 1. P-hacking indicators
        p_hack_smell = await self._check_p_hacking(state)
        if p_hack_smell:
            smells.append(p_hack_smell)
        
        # 2. Cherry-picking evidence
        cherry_pick_smell = await self._check_cherry_picking(state)
        if cherry_pick_smell:
            smells.append(cherry_pick_smell)
        
        # 3. Overclaiming
        overclaim_smell = await self._check_overclaiming(state)
        if overclaim_smell:
            smells.append(overclaim_smell)
        
        # 4. Missing error analysis
        error_smell = await self._check_missing_error_analysis(state)
        if error_smell:
            smells.append(error_smell)
        
        # 5. Vague methodology
        vague_smell = await self._check_vague_methodology(state)
        if vague_smell:
            smells.append(vague_smell)
        
        # Create issues for detected smells
        for smell in smells:
            issue = ReviewIssue(
                issue_id=f"smell_{len(state.issues_found)}",
                severity=smell["severity"],
                issue_type=smell["type"],
                description=f"Reviewer smell detected: {smell['description']}",
                location=smell["location"],
                suggested_resolution=smell["resolution"],
                affects_validity=smell["affects_validity"],
                confidence_in_issue=smell["confidence"]
            )
            issues.append(issue)
            state.add_issue(issue)
        
        return issues
    
    async def _check_p_hacking(self, state: AgentState) -> Optional[Dict[str, Any]]:
        """Check for p-hacking indicators."""
        paper_text = (state.paper.abstract + " " + (state.paper.full_text or "")).lower()
        
        # Indicators
        has_p_value = "p = 0.04" in paper_text or "p=0.04" in paper_text
        has_borderline = any(p in paper_text for p in ["p = 0.049", "p=0.049", "p < 0.05"])
        multiple_tests = paper_text.count("p-value") > 3 or paper_text.count("p =") > 3
        
        if has_p_value or (has_borderline and multiple_tests):
            return {
                "severity": Severity.MAJOR,
                "type": "statistical_error",
                "description": "Borderline p-values suggest possible p-hacking",
                "location": "statistical results",
                "resolution": "Report all tests performed, use correction for multiple comparisons",
                "affects_validity": True,
                "confidence": 0.7
            }
        
        return None
    
    async def _check_cherry_picking(self, state: AgentState) -> Optional[Dict[str, Any]]:
        """Check for cherry-picking evidence."""
        claims = list(state.epistemic_ledger.current_claims.values())
        
        # Check if all results are positive
        result_claims = [c for c in claims if c.claim_type == "result"]
        if len(result_claims) >= 3:
            # All positive results is suspicious
            return {
                "severity": Severity.MODERATE,
                "type": "insufficient_evidence",
                "description": "All reported results are positive - possible cherry-picking",
                "location": "results section",
                "resolution": "Report negative results and failed approaches",
                "affects_validity": False,
                "confidence": 0.6
            }
        
        return None
    
    async def _check_overclaiming(self, state: AgentState) -> Optional[Dict[str, Any]]:
        """Check for overclaiming."""
        paper_text = state.paper.abstract.lower()
        
        # Overclaim indicators
        strong_words = ["revolutionary", "breakthrough", "unprecedented", "proves definitively"]
        has_overclaim = any(word in paper_text for word in strong_words)
        
        if has_overclaim:
            return {
                "severity": Severity.MINOR,
                "type": "alternative_interpretation",
                "description": "Abstract contains strong claims that may be overstated",
                "location": "abstract",
                "resolution": "Moderate language and provide caveats",
                "affects_validity": False,
                "confidence": 0.75
            }
        
        return None
    
    async def _check_missing_error_analysis(self, state: AgentState) -> Optional[Dict[str, Any]]:
        """Check for missing error analysis."""
        paper_text = (state.paper.abstract + " " + (state.paper.full_text or "")).lower()
        
        # Check if paper has numerical results but no error bars
        has_numerical = any(word in paper_text for word in ["accuracy", "error rate", "performance"])
        has_error_analysis = any(word in paper_text for word in [
            "confidence interval", "standard error", "error bar", "uncertainty"
        ])
        
        if has_numerical and not has_error_analysis:
            return {
                "severity": Severity.MAJOR,
                "type": "insufficient_evidence",
                "description": "Numerical results reported without error analysis",
                "location": "results",
                "resolution": "Provide confidence intervals or error estimates",
                "affects_validity": True,
                "confidence": 0.8
            }
        
        return None
    
    async def _check_vague_methodology(self, state: AgentState) -> Optional[Dict[str, Any]]:
        """Check for vague methodology."""
        # Check if methodology claims exist
        claims = list(state.epistemic_ledger.current_claims.values())
        method_claims = [c for c in claims if c.claim_type == "methodology"]
        
        if not method_claims and len(claims) > 0:
            return {
                "severity": Severity.MODERATE,
                "type": "methodological_flaw",
                "description": "Methodology not clearly described",
                "location": "methods",
                "resolution": "Provide detailed methodology section",
                "affects_validity": True,
                "confidence": 0.65
            }
        
        return None
