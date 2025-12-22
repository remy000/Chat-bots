from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from app.rag_system import RAGSystem
from app.models import ChatRequest, ChatResponse, UserProfile, HealthRecommendation

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Fitness & Nutrition Chatbot API",
    description="AI-powered chatbot for personalized fitness and nutrition advice",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system
rag_system = RAGSystem()

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup"""
    await rag_system.initialize()

@app.get("/")
async def root():
    return {"message": "Fitness & Nutrition Chatbot API is running!"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for fitness and nutrition queries
    """
    try:
        response = await rag_system.get_response(
            query=request.message,
            user_profile=request.user_profile,
            conversation_history=request.conversation_history
        )
        
        return ChatResponse(
            response=response["answer"],
            sources=response.get("sources", []),
            recommendations=response.get("recommendations", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/profile")
async def update_profile(profile: UserProfile):
    """
    Update user profile for personalized recommendations
    """
    try:
        # Here you would typically save to a database
        return {"message": "Profile updated successfully", "profile": profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommendations/{category}")
async def get_recommendations(category: str, user_profile: Optional[UserProfile] = None):
    """
    Get specific recommendations for fitness or nutrition
    """
    try:
        recommendations = await rag_system.get_category_recommendations(
            category=category,
            user_profile=user_profile
        )
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=os.getenv("HOST", "localhost"), 
        port=int(os.getenv("PORT", 8000)), 
        reload=os.getenv("DEBUG", "True").lower() == "true"
    )