import requests
import json
import time
import re
from typing import Optional, Dict, Any, Tuple
from .llm_client import LLMClient
import logging

logger = logging.getLogger(__name__)

# Constants
DEFAULT_MAX_RETRIES = 3
RATE_LIMIT_WAIT_TIME = 25  # seconds
DEFAULT_WAIT_TIME = 25  # seconds

class GenericOpenAIAPIClient(LLMClient):
    def __init__(self, api_key: str, api_url: str, max_retries: int = DEFAULT_MAX_RETRIES):
        self.api_key = api_key
        self.base_url = api_url.rstrip('/')  # Remove trailing slash if present
        self.generate_url = f"{self.base_url}/chat/completions"
        self.max_retries = max_retries

    def generate(self,
        prompt: str,
        image_path: Optional[str] = None,
        stream: bool = False,
        model: str = "llama3.2-vision",
        temperature: float = 0.2,
        num_predict: int = 256) -> Dict[Any, Any]:
        """Generate response from OpenAI-compatible API."""
        # Prepare request content
        if image_path:
            logger.debug(f"Encoding image: {image_path}")
            base64_image = self.encode_image(image_path)
            logger.debug(f"Image encoded successfully ({len(base64_image)} chars base64)")
            content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]
        else:
            logger.debug("No image provided, sending text-only prompt")
            content = prompt

        # Prepare request data
        data = {
            "model": model,
            "messages": [{"role": "user", "content": content}],
            "stream": stream,
            "temperature": temperature,
            "max_tokens": num_predict
        }
        
        logger.debug(f"Sending request to {self.generate_url}")

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/byjlw/video-analyzer",
            "X-Title": "Video Analyzer",
            "Content-Type": "application/json"
        }

        # Try request with retries
        for attempt in range(self.max_retries):
            try:
                response = requests.post(self.generate_url, headers=headers, json=data)
                response.raise_for_status()
                
                # Parse successful response
                try:
                    json_response = response.json()
                    
                    logger.debug(f"API response status: {response.status_code}")
                    logger.debug(f"Response keys: {json_response.keys()}")
                    
                    if 'error' in json_response:
                        logger.error(f"API returned error: {json_response['error']}")
                        raise Exception(f"API error: {json_response['error']}")
                    
                    if stream:
                        return self._handle_streaming_response(response)
                    
                    if 'choices' not in json_response or not json_response['choices']:
                        logger.warning("No choices in API response")
                        raise Exception("No choices in response")
                        
                    choice = json_response['choices'][0]
                    logger.debug(f"Choice keys: {choice.keys()}")
                    
                    message = choice.get('message', {})
                    logger.debug(f"Message type: {type(message)}, Message keys: {message.keys() if isinstance(message, dict) else 'Not a dict'}")
                    
                    if not isinstance(message, dict) or 'content' not in message:
                        logger.warning(f"Response message missing content. Type: {type(message)}, Keys: {message.keys() if isinstance(message, dict) else 'N/A'}")
                        raise Exception("No content in response message")
                    
                    response_content = message['content']
                    logger.debug(f"API returned response ({len(response_content)} chars)")
                    return {"response": response_content}
                    
                except json.JSONDecodeError:
                    raise Exception(f"Invalid JSON response: {response.text}")
                    
            except Exception as e:
                if attempt == self.max_retries - 1:  # Last attempt
                    raise Exception(f"An error occurred: {str(e)}")
                
                # Get wait time based on error
                wait_time = RATE_LIMIT_WAIT_TIME
                if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 429:
                    # Try to get wait time from Retry-After header
                    if 'Retry-After' in e.response.headers:
                        try:
                            wait_time = int(e.response.headers['Retry-After'])
                            logger.info(f"Using Retry-After header value: {wait_time} seconds")
                        except (ValueError, TypeError):
                            logger.warning("Invalid Retry-After header value, using default wait time")
                else:
                    wait_time = DEFAULT_WAIT_TIME
                
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                logger.warning(f"Waiting {wait_time} seconds before retry")
                time.sleep(wait_time)

    def _handle_streaming_response(self, response: requests.Response) -> Dict[Any, Any]:
        """Handle streaming response from API.
        
        Args:
            response: Streaming response from API
            
        Returns:
            Dict containing accumulated response
        """
        accumulated_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    json_response = json.loads(line.decode('utf-8'))
                    if 'choices' in json_response and len(json_response['choices']) > 0:
                        delta = json_response['choices'][0].get('delta', {})
                        if 'content' in delta:
                            accumulated_response += delta['content']
                except json.JSONDecodeError:
                    continue

        return {"response": accumulated_response}
