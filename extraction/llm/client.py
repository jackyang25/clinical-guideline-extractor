"""Unified vision client for Anthropic and OpenAI."""

from __future__ import annotations

import base64
from typing import Literal

import anthropic
import openai


PLACEHOLDER_API_KEY = "YOUR_API_KEY"


class VisionClient:
    """Unified client for vision API (Anthropic Claude or OpenAI GPT)."""

    def __init__(
        self,
        api_key: str,
        model: str,
        max_tokens: int,
        provider: Literal["anthropic", "openai"] = "anthropic",
    ) -> None:
        if not api_key or api_key == PLACEHOLDER_API_KEY:
            raise ValueError(f"{provider.title()} API key is required.")

        if not model:
            raise ValueError("Model name is required.")

        self._model = model
        self._max_tokens = max_tokens
        self._provider = provider

        if provider == "anthropic":
            self._client = anthropic.AsyncAnthropic(api_key=api_key)
        elif provider == "openai":
            self._client = openai.AsyncOpenAI(api_key=api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def extract(
        self, prompt: str, image_bytes: bytes, mime_type: str
    ) -> tuple[str, dict]:
        """Send a prompt and image to the vision API.

        Returns:
            Tuple of (response_text, usage_metadata)
        """
        if not image_bytes:
            raise ValueError("Image bytes are empty.")

        if self._provider == "anthropic":
            return await self._extract_anthropic(prompt, image_bytes, mime_type)
        else:
            return await self._extract_openai(prompt, image_bytes, mime_type)

    async def _extract_anthropic(
        self, prompt: str, image_bytes: bytes, mime_type: str
    ) -> tuple[str, dict]:
        """Extract using Anthropic Claude."""
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

    async def _extract_openai(
        self, prompt: str, image_bytes: bytes, mime_type: str
    ) -> tuple[str, dict]:
        """Extract using OpenAI GPT-4o."""
        image_data = base64.b64encode(image_bytes).decode("ascii")

        response = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{image_data}"},
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )

        usage = {
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
        }

        return response.choices[0].message.content, usage


# Backward compatibility alias
AnthropicVisionClient = VisionClient
