"""Pydantic models for request/response schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat request model."""

    message: str = Field(..., min_length=1, max_length=4096, description="User message")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Generation temperature")
    max_tokens: Optional[int] = Field(None, ge=1, le=2048, description="Maximum tokens to generate")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "What is CRISPR-Cas9?",
                    "conversation_id": None,
                    "temperature": 0.7,
                    "max_tokens": 512
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """Chat response model."""

    response: str = Field(..., description="Model response")
    conversation_id: str = Field(..., description="Conversation ID for follow-up")
    model: str = Field(..., description="Model used for generation")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "response": "CRISPR-Cas9 is a revolutionary gene-editing technology...",
                    "conversation_id": "abc123",
                    "model": "sachinbkale27/genetics-llm-lora-merged-v1"
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
