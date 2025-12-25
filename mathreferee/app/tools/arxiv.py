"""
arXiv integration tool for fetching and processing math/stats papers.
Provides structured outputs with JSON schemas for Gemini function calling.
"""

import arxiv
from typing import List, Optional, Dict, Any
from datetime import datetime
import requests
from PyPDF2 import PdfReader
import io
import re


# JSON Schema for Gemini function calling
ARXIV_TOOL_SCHEMA = {
    "fetch_paper_metadata": {
        "name": "fetch_paper_metadata",
        "description": "Fetch metadata for a paper from arXiv by its ID",
        "parameters": {
            "type": "object",
            "properties": {
                "arxiv_id": {
                    "type": "string",
                    "description": "arXiv identifier (e.g., '2301.12345' or '2301.12345v1')"
                }
            },
            "required": ["arxiv_id"]
        }
    },
    "search_related_papers": {
        "name": "search_related_papers",
        "description": "Search for papers related to a topic on arXiv",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (keywords, concepts, or phrases)"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5
                },
                "categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "arXiv categories to filter by (e.g., ['math.ST', 'stat.ML'])"
                }
            },
            "required": ["query"]
        }
    },
    "extract_paper_sections": {
        "name": "extract_paper_sections",
        "description": "Download and extract sections from an arXiv paper PDF",
        "parameters": {
            "type": "object",
            "properties": {
                "arxiv_id": {
                    "type": "string",
                    "description": "arXiv identifier"
                }
            },
            "required": ["arxiv_id"]
        }
    }
}


class ArxivTool:
    """
    Tool for searching and retrieving papers from arXiv.
    All methods return structured outputs compatible with Gemini function calling.
    """
    
    def __init__(self):
        """Initialize arXiv tool."""
        self.client = arxiv.Client()
    
    def get_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get JSON schemas for all tool functions."""
        return ARXIV_TOOL_SCHEMA
    
    async def fetch_paper_metadata(self, arxiv_id: str) -> Dict[str, Any]:
        """
        Fetch metadata for a paper from arXiv.
        
        Args:
            arxiv_id: arXiv identifier (e.g., '2301.12345')
            
        Returns:
            Structured metadata dictionary
        """
        try:
            # Clean arxiv_id (remove version if present)
            clean_id = arxiv_id.split('v')[0]
            
            search = arxiv.Search(id_list=[clean_id])
            paper = next(self.client.results(search))
            
            return {
                "success": True,
                "arxiv_id": clean_id,
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "abstract": paper.summary,
                "published_date": paper.published.isoformat() if paper.published else None,
                "updated_date": paper.updated.isoformat() if paper.updated else None,
                "categories": paper.categories,
                "primary_category": paper.primary_category,
                "pdf_url": paper.pdf_url,
                "doi": paper.doi,
                "journal_ref": paper.journal_ref,
                "comment": paper.comment
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "arxiv_id": arxiv_id
            }
    
    async def search_related_papers(
        self,
        query: str,
        max_results: int = 5,
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search for papers related to a topic on arXiv.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            categories: arXiv categories to filter by
            
        Returns:
            Structured search results
        """
        try:
            # Build search query with categories if provided
            search_query = query
            if categories:
                cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
                search_query = f"({query}) AND ({cat_query})"
            
            search = arxiv.Search(
                query=search_query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            results = []
            for paper in self.client.results(search):
                results.append({
                    "arxiv_id": paper.entry_id.split("/")[-1],
                    "title": paper.title,
                    "authors": [author.name for author in paper.authors],
                    "abstract": paper.summary[:300] + "..." if len(paper.summary) > 300 else paper.summary,
                    "published_date": paper.published.isoformat() if paper.published else None,
                    "categories": paper.categories,
                    "relevance_score": 1.0 / (results.__len__() + 1)  # Simple relevance scoring
                })
            
            return {
                "success": True,
                "query": query,
                "total_results": len(results),
                "papers": results
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def extract_paper_sections(self, arxiv_id: str) -> Dict[str, Any]:
        """
        Download PDF and extract sections from an arXiv paper.
        
        Args:
            arxiv_id: arXiv identifier
            
        Returns:
            Structured sections dictionary
        """
        try:
            # Download PDF
            clean_id = arxiv_id.split('v')[0]
            pdf_url = f"https://arxiv.org/pdf/{clean_id}.pdf"
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            # Extract text
            pdf_file = io.BytesIO(response.content)
            reader = PdfReader(pdf_file)
            
            full_text = []
            for page in reader.pages:
                full_text.append(page.extract_text())
            
            text = "\n\n".join(full_text)
            
            # Basic section extraction using common patterns
            sections = self._parse_sections(text)
            
            return {
                "success": True,
                "arxiv_id": clean_id,
                "total_pages": len(reader.pages),
                "sections": sections,
                "full_text_length": len(text),
                "extraction_method": "basic_pattern_matching"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "arxiv_id": arxiv_id
            }
    
    def _parse_sections(self, text: str) -> List[Dict[str, str]]:
        """
        Parse sections from paper text using basic pattern matching.
        
        Args:
            text: Full paper text
            
        Returns:
            List of section dictionaries
        """
        sections = []
        
        # Common section patterns in academic papers
        section_patterns = [
            r'\n\s*(\d+\.?\s+[A-Z][^\n]{5,50})\n',  # Numbered sections
            r'\n\s*([A-Z][A-Z\s]{5,50})\n',  # All caps sections
            r'\n\s*(Abstract|Introduction|Methods?|Results?|Discussion|Conclusion|References)\s*\n'  # Common sections
        ]
        
        # Find all potential section headers
        headers = []
        for pattern in section_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                header = match.group(1).strip()
                position = match.start()
                headers.append((position, header))
        
        # Sort by position
        headers.sort(key=lambda x: x[0])
        
        # Extract content for each section
        for i, (pos, header) in enumerate(headers):
            next_pos = headers[i + 1][0] if i + 1 < len(headers) else len(text)
            content = text[pos:next_pos].strip()
            
            # Remove the header from content
            content = content[len(header):].strip()
            
            # Limit content length for structured output
            if len(content) > 1000:
                content = content[:1000] + "..."
            
            sections.append({
                "title": header,
                "content": content,
                "position": pos
            })
        
        # If no sections found, return full text as single section
        if not sections:
            sections.append({
                "title": "Full Text",
                "content": text[:2000] + "..." if len(text) > 2000 else text,
                "position": 0
            })
        
        return sections[:10]  # Limit to first 10 sections
