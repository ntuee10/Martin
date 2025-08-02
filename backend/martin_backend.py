"""
Martin Backend API
High-performance prompt analysis service using FastAPI and Grok 3 API
"""

import asyncio
import hashlib
import json
import os
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID, uuid4

import httpx
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from prometheus_client import Counter, Histogram, make_asgi_app
import structlog
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure structured logging
logger = structlog.get_logger()

# Metrics
REQUEST_COUNT = Counter('martin_requests_total', 'Total requests', ['endpoint', 'status'])
REQUEST_LATENCY = Histogram('martin_request_duration_seconds', 'Request latency')
GROK3_LATENCY = Histogram('grok3_request_duration_seconds', 'Grok3 API latency')

# Initialize FastAPI
app = FastAPI(title="Martin API", version="1.0.0")

# CORS configuration for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=json.loads(os.getenv("CORS_ORIGINS", '["chrome-extension://*"]')),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global instances
redis_client = None

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

class SuggestionLevel(str, Enum):
    AGGRESSIVE = "aggressive"
    MODERATE = "moderate"
    CONSERVATIVE = "conservative"

class Domain(str, Enum):
    TECHNICAL = "technical"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    CONVERSATIONAL = "conversational"
    CODE_GENERATION = "code_generation"
    DEBUGGING = "debugging"

# Pydantic models
class PromptContext(BaseModel):
    domain: Domain
    previous_prompts: List[str] = Field(default_factory=list, max_items=10)
    session_id: Optional[UUID] = None
    developer_context: Optional[Dict[str, str]] = None

class AnalysisOptions(BaseModel):
    suggestion_level: SuggestionLevel = SuggestionLevel.MODERATE
    preserve_style: bool = True
    optimize_for_tokens: bool = True
    include_examples: bool = True
    target_token_reduction: Optional[float] = Field(None, ge=0, le=0.5)

class AnalyzeRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)
    target_model: TargetModel
    context: PromptContext
    options: AnalysisOptions = Field(default_factory=AnalysisOptions)

class Suggestion(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: SuggestionType
    original: str
    suggested: str
    confidence: float = Field(..., ge=0, le=1)
    explanation: str
    token_delta: int
    position: Tuple[int, int]
    developer_tip: Optional[str] = None
    code_example: Optional[str] = None

class PromptMetrics(BaseModel):
    clarity_score: float = Field(..., ge=0, le=100)
    specificity_score: float = Field(..., ge=0, le=100)
    token_efficiency: float = Field(..., ge=0, le=100)
    technical_accuracy: float = Field(..., ge=0, le=100)
    estimated_quality_improvement: float = Field(..., ge=0, le=100)
    token_count: int
    estimated_cost: float

class AnalyzeResponse(BaseModel):
    suggestions: List[Suggestion]
    metrics: PromptMetrics
    processing_time_ms: int
    cache_hit: bool = False
    model_specific_tips: List[str] = Field(default_factory=list)

# Grok 3 API Client
class Grok3Client:
    """Client for interacting with Grok 3 API"""
    
    def __init__(self):
        self.api_key = os.getenv("GROK3_API_KEY")
        self.api_url = os.getenv("GROK3_API_URL", "https://api.x.ai/v1")
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        
        self.model_configs = {
            TargetModel.GPT4: {
                "instructions": "Optimize for explicit instructions and clear output format specifications.",
                "focus": ["step-by-step reasoning", "explicit constraints", "output format"]
            },
            TargetModel.CLAUDE3: {
                "instructions": "Optimize for conversational tone and ethical considerations.",
                "focus": ["natural language", "context awareness", "safety"]
            },
            TargetModel.GEMINI_ULTRA: {
                "instructions": "Optimize for multimodal capabilities and long context.",
                "focus": ["visual descriptions", "extended context", "cross-modal reasoning"]
            }
        }
    
    async def analyze_prompt(self, prompt: str, target_model: TargetModel, 
                           context: PromptContext, options: AnalysisOptions) -> Dict:
        """Analyze prompt using Grok 3 API"""
        start_time = time.time()
        
        try:
            # Build the analysis prompt for Grok 3
            system_prompt = self._build_system_prompt(target_model, context, options)
            user_prompt = self._build_user_prompt(prompt, target_model)
            
            # Call Grok 3 API
            response = await self.client.post(
                f"{self.api_url}/chat/completions",
                json={
                    "model": "grok-beta",  # Use the appropriate Grok model
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000,
                    "response_format": {"type": "json_object"}
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Parse Grok 3 response
            grok_response = json.loads(result["choices"][0]["message"]["content"])
            
            # Convert to our format
            suggestions = self._parse_suggestions(grok_response, prompt)
            metrics = self._calculate_metrics(prompt, suggestions, grok_response)
            
            GROK3_LATENCY.observe(time.time() - start_time)
            
            return {
                "suggestions": suggestions,
                "metrics": metrics,
                "model_tips": self._get_model_tips(target_model, context)
            }
            
        except Exception as e:
            logger.error("Grok 3 API error", error=str(e))
            # Fallback to local analysis if Grok 3 fails
            return self._fallback_analysis(prompt, target_model, context, options)
    
    def _build_system_prompt(self, target_model: TargetModel, context: PromptContext, 
                           options: AnalysisOptions) -> str:
        """Build system prompt for Grok 3"""
        model_config = self.model_configs.get(target_model, {})
        
        return f"""You are Martin, an AI prompt optimization assistant for developers.

Analyze the given prompt and provide suggestions to improve it for {target_model.value}.

Target Model Optimization:
{model_config.get('instructions', 'General optimization')}
Focus areas: {', '.join(model_config.get('focus', ['clarity', 'specificity']))}

Context:
- Domain: {context.domain.value}
- Suggestion Level: {options.suggestion_level.value}
- Optimize for Tokens: {options.optimize_for_tokens}
- Include Examples: {options.include_examples}

Provide your response as a JSON object with this structure:
{{
    "suggestions": [
        {{
            "type": "clarity|specificity|structure|token_optimization|technical_accuracy",
            "original_text": "exact text to replace",
            "suggested_text": "improved version",
            "confidence": 0.0-1.0,
            "explanation": "why this change improves the prompt",
            "token_delta": integer,
            "start_position": integer,
            "end_position": integer,
            "developer_tip": "optional tip for developers",
            "code_example": "optional code example"
        }}
    ],
    "analysis": {{
        "overall_quality": 0-100,
        "main_issues": ["list of main issues found"],
        "strengths": ["list of prompt strengths"]
    }}
}}

Focus on developer-specific improvements like:
- Clear variable and function naming in code generation prompts
- Explicit error handling requirements
- Performance constraints and optimization hints
- API design patterns and best practices
- Debugging context and expected behaviors"""
    
    def _build_user_prompt(self, prompt: str, target_model: TargetModel) -> str:
        """Build user prompt for analysis"""
        return f"""Analyze this prompt intended for {target_model.value}:

"{prompt}"

Provide specific, actionable suggestions to improve this prompt for better results."""
    
    def _parse_suggestions(self, grok_response: Dict, original_prompt: str) -> List[Suggestion]:
        """Parse Grok 3 response into suggestions"""
        suggestions = []
        
        for item in grok_response.get("suggestions", []):
            try:
                suggestion = Suggestion(
                    type=SuggestionType(item["type"]),
                    original=item["original_text"],
                    suggested=item["suggested_text"],
                    confidence=item["confidence"],
                    explanation=item["explanation"],
                    token_delta=item["token_delta"],
                    position=(item["start_position"], item["end_position"]),
                    developer_tip=item.get("developer_tip"),
                    code_example=item.get("code_example")
                )
                suggestions.append(suggestion)
            except Exception as e:
                logger.warning("Failed to parse suggestion", error=str(e))
                
        return suggestions
    
    def _calculate_metrics(self, prompt: str, suggestions: List[Suggestion], 
                         grok_response: Dict) -> PromptMetrics:
        """Calculate prompt quality metrics"""
        word_count = len(prompt.split())
        analysis = grok_response.get("analysis", {})
        
        # Use Grok's analysis if available, otherwise calculate
        overall_quality = analysis.get("overall_quality", 70)
        
        # Estimate metrics based on suggestions and analysis
        clarity_score = max(0, overall_quality - len(suggestions) * 5)
        specificity_score = min(100, overall_quality + (word_count * 0.5))
        token_efficiency = max(0, 100 - (word_count - 30) if word_count > 30 else 100)
        technical_accuracy = 100 - sum(1 for s in suggestions if s.type == SuggestionType.TECHNICAL_ACCURACY) * 20
        
        # Estimate token count (rough approximation)
        token_count = int(word_count * 1.3)
        
        # Cost estimation
        cost_per_1k_tokens = 0.01
        estimated_cost = (token_count / 1000) * cost_per_1k_tokens
        
        return PromptMetrics(
            clarity_score=clarity_score,
            specificity_score=specificity_score,
            token_efficiency=token_efficiency,
            technical_accuracy=technical_accuracy,
            estimated_quality_improvement=min(100, len(suggestions) * 15),
            token_count=token_count,
            estimated_cost=round(estimated_cost, 4)
        )
    
    def _get_model_tips(self, target_model: TargetModel, context: PromptContext) -> List[str]:
        """Get model-specific tips"""
        tips = []
        
        if target_model == TargetModel.GPT4:
            tips.extend([
                "Use system messages for consistent behavior",
                "Specify output format explicitly (JSON, markdown, etc.)",
                "Break complex tasks into numbered steps"
            ])
        elif target_model == TargetModel.CLAUDE3:
            tips.extend([
                "Use conversational, polite language",
                "Provide context and examples",
                "Ask for clarification when needed"
            ])
        elif target_model == TargetModel.GROK:
            tips.extend([
                "Be direct and concise",
                "Leverage Grok's real-time knowledge",
                "Use specific technical terminology"
            ])
        
        if context.domain == Domain.CODE_GENERATION:
            tips.extend([
                "Include language and framework versions",
                "Specify error handling requirements",
                "Mention performance constraints"
            ])
        
        return tips[:3]
    
    def _fallback_analysis(self, prompt: str, target_model: TargetModel,
                          context: PromptContext, options: AnalysisOptions) -> Dict:
        """Fallback analysis when Grok 3 is unavailable"""
        # Basic rule-based analysis
        suggestions = []
        
        # Check for common improvements
        if "function that" in prompt.lower():
            start = prompt.lower().find("function that")
            suggestions.append(Suggestion(
                type=SuggestionType.CLARITY,
                original="function that",
                suggested="function to",
                confidence=0.8,
                explanation="More concise phrasing",
                token_delta=-1,
                position=(start, start + 13),
                developer_tip="Use infinitive form for function purposes"
            ))
        
        metrics = PromptMetrics(
            clarity_score=75,
            specificity_score=70,
            token_efficiency=80,
            technical_accuracy=90,
            estimated_quality_improvement=15,
            token_count=len(prompt.split()) * 1.3,
            estimated_cost=0.001
        )
        
        return {
            "suggestions": suggestions,
            "metrics": metrics,
            "model_tips": self._get_model_tips(target_model, context)
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

# Initialize services
grok3_client = None

async def startup_event():
    global redis_client, grok3_client
    
    # Initialize Redis
    redis_client = await redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379"),
        encoding="utf-8",
        decode_responses=True
    )
    
    # Initialize Grok 3 client
    grok3_client = Grok3Client()
    
    logger.info("Martin backend initialized")

async def shutdown_event():
    global redis_client, grok3_client
    
    if redis_client:
        await redis_client.close()
    
    if grok3_client:
        await grok3_client.close()

app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)

# Cache key generation
def generate_cache_key(request: AnalyzeRequest) -> str:
    """Generate cache key for request"""
    key_data = {
        "prompt": request.prompt,
        "target_model": request.target_model.value,
        "domain": request.context.domain.value,
        "options": request.options.dict()
    }
    key_str = json.dumps(key_data, sort_keys=True)
    return f"martin:analysis:{hashlib.sha256(key_str.encode()).hexdigest()}"

# Authentication
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    # TODO: Implement actual JWT verification
    if not credentials.credentials:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return credentials.credentials

# API Endpoints
@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
async def analyze_prompt(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """Analyze prompt and return suggestions"""
    start_time = time.time()
    REQUEST_COUNT.labels(endpoint="/analyze", status="started").inc()
    
    try:
        # Check cache
        cache_key = generate_cache_key(request)
        cached_result = await redis_client.get(cache_key)
        
        if cached_result:
            result = json.loads(cached_result)
            result["cache_hit"] = True
            REQUEST_COUNT.labels(endpoint="/analyze", status="cache_hit").inc()
            return AnalyzeResponse(**result)
        
        # Analyze prompt with Grok 3
        analysis_result = await grok3_client.analyze_prompt(
            request.prompt,
            request.target_model,
            request.context,
            request.options
        )
        
        # Prepare response
        response = AnalyzeResponse(
            suggestions=analysis_result["suggestions"],
            metrics=analysis_result["metrics"],
            processing_time_ms=int((time.time() - start_time) * 1000),
            model_specific_tips=analysis_result["model_tips"]
        )
        
        # Cache result (5 minute TTL)
        background_tasks.add_task(
            redis_client.setex,
            cache_key,
            300,
            response.json()
        )
        
        REQUEST_COUNT.labels(endpoint="/analyze", status="success").inc()
        REQUEST_LATENCY.observe(time.time() - start_time)
        
        return response
        
    except Exception as e:
        REQUEST_COUNT.labels(endpoint="/analyze", status="error").inc()
        logger.error("Analysis failed", error=str(e), request_id=request.context.session_id)
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "grok3_connected": grok3_client is not None
    }

@app.get("/api/v1/models")
async def list_supported_models(token: str = Depends(verify_token)):
    """List supported target models"""
    return {
        "models": [
            {
                "id": model.value,
                "name": model.value.replace("-", " ").title(),
                "description": f"Optimized for {model.value}"
            }
            for model in TargetModel
        ]
    }

# Metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "martin_backend:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("ENVIRONMENT") == "development",
        log_level="info"
    )
