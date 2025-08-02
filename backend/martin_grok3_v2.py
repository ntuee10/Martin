"""
Martin Backend v2.0 with Enhanced Grok3 Integration
Optimized specifically for developer prompt engineering
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
    title="Martin API v2.0",
    version="2.0.0",
    description="Developer-focused AI prompt optimization powered by Grok3"
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
    CLAUDE_CODE = "claude-code"
    CURSOR = "cursor"
    GEMINI = "gemini"
    GITHUB_COPILOT = "github-copilot"

class SuggestionType(str, Enum):
    CLARITY = "clarity"
    SPECIFICITY = "specificity"
    STRUCTURE = "structure"
    TOKEN_OPTIMIZATION = "token_optimization"
    TECHNICAL_ACCURACY = "technical_accuracy"

class Domain(str, Enum):
    CODE_GENERATION = "code_generation"
    DEBUGGING = "debugging"
    ARCHITECTURE = "architecture"
    API_DESIGN = "api_design"
    REFACTORING = "refactoring"

# Pydantic Models
class PromptContext(BaseModel):
    domain: Domain = Domain.CODE_GENERATION
    language: Optional[str] = None
    framework: Optional[str] = None
    session_id: Optional[str] = None

class AnalysisOptions(BaseModel):
    include_examples: bool = True
    max_suggestions: int = 5
    aggressive_optimization: bool = True

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
    example: Optional[str] = None

class PromptMetrics(BaseModel):
    clarity_score: float = Field(..., ge=0, le=100)
    specificity_score: float = Field(..., ge=0, le=100)
    token_efficiency: float = Field(..., ge=0, le=100)
    technical_accuracy: float = Field(..., ge=0, le=100)
    overall_quality: float = Field(..., ge=0, le=100)
    token_count: int
    token_reduction: int
    estimated_cost_savings: float

class AnalyzeResponse(BaseModel):
    optimized_prompt: str
    suggestions: List[Suggestion]
    metrics: PromptMetrics
    processing_time_ms: int
    developer_tips: List[str]

# Grok3 API Client
class Grok3Analyzer:
    """Enhanced Grok3 API integration for developer-focused prompt analysis"""
    
    # Developer-focused system prompt
    SYSTEM_PROMPT = """You are Martin, an AI prompt optimization specialist designed exclusively for software developers. Your mission is to transform developer prompts into precise, technically explicit instructions that maximize AI coding assistant effectiveness.

## CORE DIRECTIVE
Output ONLY the optimized prompt - never attempt to solve the underlying coding problem. Your role is prompt enhancement, not code generation.

## DEVELOPER-FOCUSED OPTIMIZATION FRAMEWORK

### 1. TECHNICAL CLARITY ANALYSIS
- Extract exact technical requirements and constraints
- Identify missing specifications (types, formats, error handling, edge cases)
- Map architectural patterns and design requirements
- Detect ambiguous technical terms that need precision

### 2. SPECIFICATION ENHANCEMENT
- Add explicit input/output types and schemas
- Define success criteria and test cases
- Specify error handling requirements
- Include performance constraints when relevant
- Add code style and convention requirements

### 3. STRUCTURAL OPTIMIZATION
For coding tasks, structure prompts as:
- Clear function/component specifications
- Explicit parameter types and return values
- Edge case handling requirements
- Example usage when beneficial
- Technology stack constraints

### 4. DEVELOPER COMMUNICATION PATTERNS
Transform casual requests into technical specifications using:
- Precise technical vocabulary
- Structured requirement lists
- Clear acceptance criteria
- Explicit constraints and boundaries

## OPTIMIZATION TECHNIQUES FOR DEVELOPERS

### Code Generation Requests
- Define exact function signatures
- Specify all data structures
- Include error handling requirements
- Add performance considerations
- Clarify integration points

### Architecture/Design Requests
- Specify design patterns expected
- Define scalability requirements
- Include technology constraints
- Clarify integration boundaries

### Debugging/Refactoring Requests
- Pinpoint exact issues or code locations
- Define expected behavior vs actual
- Specify refactoring goals and constraints
- Include relevant context and dependencies

### API/Integration Requests
- Define exact endpoints and methods
- Specify request/response schemas
- Include authentication requirements
- Add rate limiting and error handling needs

## OUTPUT FORMAT
Return ONLY the optimized prompt text. No explanations, no meta-commentary, no additional sections. The optimized prompt should be:
- Technically precise
- Immediately actionable
- Free of ambiguity
- Structured for systematic processing

## EXAMPLES OF TRANSFORMATION

Input: "create a function to process user data"
Output: "Create a TypeScript function processUserData that:
- Accepts: User[] array with schema {id: string, email: string, name: string, createdAt: Date}
- Validates: email format using regex, removes duplicate IDs
- Transforms: normalizes email to lowercase, sorts by createdAt descending
- Returns: {processed: User[], errors: {id: string, reason: string}[]}
- Handles: null/undefined inputs, empty arrays, malformed data
- Performance: O(n log n) complexity, handle up to 10k records"

Input: "help me fix this bug"
Output: "Debug TypeError at line 45 in UserService.ts:
- Error: 'Cannot read property id of undefined'
- Context: Occurs when calling getUserById() with valid UUID
- Current behavior: Throws error instead of returning user object
- Expected: Return User object or throw NotFoundException
- Provide: Root cause analysis and fix that maintains type safety"

Remember: You optimize prompts, not solve problems. Output only the enhanced prompt text."""
    
    def __init__(self):
        self.api_key = os.getenv("GROK3_API_KEY", "")
        self.api_url = os.getenv("GROK3_API_URL", "https://api.x.ai/v1")
        self.model = "grok-beta"
        
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
            print("✅ Grok3 client initialized for production")
    
    async def analyze_prompt(
        self,
        prompt: str,
        target_model: TargetModel,
        context: PromptContext,
        options: AnalysisOptions
    ) -> Dict:
        """Analyze prompt using Grok3 API with developer focus"""
        
        if not self.client:
            return self._demo_analysis(prompt, target_model)
        
        try:
            # Build the analysis request
            analysis_prompt = self._build_analysis_prompt(prompt, target_model, context)
            
            # Call Grok3 API
            response = await self.client.post(
                f"{self.api_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1500,
                    "stream": False
                }
            )
            
            if response.status_code != 200:
                print(f"Grok3 API error: {response.status_code} - {response.text}")
                return self._demo_analysis(prompt, target_model)
            
            # Parse response
            result = response.json()
            optimized_prompt = result["choices"][0]["message"]["content"].strip()
            
            # Generate detailed analysis
            return self._generate_analysis(prompt, optimized_prompt, target_model)
                
        except Exception as e:
            print(f"Grok3 API error: {str(e)}")
            return self._demo_analysis(prompt, target_model)
    
    def _build_analysis_prompt(
        self,
        prompt: str,
        target_model: TargetModel,
        context: PromptContext
    ) -> str:
        """Build the analysis request for Grok3"""
        
        context_info = ""
        if context.language:
            context_info += f"\nProgramming Language: {context.language}"
        if context.framework:
            context_info += f"\nFramework: {context.framework}"
        
        return f"""Optimize this developer prompt for {target_model.value}:{context_info}

ORIGINAL PROMPT:
{prompt}

Transform this into a precise, technical prompt that will get exactly the right code from the AI. Follow the optimization framework and output ONLY the optimized prompt."""
    
    def _generate_analysis(
        self,
        original: str,
        optimized: str,
        target_model: TargetModel
    ) -> Dict:
        """Generate detailed analysis comparing original and optimized prompts"""
        
        suggestions = []
        
        # Main optimization suggestion
        if optimized != original:
            suggestions.append(Suggestion(
                type=SuggestionType.STRUCTURE,
                original=original[:100] + "..." if len(original) > 100 else original,
                suggested=optimized,
                confidence=0.95,
                explanation="Complete developer-focused optimization for maximum clarity and efficiency",
                token_delta=len(optimized.split()) - len(original.split()),
                position=(0, len(original)),
                developer_tip="Use this version directly - it includes all technical specifications the AI needs",
                example=f"Original: {len(original.split())} words → Optimized: {len(optimized.split())} words"
            ))
        
        # Analyze specific improvements
        original_lower = original.lower()
        
        # Check for missing specifications
        code_indicators = ["function", "method", "class", "api", "component", "implement", "create", "fix", "debug"]
        has_code_request = any(word in original_lower for word in code_indicators)
        
        if has_code_request:
            # Check for missing types
            if not any(word in original_lower for word in ["type", "interface", "schema", ":", "->"]):
                suggestions.append(Suggestion(
                    type=SuggestionType.SPECIFICITY,
                    original="missing type specifications",
                    suggested="add explicit types",
                    confidence=0.9,
                    explanation="Always specify input/output types for functions",
                    token_delta=5,
                    position=(0, 0),
                    developer_tip="Format: functionName(param: Type): ReturnType",
                    example="processData(items: Item[]): ProcessedResult"
                ))
            
            # Check for error handling
            if not any(word in original_lower for word in ["error", "exception", "handle", "validate"]):
                suggestions.append(Suggestion(
                    type=SuggestionType.TECHNICAL_ACCURACY,
                    original="no error handling specified",
                    suggested="add error handling requirements",
                    confidence=0.85,
                    explanation="Specify how errors should be handled",
                    token_delta=4,
                    position=(0, 0),
                    developer_tip="Include: 'Handle X errors, throw Y exceptions'",
                    example="Handle: network errors → retry 3x, validation errors → return {error, details}"
                ))
        
        # Remove verbose language
        verbose_patterns = [
            ("can you", ""),
            ("could you please", ""),
            ("i would like", ""),
            ("help me", ""),
            ("i need", ""),
            ("please", "")
        ]
        
        for pattern, replacement in verbose_patterns:
            if pattern in original_lower:
                idx = original_lower.find(pattern)
                suggestions.append(Suggestion(
                    type=SuggestionType.TOKEN_OPTIMIZATION,
                    original=original[idx:idx+len(pattern)],
                    suggested=replacement,
                    confidence=0.95,
                    explanation=f"Remove '{pattern}' - be direct with AI",
                    token_delta=-len(pattern.split()),
                    position=(idx, idx+len(pattern)),
                    developer_tip="Start with action verbs: Create, Implement, Fix, Refactor"
                ))
                break
        
        # Calculate metrics
        original_words = len(original.split())
        optimized_words = len(optimized.split())
        reduction_percent = ((original_words - optimized_words) / original_words * 100) if original_words > 0 else 0
        
        metrics = PromptMetrics(
            clarity_score=min(100, 70 + len(suggestions) * 10),
            specificity_score=min(100, 60 + (20 if has_code_request else 0) + len(suggestions) * 8),
            token_efficiency=min(100, 100 - (optimized_words / 2)),
            technical_accuracy=85 if has_code_request else 75,
            overall_quality=min(100, 75 + len(suggestions) * 5),
            token_count=int(optimized_words * 1.3),
            token_reduction=original_words - optimized_words,
            estimated_cost_savings=round((original_words - optimized_words) * 0.00015, 4)
        )
        
        # Developer tips
        tips = [
            "Start every prompt with an action verb (Create, Implement, Debug, etc.)",
            "Always specify exact types, schemas, and return values",
            "Include error handling and edge case requirements",
            f"This optimization saved {reduction_percent:.0f}% tokens while adding precision"
        ]
        
        return {
            "optimized_prompt": optimized,
            "suggestions": suggestions[:5],  # Limit to top 5
            "metrics": metrics,
            "developer_tips": tips
        }
    
    def _demo_analysis(self, prompt: str, target_model: TargetModel) -> Dict:
        """Enhanced demo analysis for when API is not available"""
        
        # Simulate optimization
        words = prompt.split()
        
        # Remove fluff
        fluff_words = ["please", "could", "you", "can", "would", "help", "me", "i", "need", "want", "just", "really", "basically"]
        optimized_words = [w for w in words if w.lower() not in fluff_words]
        
        # Add structure if it's a code request
        code_keywords = ["function", "method", "class", "api", "create", "implement", "fix", "debug"]
        is_code_request = any(keyword in prompt.lower() for keyword in code_keywords)
        
        if is_code_request:
            # Create a structured version
            optimized_prompt = f"Implement {' '.join(optimized_words[:5])}:\n"
            optimized_prompt += "- Input: [SPECIFY TYPE]\n"
            optimized_prompt += "- Output: [SPECIFY TYPE]\n"
            optimized_prompt += "- Requirements: [ADD CONSTRAINTS]\n"
            optimized_prompt += "- Error handling: [SPECIFY APPROACH]"
        else:
            optimized_prompt = ' '.join(optimized_words)
        
        return self._generate_analysis(prompt, optimized_prompt, target_model)
    
    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()

# Global analyzer instance
analyzer = None

# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    global analyzer
    analyzer = Grok3Analyzer()
    print("🚀 Martin Backend v2.0 Started - Developer Focus Edition")
    print(f"📍 API Mode: {'Production with Grok3' if analyzer.client else 'Demo Mode'}")

@app.on_event("shutdown")
async def shutdown_event():
    global analyzer
    if analyzer:
        await analyzer.close()

# Authentication
async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Simple token verification"""
    return credentials.credentials if credentials else "demo-token"

# API Endpoints
@app.post("/api/v2/analyze", response_model=AnalyzeResponse)
async def analyze_prompt(
    request: AnalyzeRequest,
    token: str = Depends(verify_token)
):
    """Analyze a developer prompt and return optimization suggestions"""
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
            optimized_prompt=result["optimized_prompt"],
            suggestions=result["suggestions"],
            metrics=result["metrics"],
            processing_time_ms=int((time.time() - start_time) * 1000),
            developer_tips=result["developer_tips"]
        )
        
        return response
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.get("/api/v2/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "grok3_connected": analyzer.client is not None,
        "mode": "production" if analyzer.client else "demo",
        "focus": "developer-optimized"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Martin API v2.0",
        "version": "2.0.0",
        "description": "Developer-focused AI prompt optimization",
        "status": "running",
        "endpoints": {
            "health": "/api/v2/health",
            "analyze": "/api/v2/analyze",
            "docs": "/docs"
        }
    }

# Run the server
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║         Martin Backend v2.0 - Developer Edition          ║
║              Powered by Grok3 + Claude Opus              ║
╠══════════════════════════════════════════════════════════╣
║  API URL: http://localhost:{port:<6}                         ║
║  Docs:    http://localhost:{port}/docs                      ║
║  Health:  http://localhost:{port}/api/v2/health             ║
╚══════════════════════════════════════════════════════════╝

🎯 Optimized for: ChatGPT, Claude, Cursor, GitHub Copilot
🚀 Mode: {'Production (Grok3 Connected)' if os.getenv('GROK3_API_KEY') else 'Demo Mode'}
""")
    
    uvicorn.run(app, host=host, port=port, reload=True)
