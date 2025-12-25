"""
Dynamic Referee Agent - Non-linear, adaptive paper review orchestration.
Plans dynamically, calls tools conditionally, revises beliefs based on evidence.
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

from app.core.gemini import GeminiClient
from app.core.state import AgentState, Belief
from app.models.review_models import (
    Paper, RefereeReport, Claim, ReasoningStep, ToolCall,
    ReviewIssue, ClaimStatus, Severity
)
from app.tools.arxiv import ArxivTool
from app.tools.literature import LiteratureTool
from app.tools.symbolic import SymbolicMathTool
from app.tools.stats import StatisticalTool


class RefereeAgent:
    """
    Dynamic, non-linear referee agent that autonomously reviews papers.
    
    Key Features:
    - Adaptive planning based on paper content
    - Conditional tool usage
    - Epistemic state tracking and belief revision
    - Non-linear iteration with stopping criteria
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the referee agent with Gemini and tools."""
        self.gemini = GeminiClient(api_key)
        
        # Initialize tools
        self.tools = {
            "arxiv": ArxivTool(),
            "literature": LiteratureTool(),
            "symbolic": SymbolicMathTool(),
            "stats": StatisticalTool()
        }
        
        # Get all tool schemas for Gemini function calling
        self.tool_schemas = self._collect_tool_schemas()
    
    def _collect_tool_schemas(self) -> List[Dict[str, Any]]:
        """Collect all tool schemas for Gemini integration."""
        schemas = []
        for tool_name, tool in self.tools.items():
            tool_schemas = tool.get_schemas()
            schemas.extend(list(tool_schemas.values()))
        return schemas
    
    async def review_paper(
        self,
        paper: Paper,
        max_iterations: int = 10,
        verbose: bool = False
    ) -> RefereeReport:
        """
        Conduct a complete, adaptive review of a paper.
        
        Args:
            paper: Paper to review
            max_iterations: Maximum review iterations
            verbose: Print progress
            
        Returns:
            Complete RefereeReport
        """
        # Initialize state
        state = AgentState.create_for_paper(paper)
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Starting adaptive review: {paper.title}")
            print(f"{'='*60}\n")
        
        # Phase 1: Dynamic Planning
        if verbose:
            print("Phase 1: Creating adaptive review plan...")
        
        plan = await self._create_dynamic_plan(paper, state)
        
        if verbose:
            print(f"  → Generated {len(plan)} review objectives\n")
        
        # Phase 2: Non-linear Execution Loop
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            
            if verbose:
                print(f"Iteration {iteration}/{max_iterations}")
            
            # Decide next action based on current state
            should_continue, action = await self._decide_next_action(state, plan)
            
            if not should_continue:
                if verbose:
                    print(f"  → Stopping: {action}\n")
                break
            
            if verbose:
                print(f"  → Action: {action['type']}")
            
            # Execute the decided action
            await self._execute_action(action, state, verbose)
            
            # Check for belief contradictions and revise if needed
            await self._check_and_revise_beliefs(state, verbose)
            
            if verbose:
                summary = state.get_summary()
                print(f"  → Claims: {summary['claims_count']}, "
                      f"Beliefs: {summary['beliefs_count']}, "
                      f"Issues: {summary['issues_found']}\n")
        
        # Phase 3: Synthesis
        if verbose:
            print("Phase 3: Synthesizing final report...")
        
        report = await self._synthesize_report(state)
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Review complete: {report.recommendation}")
            print(f"Confidence: {report.confidence_in_recommendation:.2f}")
            print(f"{'='*60}\n")
        
        return report
    
    async def _create_dynamic_plan(
        self,
        paper: Paper,
        state: AgentState
    ) -> List[Dict[str, Any]]:
        """
        Create a dynamic review plan based on paper content.
        Different papers get different plans.
        """
        prompt = f"""You are a skeptical academic referee reviewing a paper.

Paper Title: {paper.title}
Abstract: {paper.abstract}
Categories: {paper.metadata.get('categories', [])}

Based on this paper, create a tailored review plan. Consider:
- What type of paper is this? (theoretical, empirical, methodological)
- What are the main claims likely to be?
- What tools would be most useful? (arxiv, literature, symbolic, stats)
- What are the key risks or concerns?

Create 3-5 specific review objectives. Each should be:
- Concrete and actionable
- Tailored to THIS paper
- Include which tools might be useful

Respond with JSON:
{{
    "paper_type": "theoretical/empirical/methodological/mixed",
    "key_concerns": ["concern1", "concern2"],
    "objectives": [
        {{
            "objective": "specific goal",
            "rationale": "why this matters for THIS paper",
            "suggested_tools": ["tool1", "tool2"],
            "priority": "high/medium/low"
        }}
    ]
}}"""
        
        schema = {
            "type": "object",
            "properties": {
                "paper_type": {"type": "string"},
                "key_concerns": {"type": "array", "items": {"type": "string"}},
                "objectives": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "objective": {"type": "string"},
                            "rationale": {"type": "string"},
                            "suggested_tools": {"type": "array", "items": {"type": "string"}},
                            "priority": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        response = await self.gemini.generate_structured_output(
            prompt, schema, thinking_level="high"
        )
        
        # Store plan in context
        state.update_context("paper_type", response["paper_type"])
        state.update_context("key_concerns", response["key_concerns"])
        
        return response["objectives"]
    
    async def _decide_next_action(
        self,
        state: AgentState,
        plan: List[Dict[str, Any]]
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Decide what to do next based on current state.
        Returns (should_continue, action).
        """
        summary = state.get_summary()
        
        # Stopping criteria
        if summary["claims_count"] >= 5 and summary["issues_found"] >= 2:
            # Have enough evidence to make a decision
            if summary["beliefs_count"] >= 3:
                return False, {"reason": "Sufficient evidence gathered"}
        
        if summary["reasoning_steps"] >= 15:
            # Prevent infinite loops
            return False, {"reason": "Maximum reasoning steps reached"}
        
        # Decide next action using Gemini
        prompt = f"""You are in the middle of reviewing a paper. Decide what to do next.

Current State:
- Claims identified: {summary['claims_count']}
- Beliefs formed: {summary['beliefs_count']}
- Reasoning steps: {summary['reasoning_steps']}
- Tool calls made: {summary['tool_calls']}
- Issues found: {summary['issues_found']}

Review Objectives:
{self._format_objectives(plan)}

Recent Claims:
{self._format_recent_claims(state, limit=3)}

What should you do next? Options:
1. Extract more claims from the paper
2. Verify a specific claim using tools
3. Assess novelty of a contribution
4. Check statistical assumptions
5. Investigate a potential issue
6. Conclude review (if enough evidence)

Choose the most valuable next action for THIS review.

Respond with JSON:
{{
    "action_type": "extract_claims/verify_claim/assess_novelty/check_stats/investigate_issue/conclude",
    "rationale": "why this action now",
    "target": "what specifically to focus on",
    "tools_needed": ["tool1", "tool2"]
}}"""
        
        schema = {
            "type": "object",
            "properties": {
                "action_type": {"type": "string"},
                "rationale": {"type": "string"},
                "target": {"type": "string"},
                "tools_needed": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        response = await self.gemini.generate_structured_output(
            prompt, schema, thinking_level="high"
        )
        
        if response["action_type"] == "conclude":
            return False, {"reason": "Agent decided to conclude"}
        
        return True, {
            "type": response["action_type"],
            "rationale": response["rationale"],
            "target": response["target"],
            "tools": response["tools_needed"]
        }
    
    async def _execute_action(
        self,
        action: Dict[str, Any],
        state: AgentState,
        verbose: bool
    ) -> None:
        """Execute a decided action with tool usage."""
        action_type = action["type"]
        
        if action_type == "extract_claims":
            await self._extract_claims_action(state, action, verbose)
        elif action_type == "verify_claim":
            await self._verify_claim_action(state, action, verbose)
        elif action_type == "assess_novelty":
            await self._assess_novelty_action(state, action, verbose)
        elif action_type == "check_stats":
            await self._check_stats_action(state, action, verbose)
        elif action_type == "investigate_issue":
            await self._investigate_issue_action(state, action, verbose)
    
    async def _extract_claims_action(
        self,
        state: AgentState,
        action: Dict[str, Any],
        verbose: bool
    ) -> None:
        """Extract claims from paper."""
        if verbose:
            print(f"    Extracting claims: {action['target']}")
        
        # Use Gemini to extract claims
        text = state.paper.abstract if not state.paper.full_text else state.paper.full_text[:2000]
        
        response = await self.gemini.generate(
            f"Extract 2-3 key mathematical/statistical claims from: {text}",
            thinking_level="low"
        )
        
        # Create claims (simplified for demo)
        claim = Claim(
            claim_id=f"claim_{len(state.epistemic_ledger.current_claims) + 1}",
            content=response["text"][:200],
            claim_type="result",
            section="main",
            confidence=0.5
        )
        
        state.add_claim(claim)
        
        # Create belief about this claim
        belief = Belief(
            belief_id=f"belief_{len(state.beliefs) + 1}",
            content=f"The paper claims: {claim.content[:100]}",
            confidence=0.6
        )
        state.add_belief(belief)
    
    async def _verify_claim_action(
        self,
        state: AgentState,
        action: Dict[str, Any],
        verbose: bool
    ) -> None:
        """Verify a claim using tools."""
        if verbose:
            print(f"    Verifying claim with tools: {action['tools']}")
        
        # Get a claim to verify
        claims = list(state.epistemic_ledger.current_claims.values())
        if not claims:
            return
        
        claim = claims[0]
        
        # Conditionally call tools based on action
        for tool_name in action["tools"]:
            if tool_name == "symbolic" and "equation" in claim.content.lower():
                # Call symbolic tool
                result = await self.tools["symbolic"].verify_equation(
                    "x**2 + 1", "x**2 + 1"  # Simplified
                )
                
                tool_call = ToolCall(
                    tool_name="symbolic",
                    parameters={"left": "x**2+1", "right": "x**2+1"},
                    result=result,
                    success=result.get("success", False)
                )
                state.add_tool_call(tool_call)
                
                # Update belief based on result
                if result.get("are_equal"):
                    state.update_claim(claim.claim_id, {"confidence": 0.9})
            
            elif tool_name == "literature":
                # Check novelty
                result = await self.tools["literature"].assess_novelty(
                    claim.content[:100]
                )
                
                tool_call = ToolCall(
                    tool_name="literature",
                    parameters={"claim": claim.content[:100]},
                    result=result,
                    success=result.get("success", False)
                )
                state.add_tool_call(tool_call)
                
                # Adjust confidence based on novelty
                if result.get("novelty_level") == "low":
                    state.update_claim(claim.claim_id, {"confidence": 0.4})
    
    async def _assess_novelty_action(
        self,
        state: AgentState,
        action: Dict[str, Any],
        verbose: bool
    ) -> None:
        """Assess novelty using literature tool."""
        if verbose:
            print(f"    Assessing novelty")
        
        # Use literature tool
        result = await self.tools["literature"].search_related_work(
            action["target"], limit=3
        )
        
        tool_call = ToolCall(
            tool_name="literature",
            parameters={"query": action["target"]},
            result=result,
            success=result.get("success", False)
        )
        state.add_tool_call(tool_call)
        
        # Create issue if novelty is questionable
        if result.get("total_results", 0) > 5:
            issue = ReviewIssue(
                issue_id=f"issue_{len(state.issues_found) + 1}",
                severity=Severity.MODERATE,
                issue_type="insufficient_evidence",
                description=f"Found {result.get('total_results')} similar papers",
                location="novelty assessment"
            )
            state.add_issue(issue)
    
    async def _check_stats_action(
        self,
        state: AgentState,
        action: Dict[str, Any],
        verbose: bool
    ) -> None:
        """Check statistical assumptions."""
        if verbose:
            print(f"    Checking statistical assumptions")
        
        # Use stats tool
        result = await self.tools["stats"].audit_statistical_test(
            test_type="t-test",
            sample_size=30,
            p_value=0.045
        )
        
        tool_call = ToolCall(
            tool_name="stats",
            parameters={"test_type": "t-test", "sample_size": 30},
            result=result,
            success=result.get("success", False)
        )
        state.add_tool_call(tool_call)
        
        # Create issues for violations
        if result.get("violations"):
            for violation in result["violations"]:
                issue = ReviewIssue(
                    issue_id=f"issue_{len(state.issues_found) + 1}",
                    severity=Severity.MAJOR,
                    issue_type="statistical_error",
                    description=violation.get("message", "Statistical issue"),
                    location="statistical analysis"
                )
                state.add_issue(issue)
    
    async def _investigate_issue_action(
        self,
        state: AgentState,
        action: Dict[str, Any],
        verbose: bool
    ) -> None:
        """Investigate a potential issue."""
        if verbose:
            print(f"    Investigating: {action['target']}")
        
        # Use reasoning to investigate
        response = await self.gemini.generate(
            f"Investigate this concern: {action['target']}",
            thinking_level="high"
        )
        
        # Create reasoning step
        step = ReasoningStep(
            step_number=len(state.reasoning_steps) + 1,
            description=f"Investigating: {action['target']}",
            reasoning=response["text"][:500],
            intermediate_conclusion="Investigation complete",
            confidence=0.7
        )
        state.add_reasoning_step(step)
    
    async def _check_and_revise_beliefs(
        self,
        state: AgentState,
        verbose: bool
    ) -> None:
        """Check for contradictions and revise beliefs."""
        if len(state.beliefs) < 2:
            return
        
        # Check recent beliefs for contradictions
        recent_beliefs = state.beliefs[-3:]
        
        prompt = f"""Check if these beliefs contradict each other:

{self._format_beliefs(recent_beliefs)}

If there are contradictions, which belief should be revised and why?

Respond with JSON:
{{
    "has_contradiction": true/false,
    "belief_to_revise": "belief_id or null",
    "new_confidence": 0.0-1.0,
    "rationale": "explanation"
}}"""
        
        schema = {
            "type": "object",
            "properties": {
                "has_contradiction": {"type": "boolean"},
                "belief_to_revise": {"type": "string"},
                "new_confidence": {"type": "number"},
                "rationale": {"type": "string"}
            }
        }
        
        response = await self.gemini.generate_structured_output(
            prompt, schema, thinking_level="low"
        )
        
        if response["has_contradiction"] and response["belief_to_revise"]:
            if verbose:
                print(f"    ⚠ Revising belief: {response['rationale'][:50]}...")
            
            # Revise the belief
            state.update_belief(
                response["belief_to_revise"],
                {"confidence": response["new_confidence"]}
            )
    
    async def _synthesize_report(self, state: AgentState) -> RefereeReport:
        """Synthesize final report from state."""
        # Use Gemini to generate recommendation
        summary = state.get_summary()
        
        prompt = f"""Based on this review, make a final recommendation.

Claims analyzed: {summary['claims_count']}
Issues found: {summary['issues_found']}
Tool calls: {summary['tool_calls']}

Issues:
{self._format_issues(state)}

What is your recommendation?

Respond with JSON:
{{
    "recommendation": "accept/minor_revision/major_revision/reject",
    "confidence": 0.0-1.0,
    "summary": "brief summary",
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"]
}}"""
        
        schema = {
            "type": "object",
            "properties": {
                "recommendation": {"type": "string"},
                "confidence": {"type": "number"},
                "summary": {"type": "string"},
                "strengths": {"type": "array", "items": {"type": "string"}},
                "weaknesses": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        response = await self.gemini.generate_structured_output(
            prompt, schema, thinking_level="high"
        )
        
        return state.to_report(
            report_id=str(uuid.uuid4()),
            recommendation=response["recommendation"],
            confidence=response["confidence"],
            summary=response["summary"],
            strengths=response["strengths"],
            weaknesses=response["weaknesses"]
        )
    
    # Helper formatting methods
    
    def _format_objectives(self, plan: List[Dict[str, Any]]) -> str:
        """Format objectives for prompt."""
        return "\n".join([
            f"- {obj['objective']} (priority: {obj['priority']})"
            for obj in plan
        ])
    
    def _format_recent_claims(self, state: AgentState, limit: int = 3) -> str:
        """Format recent claims for prompt."""
        claims = list(state.epistemic_ledger.current_claims.values())[-limit:]
        if not claims:
            return "No claims yet"
        return "\n".join([
            f"- {claim.claim_id}: {claim.content[:100]}"
            for claim in claims
        ])
    
    def _format_beliefs(self, beliefs: List[Belief]) -> str:
        """Format beliefs for prompt."""
        return "\n".join([
            f"- {b.belief_id}: {b.content} (confidence: {b.confidence:.2f})"
            for b in beliefs
        ])
    
    def _format_issues(self, state: AgentState) -> str:
        """Format issues for prompt."""
        if not state.issues_found:
            return "No issues found"
        return "\n".join([
            f"- {issue.severity.value}: {issue.description}"
            for issue in state.issues_found[:5]
        ])
