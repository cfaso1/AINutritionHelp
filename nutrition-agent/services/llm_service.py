import anthropic
from typing import Optional


class LLMService:
    """Service for interacting with Claude AI"""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
    
    async def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate a response from Claude
        
        Args:
            prompt: The prompt to send to Claude
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text response
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract text from response
            return message.content[0].text
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Error: Unable to generate analysis. {str(e)}"
    
    async def analyze_with_context(self, 
                                   system_prompt: str, 
                                   user_prompt: str, 
                                   max_tokens: int = 500) -> str:
        """
        Generate a response with system context
        
        Args:
            system_prompt: System-level instructions
            user_prompt: User's specific query
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text response
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Error: Unable to generate analysis. {str(e)}"