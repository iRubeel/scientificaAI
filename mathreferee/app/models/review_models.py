"""
Pydantic v2 data models for the math referee system.
Defines the data structures for papers, reviews, claims, and epistemic tracking.

All models are fully serializable and include validation constraints.
"""

from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ============================================================================
# Enums
# ============================================================================

class ClaimStatus(str, Enum):
    """
    Status of a claim during review process.
    
    - IDENTIFIED: Claim has been extracted from paper
    - ANALYZING: Currently being analyzed
    - VERIFIED: Claim has been verified as correct
    - QUESTIONED: Claim has issues or requires clarification
    - REFUTED: Claim has been found to be incorrect
    - PENDING: Awaiting further investigation
    """
    IDENTIFIED = "identified"
    ANALYZING = "analyzing"
    VERIFIED = "verified"
    QUESTIONED = "questioned"
    REFUTED = "refuted"
    PENDING = "pending"


class Severity(str, Enum):
    """
    Severity level for issues found in review.
    
    - CRITICAL: Fatal flaw that invalidates the work
    - MAJOR: Significant issue requiring substantial revision
    - MINOR: Small issue that should be addressed
    - INFORMATIONAL: Suggestion or note, not blocking
    """
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFORMATIONAL = "informational"


# ============================================================================
# Core Models
# ============================================================================

class EpistemicState(BaseModel):
    """
    Tracks the epistemic state of a claim (confidence, evidence, uncertainty).
    """
    model_config = ConfigDict(frozen=False)
    
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence level (0.0 to 1.0)"
    )
    evidence_quality: Literal["strong", "moderate", "weak", "none"] = Field(
        default="none",
        description="Quality of supporting evidence"
    )
    uncertainty_sources: List[str] = Field(
        default_factory=list,
        description="Sources of uncertainty"
    )
    requires_verification: bool = Field(
        default=False,
        description="Whether this claim needs specific verification"
    )

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {v}")
        return v


class Critique(BaseModel):
    """
    Represents a specific critique of a claim or reasoning step.
    """
    model_config = ConfigDict(frozen=False)
    
    target_id: str = Field(..., description="ID of the claim or step being critiqued")
    critique_type: str = Field(..., description="Type of critique (e.g., logical_gap)")
    severity: str = Field(..., description="Severity of the critique")
    description: str = Field(..., description="Detailed description")
    suggested_revision: Optional[str] = Field(None, description="Suggested revision")


class Claim(BaseModel):
    """
    Represents a mathematical or statistical claim from a paper.
    
    Claims are the fundamental units of analysis in the review process.
    Each claim tracks its content, status, confidence, and supporting evidence.
    """
    model_config = ConfigDict(frozen=False)
    
    claim_id: str = Field(..., description="Unique identifier for the claim")
    content: str = Field(..., description="The actual claim text")
    claim_type: Literal["theorem", "lemma", "proposition", "assumption", "result", "methodology"] = Field(
        ..., description="Type of mathematical/statistical claim"
    )
    section: str = Field(..., description="Section of paper where claim appears")
    page_number: Optional[int] = Field(None, description="Page number if available")
    
    # Status tracking
    status: ClaimStatus = Field(
        default=ClaimStatus.IDENTIFIED,
        description="Current status of the claim in review process"
    )
    
    # Epistemic tracking (Grouped)
    epistemic_state: EpistemicState = Field(
        default_factory=EpistemicState,
        description="Epistemic state of the claim"
    )
    
    # Dependencies and relationships
    dependencies: List[str] = Field(
        default_factory=list,
        description="IDs of claims this depends on"
    )
    supports: List[str] = Field(
        default_factory=list,
        description="IDs of claims this supports"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReviewIssue(BaseModel):
    """
    Represents an issue, concern, or critique found during review.
    
    Issues can range from critical flaws to minor suggestions.
    Each issue tracks its severity, description, and suggested resolution.
    """
    model_config = ConfigDict(frozen=False)
    
    issue_id: str = Field(..., description="Unique identifier for the issue")
    claim_id: Optional[str] = Field(
        None,
        description="ID of related claim, if applicable"
    )
    
    # Issue classification
    severity: Severity = Field(..., description="Severity level of the issue")
    issue_type: Literal[
        "logical_gap",
        "assumption_violation",
        "insufficient_evidence",
        "alternative_interpretation",
        "methodological_flaw",
        "statistical_error",
        "notation_ambiguity",
        "missing_citation"
    ] = Field(..., description="Type of issue identified")
    
    # Issue details
    description: str = Field(..., description="Detailed description of the issue")
    location: str = Field(..., description="Where in the paper the issue occurs")
    suggested_resolution: Optional[str] = Field(
        None,
        description="Suggested way to address the issue"
    )
    
    # Impact assessment
    affects_validity: bool = Field(
        default=False,
        description="Whether this issue affects the validity of main results"
    )
    confidence_in_issue: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence that this is a real issue (0.0 to 1.0)"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('confidence_in_issue')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is in valid range [0, 1]."""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {v}")
        return v


class ToolCall(BaseModel):
    """
    Represents a tool invocation during the review process.
    
    Tracks which tools were used, with what parameters, and what results
    were obtained. Essential for transparency and reproducibility.
    """
    model_config = ConfigDict(frozen=False)
    
    tool_name: str = Field(..., description="Name of the tool invoked")
    parameters: Dict[str, Any] = Field(..., description="Parameters passed to the tool")
    result: Optional[Any] = Field(None, description="Result returned by the tool")
    success: bool = Field(default=True, description="Whether the tool call succeeded")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time_ms: Optional[float] = Field(
        None,
        description="Execution time in milliseconds"
    )


class ReasoningStep(BaseModel):
    """
    A single step in multi-step reasoning process.
    
    Each step represents a discrete reasoning action, including what tools
    were used, what was concluded, and the confidence in that conclusion.
    """
    model_config = ConfigDict(frozen=False)
    
    step_number: int = Field(..., description="Sequential step number")
    description: str = Field(..., description="What this step is doing")
    reasoning: str = Field(..., description="The reasoning applied in this step")
    
    # Tool usage
    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="Tools invoked during this step"
    )
    
    # Conclusions
    intermediate_conclusion: str = Field(
        ...,
        description="Conclusion reached in this step"
    )
    confidence: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Confidence in this reasoning step (0.0 to 1.0)"
    )
    
    # Dependencies
    depends_on_steps: List[int] = Field(
        default_factory=list,
        description="Step numbers this depends on"
    )
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is in valid range [0, 1]."""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {v}")
        return v


class RefereeReport(BaseModel):
    """
    Complete referee report for a paper.
    
    This is the final output of the review process, containing the overall
    assessment, recommendation, and all supporting evidence.
    """
    model_config = ConfigDict(frozen=False)
    
    report_id: str = Field(..., description="Unique identifier for the report")
    paper_id: str = Field(..., description="ID of the paper being reviewed")
    paper_title: str = Field(..., description="Title of the paper")
    
    # Overall assessment
    recommendation: Literal[
        "accept",
        "minor_revision",
        "major_revision",
        "reject"
    ] = Field(..., description="Final recommendation")
    
    confidence_in_recommendation: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in the recommendation (0.0 to 1.0)"
    )
    
    # Summary
    summary: str = Field(..., description="Overall summary of the review")
    strengths: List[str] = Field(..., description="Key strengths of the paper")
    weaknesses: List[str] = Field(..., description="Key weaknesses of the paper")
    
    # Detailed findings
    claims_analyzed: List[Claim] = Field(
        default_factory=list,
        description="All claims analyzed during review"
    )
    issues_found: List[ReviewIssue] = Field(
        default_factory=list,
        description="All issues identified during review"
    )
    reasoning_steps: List[ReasoningStep] = Field(
        default_factory=list,
        description="Reasoning steps taken during review"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None)
    
    @field_validator('confidence_in_recommendation')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is in valid range [0, 1]."""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {v}")
        return v


class EpistemicLedger(BaseModel):
    """
    Immutable ledger tracking claims and their epistemic states over time.
    
    The ledger maintains a history of all claim updates, allowing us to
    see how confidence and status evolved during the review process.
    This supports transparency and allows backtracking if needed.
    """
    model_config = ConfigDict(frozen=False)
    
    ledger_id: str = Field(..., description="Unique identifier for the ledger")
    paper_id: str = Field(..., description="ID of the paper being tracked")
    
    # Claim history (immutable append-only)
    claim_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Chronological history of claim states"
    )
    
    # Current state (derived from history)
    current_claims: Dict[str, Claim] = Field(
        default_factory=dict,
        description="Current state of all claims (claim_id -> Claim)"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    def add_claim(self, claim: Claim) -> "EpistemicLedger":
        """
        Add a new claim to the ledger (immutable update).
        
        Args:
            claim: The claim to add
            
        Returns:
            New EpistemicLedger instance with the claim added
        """
        # Create history entry
        history_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "add_claim",
            "claim_id": claim.claim_id,
            "claim_data": claim.model_dump()
        }
        
        # Create new ledger with updated state
        new_history = self.claim_history + [history_entry]
        new_claims = self.current_claims.copy()
        new_claims[claim.claim_id] = claim
        
        return EpistemicLedger(
            ledger_id=self.ledger_id,
            paper_id=self.paper_id,
            claim_history=new_history,
            current_claims=new_claims,
            created_at=self.created_at,
            last_updated=datetime.utcnow()
        )
    
    def update_claim(self, claim_id: str, updates: Dict[str, Any]) -> "EpistemicLedger":
        """
        Update an existing claim (immutable update).
        
        Args:
            claim_id: ID of the claim to update
            updates: Dictionary of fields to update
            
        Returns:
            New EpistemicLedger instance with the claim updated
        """
        if claim_id not in self.current_claims:
            raise ValueError(f"Claim {claim_id} not found in ledger")
        
        # Get current claim and apply updates
        current_claim = self.current_claims[claim_id]
        updated_claim_data = current_claim.model_dump()
        
        # Handle mapping of legacy/flat fields to epistemic_state
        epistemic_fields = {"confidence", "evidence_quality", "uncertainty_sources", "requires_verification"}
        epistemic_updates = {k: v for k, v in updates.items() if k in epistemic_fields}
        other_updates = {k: v for k, v in updates.items() if k not in epistemic_fields}
        
        if epistemic_updates:
            current_epistemic = updated_claim_data.get("epistemic_state", {})
            # Ensure current_epistemic is a dict
            if hasattr(current_epistemic, "model_dump"):
                 current_epistemic = current_epistemic.model_dump()
            current_epistemic.update(epistemic_updates)
            updated_claim_data["epistemic_state"] = current_epistemic
            
        updated_claim_data.update(other_updates)
        
        updated_claim_data["updated_at"] = datetime.utcnow()
        updated_claim = Claim(**updated_claim_data)
        
        # Create history entry
        history_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "update_claim",
            "claim_id": claim_id,
            "updates": updates,
            "claim_data": updated_claim.model_dump()
        }
        
        # Create new ledger with updated state
        new_history = self.claim_history + [history_entry]
        new_claims = self.current_claims.copy()
        new_claims[claim_id] = updated_claim
        
        return EpistemicLedger(
            ledger_id=self.ledger_id,
            paper_id=self.paper_id,
            claim_history=new_history,
            current_claims=new_claims,
            created_at=self.created_at,
            last_updated=datetime.utcnow()
        )
    
    def get_claim_history(self, claim_id: str) -> List[Dict[str, Any]]:
        """
        Get the complete history of a specific claim.
        
        Args:
            claim_id: ID of the claim
            
        Returns:
            List of history entries for this claim
        """
        return [
            entry for entry in self.claim_history
            if entry.get("claim_id") == claim_id
        ]


class Paper(BaseModel):
    """
    Represents a math/statistics paper to be reviewed.
    
    Contains all metadata and content needed for the review process.
    """
    model_config = ConfigDict(frozen=False)
    
    paper_id: str = Field(..., description="Unique identifier for the paper")
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(..., description="List of author names")
    abstract: str = Field(..., description="Paper abstract")
    
    # Optional fields
    arxiv_id: Optional[str] = Field(None, description="arXiv identifier if applicable")
    pdf_url: Optional[str] = Field(None, description="URL to PDF")
    full_text: Optional[str] = Field(None, description="Full text content")
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    submitted_at: datetime = Field(default_factory=datetime.utcnow)