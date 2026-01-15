"""Anthropic vision client wrapper."""

from __future__ import annotations

import base64

import anthropic


PLACEHOLDER_API_KEY = "YOUR_API_KEY"


class AnthropicVisionClient:
    """Client wrapper for Anthropic vision models."""

    def __init__(self, api_key: str, model: str, max_tokens: int) -> None:
        if not api_key:
            raise ValueError("Anthropic API key is required.")

        if api_key == PLACEHOLDER_API_KEY:
            raise ValueError("Anthropic API key is a placeholder.")

        if not model:
            raise ValueError("Anthropic model name is required.")

        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens

    async def extract(
        self, prompt: str, image_bytes: bytes, mime_type: str
    ) -> tuple[str, dict]:
        """Send a prompt and image to the Anthropic API.
        
        Returns:
            Tuple of (response_text, usage_metadata)
        """

        if not image_bytes:
            raise ValueError("Image bytes are empty.")

        image_data = base64.b64encode(image_bytes).decode("ascii")
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": image_data,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        
        usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }
        
        return response.content[0].text, usage
