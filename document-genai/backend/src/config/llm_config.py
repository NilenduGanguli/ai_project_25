import os
import asyncio
from google import generativeai as genai
from typing import Dict, Any, Optional, List
import json


class GenAIClient:
    """Google GenerativeAI client for Gemini models with structured output support"""
    
    def __init__(self, model_name: str, temperature: float = 0.0, structured_schema: type = None):
        self.model_name = model_name
        self.temperature = temperature
        self.structured_schema = structured_schema
        
        # Configure the API key - check if already set
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Configure genai with the API key (safe to call multiple times)
        genai.configure(api_key=api_key)
        
        # Initialize the model with generation config
        self.generation_config = genai.GenerationConfig(
            temperature=temperature,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
        )
        
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=self.generation_config
        )
    
    async def ainvoke(self, messages: List) -> Any:
        """Async invoke method to maintain compatibility with LangChain interface"""
        try:
            # Convert messages to content parts
            content_parts = self._process_messages(messages)
            
            # Add structured output instructions if needed
            if self.structured_schema:
                schema_prompt = self._get_schema_prompt()
                content_parts = [f"{content_parts[0]}\n\n{schema_prompt}"] + content_parts[1:]
            
            # Generate response using google.generativeai
            response = await asyncio.to_thread(
                self.model.generate_content,
                content_parts
            )
            
            if self.structured_schema:
                return self._parse_structured_response(response.text)
            else:
                return StructuredResponse(content=response.text)
                
        except Exception as e:
            raise Exception(f"Google GenAI generation failed: {str(e)}")
    
    def _process_messages(self, messages: List) -> List:
        """Process messages into content format expected by google.generativeai"""
        content_parts = []
        
        for message in messages:
            if hasattr(message, 'content'):
                if isinstance(message.content, list):
                    for part in message.content:
                        if isinstance(part, dict):
                            if part.get('type') == 'text':
                                content_parts.append(part['text'])
                            elif part.get('type') == 'image_url' and 'image_url' in part:
                                # Handle base64 encoded images (from extraction)
                                image_url = part['image_url']
                                if isinstance(image_url, str) and 'base64' in image_url:
                                    image_data = image_url.split(',')[1] if ',' in image_url else image_url
                                else:
                                    image_data = image_url.get('url', '').split(',')[1] if isinstance(image_url, dict) and ',' in image_url.get('url', '') else str(image_url)
                                
                                content_parts.append({
                                    'mime_type': 'image/jpeg',  # Default to JPEG, should be determined from data
                                    'data': image_data
                                })
                            elif part.get('type') == 'media':
                                # Handle media content (from classification)
                                content_parts.append({
                                    'mime_type': part.get('mime_type', 'application/pdf'),
                                    'data': part.get('data', '')
                                })
                        else:
                            content_parts.append(str(part))
                else:
                    content_parts.append(message.content)
        
        return content_parts
    
    def _get_schema_prompt(self) -> str:
        """Generate JSON schema prompt for structured output"""
        if not self.structured_schema:
            return ""
        
        # Get field hints from the Pydantic model
        schema_info = self.structured_schema.model_json_schema()
        
        prompt = f"""
Please respond with a valid JSON object that matches this schema:
{json.dumps(schema_info, indent=2)}

Ensure your response is a valid JSON object only, with no additional text or explanations.
"""
        return prompt
    
    def _parse_structured_response(self, response_text: str):
        """Parse response into structured format"""
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            parsed_data = json.loads(cleaned_text)
            
            # Return structured response with Pydantic model
            if self.structured_schema:
                return self.structured_schema(**parsed_data)
            else:
                return StructuredResponse(content=cleaned_text, parsed_data=parsed_data)
                
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON from the text
            import re
            json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
            if json_match:
                try:
                    parsed_data = json.loads(json_match.group())
                    if self.structured_schema:
                        return self.structured_schema(**parsed_data)
                    else:
                        return StructuredResponse(content=cleaned_text, parsed_data=parsed_data)
                except:
                    pass
            
            # If all parsing fails, raise an error
            raise ValueError(f"Could not parse structured response: {response_text}")


class StructuredResponse:
    """Response wrapper to maintain compatibility"""
    def __init__(self, content: str, parsed_data: Dict[Any, Any] = None):
        self.content = content
        self.parsed_data = parsed_data or {}
    
    def model_dump_json(self, indent: int = None) -> str:
        """Compatibility method for Pydantic-like interface"""
        return json.dumps(self.parsed_data, indent=indent)


async def get_llm(model_name: str, model_provider: str, temperature: float, structured_schema: type = None):
    """Factory function to create LLM client - maintains same interface as LangChain version"""
    
    if model_provider != "google_genai":
        raise ValueError(f"Unsupported model provider: {model_provider}. Only 'google_genai' is supported.")
    
    # Map model names if needed
    if model_name == "gemini-2.5-flash":
        genai_model_name = "gemini-1.5-flash"
    else:
        genai_model_name = model_name
    
    client = GenAIClient(
        model_name=genai_model_name,
        temperature=temperature,
        structured_schema=structured_schema
    )
    
    # If structured schema is provided, return a wrapper that behaves like LangChain's with_structured_output
    if structured_schema:
        return StructuredGenAIClient(client, structured_schema)
    
    return client


class StructuredGenAIClient:
    """Wrapper that mimics LangChain's with_structured_output behavior"""
    
    def __init__(self, client: GenAIClient, schema: type):
        self.client = client
        self.schema = schema
    
    async def ainvoke(self, messages: List) -> Any:
        """Return structured Pydantic model directly like LangChain"""
        response = await self.client.ainvoke(messages)
        # The client should already return the structured schema when configured
        return response
