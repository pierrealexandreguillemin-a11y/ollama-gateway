"""
Ollama Gateway - OpenAI-compatible API for local Ollama models
Enables Claude-Code, Continue.dev, and other tools to use local models
"""

import json
import logging
import os
import time

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from router import IntelligentRouter

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load config
with open("config.json") as f:
    config = json.load(f)

app = FastAPI(
    title="Ollama Gateway",
    description="OpenAI-compatible gateway for local Ollama models with intelligent routing",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize router
router = IntelligentRouter()

# Configuration from environment or config.json
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", config["ollama_base_url"])
GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", config.get("gateway_port", 4000)))
ENABLE_STREAMING = (
    os.getenv("ENABLE_STREAMING", str(config.get("enable_streaming", True))).lower() == "true"
)
ENABLE_LOGGING = (
    os.getenv("ENABLE_LOGGING", str(config.get("enable_logging", True))).lower() == "true"
)


@app.get("/")
async def root():
    """Redirect to Pilot Studio if available, otherwise show API info"""
    import os

    if os.path.exists("studio/index.html"):
        from fastapi.responses import RedirectResponse

        return RedirectResponse(url="/studio/")
    return {
        "status": "healthy",
        "service": "Ollama Gateway",
        "version": "1.0.0",
        "ollama_url": OLLAMA_URL,
        "models_configured": len(config["models"]),
        "endpoints": {
            "api": "/v1/chat/completions",
            "models": "/v1/models",
            "health": "/health",
            "studio": "/studio/",
        },
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            ollama_models = response.json().get("models", [])

        return {
            "status": "healthy",
            "ollama_connected": True,
            "ollama_models_count": len(ollama_models),
            "configured_models": len(config["models"]),
            "routing_enabled": True,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "ollama_connected": False, "error": str(e)},
        )


@app.get("/v1/models")
async def list_models():
    """OpenAI-compatible models endpoint"""
    models_info = router.get_available_models()

    # Format as OpenAI response
    return {
        "object": "list",
        "data": [
            {
                "id": model["name"],
                "object": "model",
                "created": int(time.time()),
                "owned_by": "local",
                "permission": [],
                "root": model["name"],
                "parent": None,
                "metadata": {
                    "role": model["role"],
                    "priority": model["priority"],
                    "tags": model["tags"],
                },
            }
            for model in models_info["models"]
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completion(request: Request):
    """
    OpenAI-compatible chat completions endpoint
    Automatically routes to best local model based on prompt content
    """
    try:
        payload = await request.json()

        if ENABLE_LOGGING:
            logger.info("Received chat completion request")

        # Extract user message for routing
        messages = payload.get("messages", [])
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        # Get last user message for routing decision
        user_message = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")

        # Intelligent routing
        requested_model = payload.get("model")
        selected_model, routing_reason = router.route(user_message, requested_model)

        if ENABLE_LOGGING:
            logger.info(f"Routing: {selected_model} - {routing_reason}")

        # Prepare Ollama request
        ollama_payload = {
            "model": selected_model,
            "messages": messages,
            "stream": payload.get("stream", False),
            "options": {
                "temperature": payload.get("temperature", 0.7),
                "top_p": payload.get("top_p", 0.9),
                "max_tokens": payload.get("max_tokens", 2048),
            },
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            if ollama_payload["stream"] and ENABLE_STREAMING:
                # Streaming response
                response = await client.post(
                    f"{OLLAMA_URL}/api/chat", json=ollama_payload, timeout=None
                )

                async def generate():
                    async for chunk in response.aiter_lines():
                        if chunk:
                            try:
                                data = json.loads(chunk)
                                # Convert to OpenAI format
                                openai_chunk = {
                                    "id": f"chatcmpl-{int(time.time())}",
                                    "object": "chat.completion.chunk",
                                    "created": int(time.time()),
                                    "model": selected_model,
                                    "choices": [
                                        {
                                            "index": 0,
                                            "delta": {
                                                "content": data.get("message", {}).get(
                                                    "content", ""
                                                )
                                            },
                                            "finish_reason": "stop" if data.get("done") else None,
                                        }
                                    ],
                                }
                                yield f"data: {json.dumps(openai_chunk)}\n\n"

                                if data.get("done"):
                                    yield "data: [DONE]\n\n"
                                    break
                            except json.JSONDecodeError:
                                continue

                return StreamingResponse(
                    generate(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Access-Control-Allow-Origin": "*",
                    },
                )

            else:
                # Non-streaming response
                response = await client.post(f"{OLLAMA_URL}/api/chat", json=ollama_payload)

                ollama_data = response.json()

                # Convert to OpenAI format
                openai_response = {
                    "id": f"chatcmpl-{int(time.time())}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": selected_model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": ollama_data.get("message", {}).get("content", ""),
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {
                        "prompt_tokens": ollama_data.get("prompt_eval_count", 0),
                        "completion_tokens": ollama_data.get("eval_count", 0),
                        "total_tokens": ollama_data.get("prompt_eval_count", 0)
                        + ollama_data.get("eval_count", 0),
                    },
                    "metadata": {
                        "routing_reason": routing_reason,
                        "selected_model": selected_model,
                    },
                }

                return JSONResponse(openai_response)

    except httpx.RequestError as e:
        logger.error(f"Ollama request failed: {e}")
        raise HTTPException(status_code=503, detail=f"Ollama service unavailable: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/gateway/models")
async def gateway_models():
    """Gateway-specific endpoint to view routing configuration"""
    return router.get_available_models()


@app.post("/gateway/route")
async def test_routing(request: Request):
    """Test endpoint to see which model would be selected for a prompt"""
    payload = await request.json()
    prompt = payload.get("prompt", "")

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt required")

    model, reason = router.route(prompt)

    return {"prompt": prompt, "selected_model": model, "reason": reason}


# Mount Pilot Studio (must be AFTER all API routes to avoid conflicts)
if os.path.exists("studio"):
    from fastapi.staticfiles import StaticFiles

    app.mount("/studio", StaticFiles(directory="studio", html=True), name="studio")
    logger.info("✅ Pilot Studio mounted at /studio")
else:
    logger.warning("⚠️  studio/ directory not found - dashboard unavailable")


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting Ollama Gateway on port {GATEWAY_PORT}")
    logger.info(f"Ollama URL: {OLLAMA_URL}")
    logger.info(f"Configured models: {len(config['models'])}")
    logger.info(f"Default model: {config['default_model']}")
    logger.info(f"Streaming: {'enabled' if ENABLE_STREAMING else 'disabled'}")
    logger.info(f"Dashboard: http://localhost:{GATEWAY_PORT}/studio")

    uvicorn.run(app, host="0.0.0.0", port=GATEWAY_PORT, log_level="info")
