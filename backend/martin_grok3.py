"""
Martin Backend with Full Grok3 Integration
AI-powered prompt optimization using Grok3 API
"""

import os
import json
import time
import asyncio
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Martin API - Grok3 Powered",
    version="2.0.0",
    description="AI prompt optimization powered by Grok3"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your extension ID
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
    CLAUDE_CODE = "claude-code"  # Added for Cursor/Claude coding
    CURSOR = "cursor"  # Added for Cursor IDE
    GEMINI = "gemini"
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

# Pydantic Models
class PromptContext(BaseModel):
    domain: Domain = Domain.TECHNICAL
    previous_prompts: List[str] = Field(default_factory=list)
    session_id: Optional[str] = None

class AnalysisOptions(BaseModel):
    suggestion_level: str = "moderate"
    preserve_style: bool = True
    optimize_for_tokens: bool = True
    include_examples: bool = True
    max_suggestions: int = 5

class AnalyzeRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)
    target_model: TargetModel = TargetModel.GPT4
    context: PromptContext = Field(default_factory=PromptContext)
    options: AnalysisOptions = Field(default_factory=AnalysisOptions)

class Suggestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
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
    tips: List[str] = Field(default_factory=list)

# Grok3 API Client
class Grok3Analyzer:
    """Grok3 API integration for prompt analysis"""
    
    def __init__(self):
        self.api_key = os.getenv("GROK3_API_KEY", "")
        self.api_url = os.getenv("GROK3_API_URL", "https://api.x.ai/v1")
        self.model = "grok-beta"  # or "grok-2" depending on availability
        
        if not self.api_key or self.api_key == "your_grok3_api_key_here":
            self.client = None
            print("⚠️  No valid Grok3 API key found - running in demo mode")
        else:
            self.client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            print("✅ Grok3 client initialized")
    
    async def analyze_prompt(
        self,
        prompt: str,
        target_model: TargetModel,
        context: PromptContext,
        options: AnalysisOptions
    ) -> Dict:
        """Analyze prompt using Grok3 API"""
        
        if not self.client:
            return self._demo_analysis(prompt, target_model)
        
        try:
            # Build the analysis request for Grok3
            system_message = self._build_system_message(target_model, context, options)
            user_message = self._build_user_message(prompt, target_model)
            
            # Call Grok3 API
            response = await self.client.post(
                f"{self.api_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000,
                    "stream": False
                }
            )
            
            if response.status_code != 200:
                print(f"Grok3 API error: {response.status_code} - {response.text}")
                return self._demo_analysis(prompt, target_model)
            
            # Parse Grok3 response
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Try to parse as JSON
            try:
                # Grok3 might return markdown-wrapped JSON
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                analysis = json.loads(content)
                return self._process_grok3_response(analysis, prompt)
            except json.JSONDecodeError:
                # If not JSON, parse the text response
                return self._parse_text_response(content, prompt)
                
        except Exception as e:
            print(f"Grok3 API error: {str(e)}")
            return self._demo_analysis(prompt, target_model)
    
    def _build_system_message(
        self,
        target_model: TargetModel,
        context: PromptContext,
        options: AnalysisOptions
    ) -> str:
        """Build system message for Grok3"""
        
        model_tips = {
            TargetModel.GPT4: "Remove ALL unnecessary words. Start with action verbs. Specify EXACT output format.",
            TargetModel.CLAUDE3: "Be direct but include context. Use 'Code:' prefix for code requests. Specify language and framework versions.",
            TargetModel.GEMINI: "Extremely concise. Use bullet points. Include file types and structure requirements.",
            TargetModel.GROK: "Ultra-direct language. No pleasantries. Technical terms only."
        }
        
        # For code-specific models like Cursor/Claude Code
        code_assistant_prompt = """You are Martin, a prompt optimization system for developers using AI coding assistants (Cursor, Claude Code, GitHub Copilot).

CRITICAL REQUIREMENTS:
1. REMOVE all fluff words: "please", "could you", "I would like", "help me"
2. START with action verb: "Create", "Fix", "Refactor", "Implement", "Debug"
3. BE SPECIFIC: Include exact function names, types, error messages, file paths
4. USE this format for code requests:
   [ACTION] [WHAT] [SPECIFICATIONS] [CONSTRAINTS] [OUTPUT]

EXAMPLES OF OPTIMIZATION:

BAD: "Could you please help me create a function that processes user data?"
GOOD: "Create processUserData(users: User[]): ProcessedData[] - validate emails, remove duplicates, sort by created_at DESC"

BAD: "I'm having trouble with my React component"
GOOD: "Fix React useState infinite loop in UserDashboard.tsx line 45 - deps array missing userId"

BAD: "Write code to connect to a database"
GOOD: "Implement PostgreSQL connection pool: max 10 connections, 30s timeout, SSL required, return typed client"
"""
        
        if context.domain in [Domain.CODE_GENERATION, Domain.DEBUGGING] or "claude" in target_model.value.lower():
            base_prompt = code_assistant_prompt
        else:
            base_prompt = f"You are Martin, optimizing prompts for {target_model.value}."
        
        return f"""{base_prompt}

ANALYZE this prompt for {target_model.value}. Focus on:
{model_tips.get(target_model, "Maximum clarity and minimal tokens")}

OUTPUT FORMAT (JSON):
{{
    "suggestions": [
        {{
            "type": "clarity|specificity|structure|token_optimization|technical_accuracy",
            "original_text": "exact problematic text",
            "suggested_text": "optimized replacement",
            "explanation": "why this improves prompt effectiveness",
            "confidence": 0.8-1.0,
            "token_delta": -X (always negative for optimization),
            "developer_tip": "specific tip for this optimization pattern"
        }}
    ],
    "overall_analysis": {{
        "main_issues": ["verbose language", "missing specifications", "unclear output format"],
        "strengths": ["technical accuracy", "includes constraints"],
        "clarity_score": 0-100,
        "specificity_score": 0-100,
        "technical_accuracy_score": 0-100,
        "optimized_prompt": "COMPLETE REWRITTEN PROMPT - MUST BE 30-50% SHORTER"
    }}
}}

RULES:
1. Every suggestion MUST reduce tokens (negative token_delta)
2. Remove ALL polite language, fillers, redundancies
3. Convert questions to commands
4. Add specific types, formats, constraints
5. Include example output format when applicable
6. For code: ALWAYS specify language, framework, error handling
7. Minimum 3 suggestions, maximum {options.max_suggestions}
8. The "optimized_prompt" field MUST contain the ENTIRE prompt rewritten optimally

BE RUTHLESS in optimization. Professional developers want MAXIMUM efficiency."""
    
    def _build_user_message(self, prompt: str, target_model: TargetModel) -> str:
        """Build user message for analysis"""
        
        # Provide examples for specific coding assistants
        examples = ""
        if target_model == TargetModel.CLAUDE3 or "code" in prompt.lower():
            examples = """
CONTEXT: User is writing prompts for AI coding assistants (Cursor, Claude, GitHub Copilot)

OPTIMIZATION EXAMPLES:
- "Can you help me create a React component for user authentication?" 
  → "Create React AuthForm component: email/password inputs, JWT token handling, TypeScript, Tailwind CSS"

- "I need a function to process CSV files"
  → "Implement processCSV(file: File): Promise<ParsedData[]> - parse with PapaParse, validate headers, handle errors"

- "Fix the bug in my code"
  → "Debug TypeError line 45 UserService.ts - undefined userId in fetchUser(), add null check"
"""
        
        return f"""{examples}

PROMPT TO OPTIMIZE:
---
{prompt}
---

Transform this into a succinct, professional prompt optimized for {target_model.value}.
Requirements:
1. Remove ALL unnecessary words
2. Start with action verb
3. Include specific types, parameters, constraints
4. Specify exact output format
5. Add error handling requirements if applicable
6. Make it 30-50% shorter while MORE specific

Provide the complete analysis with the optimized version."""
    
    def _process_grok3_response(self, analysis: Dict, original_prompt: str) -> Dict:
        """Process structured response from Grok3"""
        suggestions = []
        
        # If we have an optimized_prompt, create a main suggestion for it
        overall = analysis.get("overall_analysis", {})
        optimized_prompt = overall.get("optimized_prompt", "")
        
        if optimized_prompt and optimized_prompt != original_prompt:
            # Add the complete rewrite as the first suggestion
            suggestions.append(Suggestion(
                type=SuggestionType.STRUCTURE,
                original=original_prompt[:100] + "..." if len(original_prompt) > 100 else original_prompt,
                suggested=optimized_prompt,
                confidence=0.95,
                explanation="Complete optimized rewrite for maximum efficiency",
                token_delta=len(optimized_prompt.split()) - len(original_prompt.split()),
                position=(0, len(original_prompt)),
                developer_tip="Use this optimized version directly for best results"
            ))
        
        # Process individual suggestions
        for idx, item in enumerate(analysis.get("suggestions", [])[:5]):
            try:
                # Find position in original prompt
                original_text = item.get("original_text", "")
                position = self._find_text_position(original_prompt, original_text)
                
                suggestion = Suggestion(
                    type=SuggestionType(item.get("type", "clarity")),
                    original=original_text,
                    suggested=item.get("suggested_text", ""),
                    confidence=float(item.get("confidence", 0.7)),
                    explanation=item.get("explanation", ""),
                    token_delta=int(item.get("token_delta", 0)),
                    position=position,
                    developer_tip=item.get("developer_tip")
                )
                suggestions.append(suggestion)
            except Exception as e:
                print(f"Error parsing suggestion {idx}: {e}")
                continue
        
        # Extract metrics from analysis
        word_count = len(original_prompt.split())
        optimized_word_count = len(optimized_prompt.split()) if optimized_prompt else word_count
        
        metrics = PromptMetrics(
            clarity_score=float(overall.get("clarity_score", 80)),
            specificity_score=float(overall.get("specificity_score", 75)),
            token_efficiency=self._calculate_token_efficiency(optimized_word_count),
            technical_accuracy=float(overall.get("technical_accuracy_score", 90)),
            estimated_quality_improvement=min(100, len(suggestions) * 15),
            token_count=int(optimized_word_count * 1.3),
            estimated_cost=round(optimized_word_count * 0.00015, 4)
        )
        
        # Professional tips for developers
        tips = [
            "Always start prompts with action verbs",
            "Include specific types and return values",
            "Add error handling requirements explicitly"
        ]
        
        # Add any specific tips from the analysis
        if overall.get("strengths"):
            tips = overall.get("strengths", [])[:2] + [tips[0]]
        
        return {
            "suggestions": suggestions,
            "metrics": metrics,
            "tips": tips
        }
    
    def _parse_text_response(self, content: str, original_prompt: str) -> Dict:
        """Parse non-JSON text response from Grok3"""
        # This is a fallback for when Grok3 returns plain text
        suggestions = []
        
        # Look for suggestion patterns in the text
        lines = content.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['suggest', 'improve', 'change', 'replace']):
                # Create a basic suggestion from the line
                suggestion = Suggestion(
                    type=SuggestionType.CLARITY,
                    original=original_prompt[:30] + "...",
                    suggested="See explanation",
                    confidence=0.7,
                    explanation=line.strip(),
                    token_delta=0,
                    position=(0, 30)
                )
                suggestions.append(suggestion)
                if len(suggestions) >= 3:
                    break
        
        return self._create_basic_response(suggestions, original_prompt)
    
    def _find_text_position(self, text: str, substring: str) -> Tuple[int, int]:
        """Find position of substring in text"""
        start = text.lower().find(substring.lower())
        if start == -1:
            return (0, min(50, len(text)))
        return (start, start + len(substring))
    
    def _calculate_token_efficiency(self, word_count: int) -> float:
        """Calculate token efficiency score"""
        if word_count <= 30:
            return 100.0
        elif word_count <= 50:
            return 90.0
        elif word_count <= 100:
            return 70.0
        else:
            return max(40.0, 100 - (word_count - 100) * 0.5)
    
    def _create_basic_response(self, suggestions: List[Suggestion], prompt: str) -> Dict:
        """Create a basic response structure"""
        word_count = len(prompt.split())
        
        metrics = PromptMetrics(
            clarity_score=85.0,
            specificity_score=75.0,
            token_efficiency=self._calculate_token_efficiency(word_count),
            technical_accuracy=90.0,
            estimated_quality_improvement=len(suggestions) * 10,
            token_count=int(word_count * 1.3),
            estimated_cost=round(word_count * 0.00015, 4)
        )
        
        tips = [
            "Be specific about the expected output format",
            "Include examples when possible",
            "Break complex tasks into steps"
        ]
        
        return {
            "suggestions": suggestions,
            "metrics": metrics,
            "tips": tips
        }
    
    def _demo_analysis(self, prompt: str, target_model: TargetModel) -> Dict:
        """Demo analysis when no API key is available"""
        suggestions = []
        
        # Professional, succinct optimizations
        prompt_lower = prompt.lower()
        
        # Remove polite language
        politeness_words = ["please", "could you", "would you", "can you", "i would like", "help me"]
        for word in politeness_words:
            if word in prompt_lower:
                start = prompt_lower.find(word)
                suggestions.append(Suggestion(
                    type=SuggestionType.TOKEN_OPTIMIZATION,
                    original=prompt[start:start + len(word)],
                    suggested="",
                    confidence=0.95,
                    explanation="Remove unnecessary polite language - be direct",
                    token_delta=-len(word.split()),
                    position=(start, start + len(word)),
                    developer_tip="AI coding assistants don't need politeness - save tokens"
                ))
                break
        
        # Check for vague function descriptions
        if "function that" in prompt_lower:
            start = prompt_lower.find("function that")
            suggestions.append(Suggestion(
                type=SuggestionType.CLARITY,
                original="function that",
                suggested="function to",
                confidence=0.9,
                explanation="More concise phrasing",
                token_delta=-1,
                position=(start, start + 13),
                developer_tip="Use: 'function to calculate' not 'function that calculates'"
            ))
        
        # Check for missing specifications
        code_keywords = ["function", "class", "method", "api", "implement", "create", "build"]
        has_code_request = any(keyword in prompt_lower for keyword in code_keywords)
        
        if has_code_request:
            # Check for missing type specifications
            if not any(word in prompt_lower for word in ["return", "returns", "->", ":", "type"]):
                suggestions.append(Suggestion(
                    type=SuggestionType.SPECIFICITY,
                    original=prompt[:30] + "...",
                    suggested="[Add return type]: -> ResponseType",
                    confidence=0.85,
                    explanation="Always specify return types for functions",
                    token_delta=3,
                    position=(0, 30),
                    developer_tip="Include types: funcName(param: Type): ReturnType"
                ))
            
            # Check for missing error handling
            if not any(word in prompt_lower for word in ["error", "exception", "handle", "catch", "try"]):
                suggestions.append(Suggestion(
                    type=SuggestionType.TECHNICAL_ACCURACY,
                    original="implement",
                    suggested="implement with error handling for",
                    confidence=0.8,
                    explanation="Specify error handling requirements",
                    token_delta=4,
                    position=(0, 20),
                    developer_tip="Always specify: 'handle X errors, throw Y exceptions'"
                ))
        
        # Check for verbose prompts
        word_count = len(prompt.split())
        if word_count > 30:
            # Create optimized version
            words = prompt.split()
            
            # Remove common filler words
            filler_words = ["just", "basically", "simply", "really", "very", "quite", "rather", "somewhat"]
            optimized_words = [w for w in words if w.lower() not in filler_words]
            
            # Create action-oriented rewrite
            if len(optimized_words) < len(words):
                optimized = " ".join(optimized_words)
                suggestions.append(Suggestion(
                    type=SuggestionType.STRUCTURE,
                    original=prompt[:50] + "...",
                    suggested=f"REWRITE: {optimized[:100]}...",
                    confidence=0.9,
                    explanation=f"Remove filler words - reduced from {len(words)} to {len(optimized_words)} words",
                    token_delta=len(optimized_words) - len(words),
                    position=(0, len(prompt)),
                    developer_tip="Every word should add value - remove fillers"
                ))
        
        # Professional format suggestion
        if not any(char in prompt for char in [":", "-", "•", "1.", "2."]):
            suggestions.append(Suggestion(
                type=SuggestionType.STRUCTURE,
                original=prompt[:40] + "...",
                suggested="Format: [ACTION]: [SPEC] • Input: [TYPE] • Output: [TYPE] • Constraints: [LIST]",
                confidence=0.85,
                explanation="Use structured format for clarity",
                token_delta=5,
                position=(0, 40),
                developer_tip="Structure: ACTION: what • INPUT: type • OUTPUT: format • CONSTRAINTS: list"
            ))
        
        return self._create_basic_response(suggestions[:5], prompt)
    
    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()

# Global analyzer instance
analyzer = None

# Startup/Shutdown events
async def startup_event():
    global analyzer
    analyzer = Grok3Analyzer()
    print("🚀 Martin Backend with Grok3 Integration Started")
    print(f"📍 API Mode: {'Production' if analyzer.client else 'Demo'}")

async def shutdown_event():
    global analyzer
    if analyzer:
        await analyzer.close()

app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)

# Authentication (simplified for development)
async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Simple token verification"""
    return credentials.credentials if credentials else "demo-token"

# API Endpoints
@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
async def analyze_prompt(
    request: AnalyzeRequest,
    token: str = Depends(verify_token)
):
    """Analyze a prompt and return suggestions"""
    start_time = time.time()
    
    try:
        # Analyze with Grok3
        result = await analyzer.analyze_prompt(
            request.prompt,
            request.target_model,
            request.context,
            request.options
        )
        
        # Build response
        response = AnalyzeResponse(
            suggestions=result["suggestions"],
            metrics=result["metrics"],
            processing_time_ms=int((time.time() - start_time) * 1000),
            tips=result["tips"]
        )
        
        return response
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "grok3_connected": analyzer.client is not None,
        "mode": "production" if analyzer.client else "demo"
    }

@app.get("/api/v1/models")
async def list_models():
    """List supported models"""
    return {
        "models": [
            {
                "id": model.value,
                "name": model.value.replace("-", " ").title(),
                "description": f"Optimized for {model.value}",
                "supported": True
            }
            for model in TargetModel
        ]
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Martin API",
        "version": "2.0.0",
        "description": "AI-powered prompt optimization with Grok3",
        "status": "running",
        "mode": "production" if analyzer and analyzer.client else "demo",
        "endpoints": {
            "health": "/api/v1/health",
            "analyze": "/api/v1/analyze",
            "models": "/api/v1/models",
            "docs": "/docs"
        }
    }

# Run the server
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    print(f"""
╔══════════════════════════════════════════════╗
║            Martin Backend v2.0               ║
║         Powered by Grok3 API                 ║
╠══════════════════════════════════════════════╣
║  API URL: http://localhost:{port:<6}            ║
║  Docs:    http://localhost:{port}/docs        ║
║  Health:  http://localhost:{port}/api/v1/health   ║
╚══════════════════════════════════════════════╝

Mode: {'🚀 Production (Grok3 Connected)' if os.getenv('GROK3_API_KEY') and os.getenv('GROK3_API_KEY') != 'your_grok3_api_key_here' else '⚠️  Demo Mode (No API Key)'}
""")
    
    uvicorn.run(app, host=host, port=port, reload=False)