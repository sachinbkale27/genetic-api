"""Chat endpoint for genetics Q&A."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import verify_api_key
from app.config import get_settings
from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from app.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid or missing API key"},
        500: {"model": ErrorResponse, "description": "Model inference error"},
    },
)
async def chat(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key),
) -> ChatResponse:
    """Chat with the genetics LLM.

    Send a message about genetics, genomics, or molecular biology
    and receive an AI-generated response.

    Args:
        request: Chat request with message and optional parameters
        api_key: Validated API key from header

    Returns:
        ChatResponse with the model's response
    """
    settings = get_settings()
    llm_service = get_llm_service()

    try:
        response_text, conversation_id = await llm_service.generate_response(
            message=request.message,
            conversation_id=request.conversation_id,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            model=settings.model_name,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
