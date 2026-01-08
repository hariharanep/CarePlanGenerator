import os
from anthropic import Anthropic
from app.prompt import generate_prompt
from typing import Dict

class CarePlanGenerator:

    MODEL_NAME = "claude-sonnet-4-5-20250929"
    MAX_TOKENS_LIMIT = 4500

    def __init__(self):
        # Initialize anthropic client
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("API Key hasn't been provided")
        self.client = Anthropic(api_key=api_key)
    
    def generate_care_plan_with_llm(self, data: Dict) -> str:
        """Generate care plan using LLM."""
        try:        
            # Generate prompt
            prompt = generate_prompt(data)

            # Invoke claude-sonnet-4-5-20250929 LLM with prompt
            message = self.client.messages.create(
                model=self.MODEL_NAME,
                max_tokens=self.MAX_TOKENS_LIMIT,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Return LLM response
            return message.content[0].text
        except Exception as e:
            # raise runtime error if LLM call fails
            raise RuntimeError("LLM call failed to return a valid response without any internal errors")
        