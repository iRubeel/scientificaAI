"""
FastAPI routes for the MathReferee API.
Implements POST /review-paper with end-to-end review, error handling, and partial results.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.agent.referee_agent import RefereeAgent
from app.models.review_models import Paper
from app.tools.arxiv import ArxivTool


app = FastAPI(
    title="MathReferee API",
    version="1.0.0",
    description="Autonomous AI referee for math/statistics papers"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent: Optional[RefereeAgent] = None


# Request/Response Models

class ReviewPaperRequest(BaseModel):
    """Request model for POST /review-paper."""
    arxiv_id: Optional[str] = Field(None, description="arXiv paper ID (e.g., '2301.12345')")
    pdf_url: Optional[str] = Field(None, description="URL to PDF file")
    paper_data: Optional[Dict[str, Any]] = Field(None, description="Direct paper data")
    max_iterations: int = Field(10, description="Maximum review iterations", ge=1, le=20)
    verbose: bool = Field(False, description="Include detailed progress")


class ReviewPaperResponse(BaseModel):
    """Response model for POST /review-paper."""
    success: bool
    review_id: str
    paper_title: str
    
    # Final report
    recommendation: Optional[str] = None
    confidence: Optional[float] = None
    summary: Optional[str] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    
    # Agent steps
    agent_steps: List[Dict[str, Any]] = Field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    claims_analyzed: List[Dict[str, Any]] = Field(default_factory=list)
    issues_found: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    total_iterations: int = 0
    total_reasoning_steps: int = 0
    completed_at: Optional[str] = None
    
    # Error handling
    error: Optional[str] = None
    partial_results: bool = False


# Startup/Shutdown

@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup."""
    global agent
    try:
        agent = RefereeAgent()
        print("✓ RefereeAgent initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize RefereeAgent: {e}")
        # Continue anyway - will fail on first request


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global agent
    agent = None


# Endpoints

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "MathReferee API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "review": "POST /review-paper",
            "health": "GET /health",
            "tools": "GET /tools"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/tools")
async def list_tools() -> Dict[str, Any]:
    """List available tools."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return {
        "tools": list(agent.tools.keys()),
        "schemas": agent.tool_schemas,
        "descriptions": {
            "arxiv": "Search and retrieve papers from arXiv",
            "literature": "Search academic literature and analyze citations",
            "symbolic": "Symbolic mathematics and equation solving",
            "stats": "Statistical analysis and hypothesis testing"
        }
    }


@app.post("/review-paper", response_model=ReviewPaperResponse)
async def review_paper(request: ReviewPaperRequest) -> ReviewPaperResponse:
    """
    Review a paper end-to-end.
    
    Accepts:
    - arXiv ID: Fetches paper from arXiv
    - PDF URL: Downloads and processes PDF
    - Paper data: Direct paper submission
    
    Returns:
    - Complete review with agent steps, tool calls, and final report
    - Partial results if review fails partway through
    
    Error handling:
    - Returns partial results on failure
    - Includes error message
    - All fields are JSON serializable
    """
    review_id = str(uuid.uuid4())
    
    # Initialize response with defaults
    response = ReviewPaperResponse(
        success=False,
        review_id=review_id,
        paper_title="Unknown"
    )
    
    try:
        # Step 1: Validate agent
        if not agent:
            response.error = "Agent not initialized"
            return response
        
        # Step 2: Fetch/create paper
        paper = None
        
        if request.arxiv_id:
            # Fetch from arXiv
            try:
                arxiv_tool = ArxivTool()
                paper_data = await arxiv_tool.fetch_paper_metadata(request.arxiv_id)
                
                if not paper_data.get("success"):
                    response.error = f"Failed to fetch arXiv paper: {paper_data.get('error')}"
                    return response
                
                # Try to get full text
                sections_data = await arxiv_tool.extract_paper_sections(request.arxiv_id)
                full_text = ""
                if sections_data.get("success"):
                    for section in sections_data.get("sections", []):
                        full_text += f"\n\n{section['title']}\n{section['content']}"
                
                paper = Paper(
                    paper_id=str(uuid.uuid4()),
                    title=paper_data["title"],
                    authors=paper_data["authors"],
                    abstract=paper_data["abstract"],
                    arxiv_id=request.arxiv_id,
                    pdf_url=paper_data.get("pdf_url"),
                    full_text=full_text if full_text else paper_data["abstract"],
                    metadata={
                        "categories": paper_data.get("categories", []),
                        "published": paper_data.get("published_date")
                    }
                )
                
            except Exception as e:
                response.error = f"Error fetching arXiv paper: {str(e)}"
                response.partial_results = True
                return response
        
        elif request.pdf_url:
            response.error = "PDF URL processing not yet implemented"
            return response
        
        elif request.paper_data:
            # Direct paper data
            try:
                paper = Paper(
                    paper_id=str(uuid.uuid4()),
                    title=request.paper_data.get("title", "Untitled"),
                    authors=request.paper_data.get("authors", []),
                    abstract=request.paper_data.get("abstract", ""),
                    full_text=request.paper_data.get("full_text"),
                    metadata=request.paper_data.get("metadata", {})
                )
            except Exception as e:
                response.error = f"Invalid paper data: {str(e)}"
                return response
        
        else:
            response.error = "Must provide arxiv_id, pdf_url, or paper_data"
            return response
        
        response.paper_title = paper.title
        
        # Step 3: Conduct review
        try:
            report = await agent.review_paper(
                paper,
                max_iterations=request.max_iterations,
                verbose=request.verbose
            )
            
            # Extract agent state for detailed results
            # Note: In production, agent would expose state
            # For now, we'll extract from report
            
            response.success = True
            response.recommendation = report.recommendation
            response.confidence = report.confidence_in_recommendation
            response.summary = report.summary
            response.strengths = report.strengths
            response.weaknesses = report.weaknesses
            
            # Convert claims to JSON-serializable format
            response.claims_analyzed = [
                {
                    "claim_id": claim.claim_id,
                    "content": claim.content,
                    "claim_type": claim.claim_type,
                    "confidence": claim.epistemic_state.confidence,
                    "status": claim.status.value if hasattr(claim.status, 'value') else str(claim.status)
                }
                for claim in report.claims_analyzed
            ]
            
            # Convert issues to JSON-serializable format
            response.issues_found = [
                {
                    "issue_id": issue.issue_id,
                    "severity": issue.severity.value if hasattr(issue.severity, 'value') else str(issue.severity),
                    "issue_type": issue.issue_type,
                    "description": issue.description,
                    "location": issue.location,
                    "affects_validity": issue.affects_validity
                }
                for issue in report.issues_found
            ]
            
            # Convert reasoning steps to agent steps
            response.agent_steps = [
                {
                    "step_number": step.step_number,
                    "description": step.description,
                    "reasoning": step.reasoning[:200] + "..." if len(step.reasoning) > 200 else step.reasoning,
                    "conclusion": step.intermediate_conclusion,
                    "confidence": step.confidence
                }
                for step in report.reasoning_steps
            ]
            
            # Extract tool calls from reasoning steps
            tool_calls = []
            for step in report.reasoning_steps:
                for tool_call in step.tool_calls:
                    tool_calls.append({
                        "tool_name": tool_call.tool_name,
                        "parameters": tool_call.parameters,
                        "success": tool_call.success,
                        "result_summary": str(tool_call.result)[:100] + "..." if tool_call.result else None
                    })
            response.tool_calls = tool_calls
            
            response.total_reasoning_steps = len(report.reasoning_steps)
            response.completed_at = report.completed_at.isoformat() if report.completed_at else datetime.utcnow().isoformat()
            
        except Exception as e:
            # Review failed partway through - return partial results
            response.error = f"Review failed: {str(e)}"
            response.partial_results = True
            
            # Try to extract any partial results from exception context
            # In production, agent would expose partial state
            response.summary = f"Review incomplete due to error: {str(e)}"
            
            return response
    
    except Exception as e:
        # Outer exception handler for unexpected errors
        response.error = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        response.partial_results = True
        return response
    
    return response


# Legacy endpoints for backwards compatibility

@app.post("/review/arxiv/{arxiv_id}")
async def review_arxiv_paper_legacy(arxiv_id: str, verbose: bool = False) -> Dict[str, Any]:
    """
    Legacy endpoint for arXiv review.
    Redirects to POST /review-paper.
    """
    request = ReviewPaperRequest(arxiv_id=arxiv_id, verbose=verbose)
    response = await review_paper(request)
    
    if not response.success:
        raise HTTPException(status_code=500, detail=response.error)
    
    return {
        "review_id": response.review_id,
        "paper_title": response.paper_title,
        "recommendation": response.recommendation,
        "confidence": response.confidence,
        "summary": response.summary,
        "strengths": response.strengths,
        "weaknesses": response.weaknesses,
        "claims_analyzed": len(response.claims_analyzed),
        "issues_found": len(response.issues_found)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
