"""FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse

from app.config import get_settings
from app.routes import chat, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Get first API key for Swagger UI (if available)
default_api_key = settings.api_keys_list[0] if settings.api_keys_list else ""

# Create FastAPI app (disable default docs to use custom)
app = FastAPI(
    title="GeneticLLM API",
    description="Chat API for genetics and genomics Q&A powered by fine-tuned LLM",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url="/redoc",
)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with pre-filled API key."""
    return HTMLResponse(
        content=f"""
<!DOCTYPE html>
<html>
<head>
    <title>{app.title} - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: "/openapi.json",
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout",
                persistAuthorization: true,
                tryItOutEnabled: true,
                onComplete: function() {{
                    // Auto-fill API key from .env
                    const apiKey = "{default_api_key}";
                    if (apiKey) {{
                        ui.preauthorizeApiKey("APIKeyHeader", apiKey);
                    }}
                }}
            }});
            window.ui = ui;
        }};
    </script>
</body>
</html>
        """,
        media_type="text/html",
    )


def custom_openapi():
    """Custom OpenAPI schema with API key security."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API Key for authentication",
        }
    }

    # Apply security to all paths except health endpoints
    for path in openapi_schema["paths"]:
        if path not in ["/health", "/ready"]:
            for method in openapi_schema["paths"][path]:
                openapi_schema["paths"][path][method]["security"] = [{"APIKeyHeader": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(chat.router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    settings = get_settings()
    logger.info(f"Starting GeneticLLM API")
    logger.info(f"Model: {settings.model_name}")
    logger.info(f"API keys configured: {len(settings.api_keys_list)}")

    if not settings.hf_token:
        logger.warning("HF_TOKEN not set - API calls may fail")

    if not settings.api_keys_list:
        logger.warning("No API_KEYS configured - running in development mode")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down GeneticLLM API")


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        reload=True,
    )
