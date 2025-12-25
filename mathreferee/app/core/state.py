"""
State management for the referee agent.
Tracks the current state of the review process including context, claims, reasoning,
tool calls, and epistemic beliefs.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.models.review_models import (
    Paper, RefereeReport, ReviewIssue, Claim, ReasoningStep,
    ToolCall, EpistemicLedger, ClaimStatus
)


class Belief(BaseModel):
    """
    Represents a belief held by the agent during the review process.
    
    Beliefs track what the agent thinks is true, with associated confidence
    and supporting evidence. This enables epistemic reasoning and self-critique.
    """
    model_config = ConfigDict(frozen=False)
    
    belief_id: str = Field(..., description="Unique identifier for the belief")
    content: str = Field(..., description="What the agent believes")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in this belief (0.0 to 1.0)"
    )
    supporting_evidence: List[str] = Field(
        default_factory=list,
        description="Evidence supporting this belief"
    )
    contradicting_evidence: List[str] = Field(
        default_factory=list,
        description="Evidence contradicting this belief"
    )
    based_on_steps: List[int] = Field(
        default_factory=list,
        description="Reasoning step numbers this belief is based on"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AgentState(BaseModel):
    """
    Manages the complete state of the referee agent during a review.
    
    Stores all steps, tool calls, claims, beliefs, and context needed to
    track the review process. Supports serialization for checkpointing
    and resuming reviews.
    """
    model_config = ConfigDict(frozen=False)
    
    # Core data
    paper: Paper = Field(..., description="The paper being reviewed")
    
    # Epistemic tracking
    epistemic_ledger: EpistemicLedger = Field(
        ...,
        description="Ledger tracking claims and their evolution"
    )
    beliefs: List[Belief] = Field(
        default_factory=list,
        description="Current beliefs held by the agent"
    )
    
    # Review process tracking
    reasoning_steps: List[ReasoningStep] = Field(
        default_factory=list,
        description="All reasoning steps taken"
    )
    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="All tool invocations"
    )
    issues_found: List[ReviewIssue] = Field(
        default_factory=list,
        description="Issues identified during review"
    )
    
    # Context and metadata
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary context data"
    )
    current_section: Optional[str] = Field(
        None,
        description="Current section being analyzed"
    )
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Methods for state manipulation
    
    def add_claim(self, claim: Claim) -> None:
        """
        Add a new claim to the epistemic ledger.
        
        Args:
            claim: The claim to add
        """
        self.epistemic_ledger = self.epistemic_ledger.add_claim(claim)
        self.last_updated = datetime.utcnow()
    
    def update_claim(self, claim_id: str, updates: Dict[str, Any]) -> None:
        """
        Update an existing claim in the ledger.
        
        Args:
            claim_id: ID of the claim to update
            updates: Dictionary of fields to update
        """
        self.epistemic_ledger = self.epistemic_ledger.update_claim(claim_id, updates)
        self.last_updated = datetime.utcnow()
    
    def get_claim(self, claim_id: str) -> Optional[Claim]:
        """
        Get a claim by ID.
        
        Args:
            claim_id: ID of the claim
            
        Returns:
            The claim if found, None otherwise
        """
        return self.epistemic_ledger.current_claims.get(claim_id)
    
    def get_claims_by_status(self, status: ClaimStatus) -> List[Claim]:
        """
        Get all claims with a specific status.
        
        Args:
            status: The status to filter by
            
        Returns:
            List of claims with that status
        """
        return [
            claim for claim in self.epistemic_ledger.current_claims.values()
            if claim.status == status
        ]
    
    def add_belief(self, belief: Belief) -> None:
        """
        Add a new belief to the agent's belief state.
        
        Args:
            belief: The belief to add
        """
        self.beliefs.append(belief)
        self.last_updated = datetime.utcnow()
    
    def update_belief(self, belief_id: str, updates: Dict[str, Any]) -> None:
        """
        Update an existing belief.
        
        Args:
            belief_id: ID of the belief to update
            updates: Dictionary of fields to update
        """
        for belief in self.beliefs:
            if belief.belief_id == belief_id:
                for key, value in updates.items():
                    setattr(belief, key, value)
                belief.updated_at = datetime.utcnow()
                break
        self.last_updated = datetime.utcnow()
    
    def add_reasoning_step(self, step: ReasoningStep) -> None:
        """
        Add a reasoning step to the history.
        
        Args:
            step: The reasoning step to add
        """
        self.reasoning_steps.append(step)
        self.last_updated = datetime.utcnow()
    
    def add_tool_call(self, tool_call: ToolCall) -> None:
        """
        Record a tool invocation.
        
        Args:
            tool_call: The tool call to record
        """
        self.tool_calls.append(tool_call)
        self.last_updated = datetime.utcnow()
    
    def add_issue(self, issue: ReviewIssue) -> None:
        """
        Add an issue found during review.
        
        Args:
            issue: The issue to add
        """
        self.issues_found.append(issue)
        self.last_updated = datetime.utcnow()
    
    def update_context(self, key: str, value: Any) -> None:
        """
        Update a context value.
        
        Args:
            key: Context key
            value: Context value
        """
        self.context[key] = value
        self.last_updated = datetime.utcnow()
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Get a context value.
        
        Args:
            key: Context key
            default: Default value if key not found
            
        Returns:
            Context value or default
        """
        return self.context.get(key, default)
    
    def to_report(
        self,
        report_id: str,
        recommendation: str,
        confidence: float,
        summary: str,
        strengths: List[str],
        weaknesses: List[str]
    ) -> RefereeReport:
        """
        Convert current state to a RefereeReport.
        
        Args:
            report_id: Unique report identifier
            recommendation: Final recommendation
            confidence: Confidence in recommendation
            summary: Overall summary
            strengths: List of strengths
            weaknesses: List of weaknesses
            
        Returns:
            Complete RefereeReport
        """
        return RefereeReport(
            report_id=report_id,
            paper_id=self.paper.paper_id,
            paper_title=self.paper.title,
            recommendation=recommendation,
            confidence_in_recommendation=confidence,
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            claims_analyzed=list(self.epistemic_ledger.current_claims.values()),
            issues_found=self.issues_found,
            reasoning_steps=self.reasoning_steps,
            completed_at=datetime.utcnow()
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current state.
        
        Returns:
            Dictionary with state summary
        """
        return {
            "paper_id": self.paper.paper_id,
            "paper_title": self.paper.title,
            "claims_count": len(self.epistemic_ledger.current_claims),
            "beliefs_count": len(self.beliefs),
            "reasoning_steps": len(self.reasoning_steps),
            "tool_calls": len(self.tool_calls),
            "issues_found": len(self.issues_found),
            "current_section": self.current_section,
            "elapsed_time_seconds": (datetime.utcnow() - self.started_at).total_seconds()
        }
    
    @classmethod
    def create_for_paper(cls, paper: Paper) -> "AgentState":
        """
        Create a new AgentState for a paper.
        
        Args:
            paper: The paper to review
            
        Returns:
            New AgentState instance
        """
        import uuid
        ledger = EpistemicLedger(
            ledger_id=str(uuid.uuid4()),
            paper_id=paper.paper_id
        )
        
        return cls(
            paper=paper,
            epistemic_ledger=ledger
        )
