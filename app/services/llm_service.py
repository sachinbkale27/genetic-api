"""HuggingFace Inference API service."""

import logging
import uuid
from typing import Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with the genetics LLM via HuggingFace Inference API."""

    def __init__(self):
        """Initialize the LLM service."""
        self.settings = get_settings()
        self.model = self.settings.model_name
        # Use dedicated endpoint if available
        self.use_dedicated_endpoint = bool(self.settings.hf_endpoint_url)
        if self.use_dedicated_endpoint:
            self.api_url = self.settings.hf_endpoint_url
        else:
            self.api_url = "https://router.huggingface.co/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.settings.hf_token}",
            "Content-Type": "application/json",
        }

    async def generate_response(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> tuple[str, str]:
        """Generate a response from the genetics LLM.

        Args:
            message: User message
            conversation_id: Optional conversation ID
            temperature: Generation temperature (defaults to settings)
            max_tokens: Max tokens to generate (defaults to settings)

        Returns:
            Tuple of (response text, conversation_id)

        Raises:
            Exception: If generation fails
        """
        # Use provided values or fall back to settings
        temp = temperature if temperature is not None else self.settings.temperature
        max_new = max_tokens if max_tokens is not None else self.settings.max_new_tokens

        # Generate or use existing conversation ID
        conv_id = conversation_id or str(uuid.uuid4())[:8]

        # Format the prompt
        prompt = self._format_prompt(message)

        try:
            logger.info(f"Generating response for conversation {conv_id}")
            logger.info(f"Using model: {self.model}")
            logger.info(f"API URL: {self.api_url}")

            # Use different format based on endpoint type
            if self.use_dedicated_endpoint:
                # TGI text generation format
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": max_new,
                        "temperature": temp,
                        "do_sample": True,
                        "return_full_text": False,
                        "repetition_penalty": 1.2,
                    },
                }
            else:
                # OpenAI-compatible chat completions format
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.settings.system_prompt},
                        {"role": "user", "content": message},
                    ],
                    "max_tokens": max_new,
                    "temperature": temp,
                }

            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                )

            logger.info(f"Response status: {response.status_code}")

            logger.info(f"Response body: {response.text[:500] if response.text else 'empty'}")

            if response.status_code != 200:
                error_msg = response.text or f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", error_msg) if isinstance(error_data.get("error"), dict) else error_data.get("error", error_msg)
                except:
                    pass
                logger.error(f"API error: {response.status_code} - {error_msg}")
                raise Exception(f"HuggingFace API error ({response.status_code}): {error_msg}")

            data = response.json()
            logger.info(f"Response data: {data}")

            # Extract response based on endpoint type
            if self.use_dedicated_endpoint:
                # TGI format: [{"generated_text": "..."}]
                if isinstance(data, list) and len(data) > 0:
                    response_text = data[0].get("generated_text", "")
                else:
                    response_text = data.get("generated_text", str(data))
            else:
                # OpenAI format
                response_text = data["choices"][0]["message"]["content"]

            # Clean up the response
            response_text = self._clean_response(response_text or "")

            if not response_text:
                raise Exception("Model returned empty response.")

            logger.info(f"Generated {len(response_text)} chars for conversation {conv_id}")
            return response_text, conv_id

        except httpx.TimeoutException:
            raise Exception("Request timed out. The model may be loading - please try again.")
        except Exception as e:
            import traceback
            logger.error(f"Generation error: {traceback.format_exc()}")
            raise Exception(f"Failed to generate response: {str(e)}")

    def _format_prompt(self, message: str) -> str:
        """Format the prompt for the model.

        Args:
            message: User message

        Returns:
            Formatted prompt string
        """
        # Qwen2 chat format
        return f"""<|im_start|>system{self.settings.system_prompt}<|im_end|><|im_start|>user{message}<|im_end|><|im_start|>assistant"""

    def _clean_response(self, response: str) -> str:
        """Clean up the model response.

        Args:
            response: Raw model response

        Returns:
            Cleaned response text
        """
        # Remove any trailing special tokens
        response = response.strip()

        # Remove end tokens if present
        for token in ["<|im_end|>", "<|endoftext|>", "</s>"]:
            if response.endswith(token):
                response = response[: -len(token)].strip()

        return response


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get the LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
