"""
Literature search and citation analysis tool.
Provides structured novelty signals and citation analysis using Semantic Scholar API.
"""

from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime


# JSON Schema for Gemini function calling
LITERATURE_TOOL_SCHEMA = {
    "search_related_work": {
        "name": "search_related_work",
        "description": "Search for related academic papers and assess novelty",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query describing the research topic or claim"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of papers to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    "analyze_citations": {
        "name": "analyze_citations",
        "description": "Analyze citation network for a paper to assess impact and relationships",
        "parameters": {
            "type": "object",
            "properties": {
                "paper_id": {
                    "type": "string",
                    "description": "Semantic Scholar paper ID or DOI"
                }
            },
            "required": ["paper_id"]
        }
    },
    "assess_novelty": {
        "name": "assess_novelty",
        "description": "Assess the novelty of a claim by searching existing literature",
        "parameters": {
            "type": "object",
            "properties": {
                "claim": {
                    "type": "string",
                    "description": "The claim or contribution to assess for novelty"
                },
                "context": {
                    "type": "string",
                    "description": "Additional context about the research area"
                }
            },
            "required": ["claim"]
        }
    }
}


class LiteratureTool:
    """
    Tool for searching academic literature and analyzing citations.
    Returns structured novelty signals and citation analysis.
    """
    
    def __init__(self):
        """Initialize literature search tool."""
        self.semantic_scholar_base = "https://api.semanticscholar.org/graph/v1"
        self.timeout = 30.0
    
    def get_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get JSON schemas for all tool functions."""
        return LITERATURE_TOOL_SCHEMA
    
    async def search_related_work(
        self,
        query: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Search for related academic papers.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Structured search results with papers
        """
        try:
            fields = ["paperId", "title", "abstract", "authors", "year",
                     "citationCount", "influentialCitationCount", "url", "fieldsOfStudy"]
            
            params = {
                "query": query,
                "limit": limit,
                "fields": ",".join(fields)
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.semantic_scholar_base}/paper/search",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
            
            papers = data.get("data", [])
            
            return {
                "success": True,
                "query": query,
                "total_results": len(papers),
                "papers": [self._format_paper(p) for p in papers]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def analyze_citations(self, paper_id: str) -> Dict[str, Any]:
        """
        Analyze citation network for a paper.
        
        Args:
            paper_id: Semantic Scholar paper ID or DOI
            
        Returns:
            Structured citation analysis
        """
        try:
            # Get paper details
            fields = ["paperId", "title", "citationCount", "referenceCount",
                     "influentialCitationCount", "year", "fieldsOfStudy"]
            
            params = {"fields": ",".join(fields)}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.semantic_scholar_base}/paper/{paper_id}",
                    params=params
                )
                response.raise_for_status()
                paper = response.json()
            
            # Get top citations
            citations = await self._get_top_citations(paper_id, limit=5)
            
            # Get key references
            references = await self._get_top_references(paper_id, limit=5)
            
            return {
                "success": True,
                "paper_id": paper_id,
                "title": paper.get("title"),
                "citation_metrics": {
                    "total_citations": paper.get("citationCount", 0),
                    "influential_citations": paper.get("influentialCitationCount", 0),
                    "total_references": paper.get("referenceCount", 0),
                    "year": paper.get("year")
                },
                "fields_of_study": paper.get("fieldsOfStudy", []),
                "top_citing_papers": citations,
                "key_references": references,
                "impact_assessment": self._assess_impact(paper)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "paper_id": paper_id
            }
    
    async def assess_novelty(
        self,
        claim: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Assess the novelty of a claim by searching existing literature.
        
        Args:
            claim: The claim to assess
            context: Additional context
            
        Returns:
            Structured novelty assessment
        """
        try:
            # Search for papers related to the claim
            search_query = f"{claim} {context}".strip()
            results = await self.search_related_work(search_query, limit=10)
            
            if not results["success"]:
                return results
            
            papers = results["papers"]
            
            # Analyze novelty signals
            novelty_signals = {
                "highly_similar_work_exists": len(papers) > 5,
                "recent_similar_work": any(p.get("year", 0) >= datetime.now().year - 2 for p in papers),
                "high_citation_similar_work": any(p.get("citation_count", 0) > 50 for p in papers),
                "exact_match_likelihood": "low"  # Would need semantic analysis for accurate assessment
            }
            
            # Determine novelty level
            if novelty_signals["highly_similar_work_exists"] and novelty_signals["recent_similar_work"]:
                novelty_level = "low"
                explanation = "Multiple recent papers found on similar topics"
            elif novelty_signals["highly_similar_work_exists"]:
                novelty_level = "moderate"
                explanation = "Similar work exists but may not be recent"
            else:
                novelty_level = "high"
                explanation = "Limited similar work found in literature"
            
            return {
                "success": True,
                "claim": claim,
                "novelty_level": novelty_level,
                "confidence": 0.7,  # Moderate confidence without deep semantic analysis
                "explanation": explanation,
                "novelty_signals": novelty_signals,
                "similar_papers_count": len(papers),
                "most_relevant_papers": papers[:3]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "claim": claim
            }
    
    async def _get_top_citations(self, paper_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top citing papers."""
        try:
            params = {
                "fields": "paperId,title,year,citationCount",
                "limit": limit
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.semantic_scholar_base}/paper/{paper_id}/citations",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
            
            citations = data.get("data", [])
            return [
                {
                    "title": c.get("citingPaper", {}).get("title"),
                    "year": c.get("citingPaper", {}).get("year"),
                    "citation_count": c.get("citingPaper", {}).get("citationCount", 0)
                }
                for c in citations
            ]
        except:
            return []
    
    async def _get_top_references(self, paper_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get key references."""
        try:
            params = {
                "fields": "paperId,title,year,citationCount",
                "limit": limit
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.semantic_scholar_base}/paper/{paper_id}/references",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
            
            references = data.get("data", [])
            return [
                {
                    "title": r.get("citedPaper", {}).get("title"),
                    "year": r.get("citedPaper", {}).get("year"),
                    "citation_count": r.get("citedPaper", {}).get("citationCount", 0)
                }
                for r in references
            ]
        except:
            return []
    
    def _format_paper(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """Format paper data for output."""
        return {
            "paper_id": paper.get("paperId"),
            "title": paper.get("title"),
            "authors": [a.get("name") for a in paper.get("authors", [])],
            "year": paper.get("year"),
            "abstract": paper.get("abstract", "")[:200] + "..." if paper.get("abstract") else None,
            "citation_count": paper.get("citationCount", 0),
            "influential_citation_count": paper.get("influentialCitationCount", 0),
            "fields_of_study": paper.get("fieldsOfStudy", []),
            "url": paper.get("url")
        }
    
    def _assess_impact(self, paper: Dict[str, Any]) -> str:
        """Assess paper impact based on citations."""
        citations = paper.get("citationCount", 0)
        influential = paper.get("influentialCitationCount", 0)
        year = paper.get("year", datetime.now().year)
        age = datetime.now().year - year
        
        if age == 0:
            age = 1
        
        citations_per_year = citations / age
        
        if citations_per_year > 50 or influential > 20:
            return "high_impact"
        elif citations_per_year > 10 or influential > 5:
            return "moderate_impact"
        else:
            return "low_impact"
