"""
Martin Backend API - Simple Working Version
AI-powered prompt optimization for developers
"""

import os
import json
import time
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="Martin API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Enums
class TargetModel(str, Enum):
    GPT4 = "gpt-4"
    CLAUDE3 = "claude-3"
    GEMINI_ULTRA = "gemini-ultra"
    LLAMA3 = "llama-3"
    GROK = "grok"

class SuggestionType(str, Enum):
    GRAMMAR = "grammar"
    CLARITY = "clarity"
    SPECIFICITY = "specificity"
    STRUCTURE = "structure"
    TOKEN_OPTIMIZATION = "token_optimization"
    TECHNICAL_ACCURACY = "technical_accuracy"

class Domain(str, Enum):
    TECHNICAL = "technical"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    CONVERSATIONAL = "conversational"
    CODE_GENERATION = "code_generation"
    DEBUGGING = "debugging"

# Models
class PromptContext(BaseModel):
    domain: Domain
    previous_prompts: List[str] = Field(default_factory=list)
    session_id: Optional[UUID] = None

class AnalysisOptions(BaseModel):
    suggestion_level: str = "moderate"
    preserve_style: bool = True
    optimize_for_tokens: bool = True

class AnalyzeRequest(BaseModel):
    prompt: str
    target_model: TargetModel
    context: PromptContext
    options: AnalysisOptions = Field(default_factory=AnalysisOptions)

class Suggestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: SuggestionType
    original: str
    suggested: str
    confidence: float
    explanation: str
    token_delta: int
    position: Tuple[int, int]
    developer_tip: Optional[str] = None
    code_example: Optional[str] = None

class PromptMetrics(BaseModel):
    clarity_score: float
    specificity_score: float
    token_efficiency: float
    technical_accuracy: float
    estimated_quality_improvement: float
    token_count: int
    estimated_cost: float

class AnalyzeResponse(BaseModel):
    suggestions: List[Suggestion]
    metrics: PromptMetrics
    processing_time_ms: int
    cache_hit: bool = False
    tips: List[str] = Field(default_factory=list)

# Demo analyzer
def analyze_prompt_demo(prompt: str, target_model: TargetModel) -> Dict:
    """Simple demo analysis"""
    suggestions = []
    
    # Basic suggestions
    if "function that" in prompt.lower():
        start = prompt.lower().find("function that")
        suggestions.append(Suggestion(
            type=SuggestionType.CLARITY,
            original="function that",
            suggested="function to",
            confidence=0.85,
            explanation="More concise phrasing",
            token_delta=-1,
            position=(start, start + 13),
            developer_tip="Use infinitive form"
        ))
    
    # Metrics
    word_count = len(prompt.split())
    metrics = PromptMetrics(
        clarity_score=85.0,
        specificity_score=75.0,
        token_efficiency=80.0,
        technical_accuracy=90.0,
        estimated_quality_improvement=15.0,
        token_count=int(word_count * 1.3),
        estimated_cost=0.001
    )
    
    return {
        "suggestions": suggestions,
        "metrics": metrics,
        "tips": ["Be specific", "Use examples", "Define output format"]
    }

# Auth (simplified)
async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    return "demo-token"

# Endpoints
@app.post("/api/v1/analyze")
async def analyze_prompt(request: AnalyzeRequest, token: str = Depends(verify_token)):
    """Analyze prompt and return suggestions"""
    start_time = time.time()
    
    try:
        result = analyze_prompt_demo(request.prompt, request.target_model)
        
        return AnalyzeResponse(
            suggestions=result["suggestions"],
            metrics=result["metrics"],
            processing_time_ms=int((time.time() - start_time) * 1000),
            tips=result["tips"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Martin API",
        "version": "1.0.0",
        "docs": "http://localhost:8000/docs"
    }

if __name__ == "__main__":
    import uvicorn
    
    print("""
🚀 Martin Backend Starting (Simple Version)...
   
📍 API: http://localhost:8000
📚 Docs: http://localhost:8000/docs
❤️  Health: http://localhost:8000/api/v1/health
""")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)