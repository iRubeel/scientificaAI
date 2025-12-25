"""
Gemini Client using the new google-genai SDK.
Simplified and compatible with current API.
"""

from typing import Dict, Any, Optional, Literal
import os
from google import genai
from google.genai import types


# System instruction for the referee agent
SYSTEM_INSTRUCTION = """You are an expert academic referee for mathematics and statistics papers.
Your role is to provide rigorous, skeptical, and constructive reviews.

Key principles:
- Be skeptical but fair
- Demand rigorous proofs
- Check assumptions carefully
- Verify statistical claims
- Assess novelty critically
- Provide constructive feedback"""


class GeminiClient:
    """
    Simplified Gemini client using google-genai SDK.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY must be provided or set in environment")
        
        # Configure client
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "models/gemini-2.0-flash-exp"  # Correct model for v1beta API
    
    async def generate(
        self,
        prompt: str,
        thinking_level: Literal["low", "high"] = "high",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate text response.
        
        Args:
            prompt: Input prompt
            thinking_level: Ignored (for compatibility)
            temperature: Sampling temperature
            max_tokens: Max output tokens
            
        Returns:
            Dict with 'text' key
        """
        # Truncate prompt if too long (max 1M tokens total, leave room for system + response)
        MAX_INPUT_TOKENS = 800000  # Conservative limit
        estimated_tokens = len(prompt.split()) * 1.3
        
        if estimated_tokens > MAX_INPUT_TOKENS:
            # Truncate to fit
            words = prompt.split()
            target_words = int(MAX_INPUT_TOKENS / 1.3)
            prompt = ' '.join(words[:target_words])
            prompt += "\n\n[Note: Input truncated due to length]"
        
        # Prepend system instruction
        full_prompt = f"{SYSTEM_INSTRUCTION}\n\n{prompt}"
        
        # Generate
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens or 8192,
            )
        )
        
        return {
            "text": response.text,
            "thinking_summary": None,
            "thought_signature": None,
            "thinking_level": thinking_level
        }
    
    async def generate_structured_output(
        self,
        prompt: str,
        schema: Dict[str, Any],
        thinking_level: Literal["low", "high"] = "high",
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output.
        
        Args:
            prompt: Input prompt
            schema: JSON schema (ignored, using prompt-based approach)
            thinking_level: Ignored
            temperature: Sampling temperature
            
        Returns:
            Parsed JSON dict
        """
        # Add JSON instruction to prompt
        schema_prompt = f"""{prompt}

Please respond with valid JSON matching this schema:
{schema}

Respond ONLY with the JSON, no additional text."""
        
        response = await self.generate(
            schema_prompt,
            thinking_level=thinking_level,
            temperature=temperature
        )
        
        # Parse JSON
        import json
        import re
        
        try:
            # Clean response
            cleaned = response["text"].strip()
            
            # Remove markdown code blocks if present
            if "```json" in cleaned:
                cleaned = re.search(r'```json\s*(.*?)\s*```', cleaned, re.DOTALL).group(1)
            elif "```" in cleaned:
                cleaned = re.search(r'```\s*(.*?)\s*```', cleaned, re.DOTALL).group(1)
            
            # Parse JSON
            return json.loads(cleaned)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response['text'][:500]}")
    
    async def chat(
        self,
        messages: list,
        thinking_level: Literal["low", "high"] = "high",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Multi-turn chat (simplified).
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            thinking_level: Ignored
            temperature: Sampling temperature
            
        Returns:
            Dict with 'text' key
        """
        # Convert messages to single prompt
        prompt_parts = [SYSTEM_INSTRUCTION]
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt_parts.append(f"{role.upper()}: {content}")
        
        full_prompt = "\n\n".join(prompt_parts)
        
        return await self.generate(full_prompt, thinking_level, temperature)
    
    def get_token_count(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        return len(text.split()) * 1.3  # Rough estimate
