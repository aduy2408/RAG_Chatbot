from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import Optional
import uvicorn

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.chatbot_core import APECChatbot
from modules.utils import detect_language, get_context_suggestions
from modules.config import ChatbotConfig

app = FastAPI(
    title="APEC 2025 RAG Chatbot API",
    description="API backend for APEC 2025 multilingual RAG chatbot",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global chatbot instance
chatbot = None

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    auto_detect: bool = True
    preferred_language: str = "vi"
    top_k: int = 5

class ChatResponse(BaseModel):
    answer: str
    sources: list
    num_sources: int
    detected_language: str
    response_time: Optional[float] = None

class SuggestionsRequest(BaseModel):
    response_content: str
    language: str

class SuggestionsResponse(BaseModel):
    suggestions: list

@app.on_event("startup")
async def startup_event():
    """Initialize the chatbot when the API starts"""
    global chatbot
    try:
        # Validate environment
        is_valid, message = ChatbotConfig.validate()
        if not is_valid:
            raise Exception(f"Configuration error: {message}")
        
        # Initialize chatbot
        chatbot = APECChatbot(
            api_key=ChatbotConfig.GOOGLE_API_KEY,
            persist_directory=ChatbotConfig.VECTOR_DB_PATH
        )
        print("Chatbot initialized successfully")
        
    except Exception as e:
        print(f"Failed to initialize chatbot: {str(e)}")
        raise e

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "APEC 2025 RAG Chatbot API is running",
        "status": "healthy",
        "chatbot_ready": chatbot is not None and chatbot.is_ready()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    return {
        "status": "healthy",
        "chatbot_ready": chatbot.is_ready(),
        "vector_store_count": chatbot.get_collection_count(),
        "supported_languages": ChatbotConfig.SUPPORTED_LANGUAGES
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint - receives user message and returns RAG response
    Handles multilingual processing and dataset routing
    """
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        import time
        start_time = time.time()
        
        # Get response from chatbot
        response = chatbot.query(
            question=request.message,
            top_k=request.top_k,
            auto_detect=request.auto_detect,
            preferred_language=request.preferred_language
        )
        
        end_time = time.time()
        response_time = round(end_time - start_time, 2)
        
        return ChatResponse(
            answer=response["answer"],
            sources=response["sources"],
            num_sources=response["num_sources"],
            detected_language=response["detected_language"],
            response_time=response_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@app.post("/suggestions", response_model=SuggestionsResponse)
async def suggestions_endpoint(request: SuggestionsRequest):
    """
    Suggestions endpoint - returns context-aware follow-up questions (hardcoded + LLM-generated)
    """
    try:
        # Pass the LLM instance to enable LLM-generated suggestions
        llm_instance = chatbot.llm if chatbot else None

        suggestions = get_context_suggestions(
            response_content=request.response_content,
            language=request.language,
            llm=llm_instance
        )

        return SuggestionsResponse(suggestions=suggestions)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")

@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "supported_languages": ChatbotConfig.SUPPORTED_LANGUAGES,
        "default_language": ChatbotConfig.DEFAULT_LANGUAGE
    }

if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "api_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
