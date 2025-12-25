"""
Planner component for the referee agent.
Creates structured plans for reviewing papers.
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid

from app.core.gemini import GeminiClient
from app.core.state import AgentState
from app.models.review_models import ReviewPlan, PlanStep, Paper


class Planner:
    """Creates and manages review plans."""
    
    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize planner.
        
        Args:
            gemini_client: Gemini API client
        """
        self.gemini = gemini_client
        
    async def create_review_plan(self, paper: Paper, state: AgentState) -> ReviewPlan:
        """
        Create a structured plan for reviewing a paper.
        
        Args:
            paper: Paper to review
            state: Current agent state
            
        Returns:
            ReviewPlan with ordered steps
        """
        # Create planning prompt
        prompt = f"""You are an expert mathematical referee creating a review plan for a research paper.

Paper Title: {paper.title}
Authors: {', '.join(paper.authors)}
Abstract: {paper.abstract}

Create a detailed, step-by-step plan for reviewing this paper. Consider:
1. Understanding the main claims and contributions
2. Verifying mathematical rigor and correctness
3. Checking statistical methodology (if applicable)
4. Evaluating novelty and significance
5. Assessing clarity and presentation
6. Verifying citations and related work

For each step, specify:
- A clear description of what to do
- Which tools are needed (arxiv, literature, symbolic, stats)
- What output is expected
- Any dependencies on previous steps

Respond with a JSON array of steps, each with: step_id, description, tools_needed (array), expected_output, dependencies (array of step_ids)."""

        # Get structured plan from Gemini
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step_id": {"type": "string"},
                    "description": {"type": "string"},
                    "tools_needed": {"type": "array", "items": {"type": "string"}},
                    "expected_output": {"type": "string"},
                    "dependencies": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
        
        response = await self.gemini.generate_structured_output(prompt, schema)
        
        # Convert to PlanStep objects
        steps = []
        for step_data in response:
            step = PlanStep(
                step_id=step_data["step_id"],
                description=step_data["description"],
                tools_needed=step_data["tools_needed"],
                expected_output=step_data["expected_output"],
                dependencies=step_data.get("dependencies", [])
            )
            steps.append(step)
        
        # Create ReviewPlan
        plan = ReviewPlan(
            plan_id=str(uuid.uuid4()),
            paper_id=paper.paper_id,
            steps=steps
        )
        
        return plan
    
    async def adapt_plan(
        self,
        current_plan: ReviewPlan,
        state: AgentState,
        reason: str
    ) -> ReviewPlan:
        """
        Adapt the review plan based on new information or issues.
        
        Args:
            current_plan: Current review plan
            state: Current agent state
            reason: Reason for adaptation
            
        Returns:
            Updated ReviewPlan
        """
        # Create adaptation prompt
        prompt = f"""You are adapting a review plan based on new information.

Original Plan Steps:
{self._format_plan_for_prompt(current_plan)}

Current Progress:
- Claims identified: {len(state.claims)}
- Reasoning steps completed: {len(state.reasoning_history)}
- Critiques raised: {len(state.critiques)}

Reason for Adaptation: {reason}

Update the plan to address this issue. You can:
- Add new steps
- Modify existing steps
- Reorder steps
- Mark steps as no longer needed

Respond with a complete updated JSON array of steps."""

        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step_id": {"type": "string"},
                    "description": {"type": "string"},
                    "tools_needed": {"type": "array", "items": {"type": "string"}},
                    "expected_output": {"type": "string"},
                    "dependencies": {"type": "array", "items": {"type": "string"}},
                    "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "failed"]}
                }
            }
        }
        
        response = await self.gemini.generate_structured_output(prompt, schema)
        
        # Convert to PlanStep objects
        steps = []
        for step_data in response:
            step = PlanStep(
                step_id=step_data["step_id"],
                description=step_data["description"],
                tools_needed=step_data["tools_needed"],
                expected_output=step_data["expected_output"],
                dependencies=step_data.get("dependencies", []),
                status=step_data.get("status", "pending")
            )
            steps.append(step)
        
        # Create updated plan
        updated_plan = ReviewPlan(
            plan_id=current_plan.plan_id,
            paper_id=current_plan.paper_id,
            steps=steps,
            created_at=current_plan.created_at
        )
        
        return updated_plan
    
    def _format_plan_for_prompt(self, plan: ReviewPlan) -> str:
        """Format plan steps for inclusion in prompt."""
        lines = []
        for i, step in enumerate(plan.steps, 1):
            lines.append(f"{i}. [{step.status}] {step.description}")
            lines.append(f"   Tools: {', '.join(step.tools_needed)}")
            if step.dependencies:
                lines.append(f"   Depends on: {', '.join(step.dependencies)}")
        return "\n".join(lines)
    
    def get_next_steps(self, plan: ReviewPlan) -> List[PlanStep]:
        """
        Get the next executable steps from the plan.
        
        Args:
            plan: Review plan
            
        Returns:
            List of steps that can be executed (dependencies met)
        """
        executable = []
        
        for step in plan.steps:
            if step.status != "pending":
                continue
                
            # Check if all dependencies are completed
            deps_met = True
            for dep_id in step.dependencies:
                dep_step = next((s for s in plan.steps if s.step_id == dep_id), None)
                if not dep_step or dep_step.status != "completed":
                    deps_met = False
                    break
            
            if deps_met:
                executable.append(step)
        
        return executable
