"""
FastAPI app entrypoint for the conversational booking assistant.
Now with defensive handling of malformed input and clearer logging.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langgraph_agent import handle_user_message
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for all origins (good for frontend communication)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/chat")
async def chat(request: Request):
    """
    Chat endpoint for receiving user messages.
    Expects JSON: { "message": "..." }
    Returns JSON: { "reply": "..." }
    """
    # Accepts a POST request from the frontend containing a user message.
    # Validates the message, routes it through the language agent for interpretation,
    # and returns a reply in JSON format. Handles missing input or internal errors gracefully.
    try:
        data = await request.json()
        user_msg = data.get("message", "").strip()

        # Edge case: empty or missing message
        if not user_msg:
            raise HTTPException(status_code=400, detail="Missing or empty 'message'.")

        logger.info(f"📥 Incoming user message: {user_msg}")
        reply = await handle_user_message(user_msg)
        return {"reply": reply}
    except HTTPException as http_err:
        logger.warning(f"⚠️ Bad Request: {http_err.detail}")
        raise http_err

    except Exception as e:
        logger.exception("🚨 Unexpected server error")
        return {"reply": "⚠️ Internal server error. Please try again later."}
