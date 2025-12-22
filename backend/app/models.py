from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class FitnessLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class FitnessGoal(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    GENERAL_FITNESS = "general_fitness"

class DietaryPreference(str, Enum):
    OMNIVORE = "omnivore"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    KETO = "keto"
    PALEO = "paleo"
    MEDITERRANEAN = "mediterranean"

class UserProfile(BaseModel):
    age: Optional[int] = None
    weight: Optional[float] = None  # in kg
    height: Optional[float] = None  # in cm
    fitness_level: Optional[FitnessLevel] = None
    fitness_goals: List[FitnessGoal] = []
    dietary_preferences: List[DietaryPreference] = []
    allergies: List[str] = []
    activity_level: Optional[int] = None  # 1-5 scale
    equipment_available: List[str] = []  # gym equipment available

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    user_profile: Optional[UserProfile] = None
    conversation_history: List[ChatMessage] = []

class HealthRecommendation(BaseModel):
    type: str  # "workout", "nutrition", "meal", "tip"
    title: str
    description: str
    details: Optional[Dict[str, Any]] = {}
    difficulty: Optional[str] = None
    duration: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []
    recommendations: List[HealthRecommendation] = []
    confidence_score: Optional[float] = None