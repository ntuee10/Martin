"""
Martin Backend Tests
Test suite for the Martin API v2.0
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from martin_grok3_v2 import app, analyzer

# Test client
client = TestClient(app)

class TestAPI:
    """Test API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Martin API v2.0"
        assert "endpoints" in data
    
    def test_health_endpoint(self):
        """Test health check"""
        response = client.get("/api/v2/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "mode" in data
    
    def test_analyze_endpoint_basic(self):
        """Test basic analyze request"""
        request_data = {
            "prompt": "create a function to process data",
            "target_model": "gpt-4",
            "context": {
                "domain": "code_generation"
            },
            "options": {
                "aggressive_optimization": True
            }
        }
        
        response = client.post(
            "/api/v2/analyze",
            json=request_data,
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "optimized_prompt" in data
        assert "suggestions" in data
        assert "metrics" in data
        assert "developer_tips" in data
        assert "processing_time_ms" in data
        
        # Check optimized prompt is different and better
        assert data["optimized_prompt"] != request_data["prompt"]
        assert len(data["optimized_prompt"]) > 10
        
        # Check suggestions
        assert isinstance(data["suggestions"], list)
        if len(data["suggestions"]) > 0:
            suggestion = data["suggestions"][0]
            assert "type" in suggestion
            assert "original" in suggestion
            assert "suggested" in suggestion
            assert "explanation" in suggestion
            assert "confidence" in suggestion
        
        # Check metrics
        metrics = data["metrics"]
        assert 0 <= metrics["clarity_score"] <= 100
        assert 0 <= metrics["specificity_score"] <= 100
        assert "token_reduction" in metrics
    
    def test_analyze_different_models(self):
        """Test analysis for different target models"""
        models = ["gpt-4", "claude-3", "cursor", "gemini"]
        
        for model in models:
            request_data = {
                "prompt": "help me create a React component",
                "target_model": model
            }
            
            response = client.post(
                "/api/v2/analyze",
                json=request_data,
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["optimized_prompt"]) > 0
    
    def test_analyze_long_prompt(self):
        """Test analysis of longer prompts"""
        long_prompt = """
        I need help creating a comprehensive user authentication system 
        for my web application. It should handle user registration, 
        login, password reset, and session management. I want to use 
        JWT tokens and implement proper security measures. The system 
        should also support OAuth integration with Google and GitHub.
        Please make it scalable and follow best practices.
        """
        
        request_data = {
            "prompt": long_prompt,
            "target_model": "gpt-4",
            "context": {
                "domain": "architecture",
                "language": "TypeScript",
                "framework": "Express.js"
            }
        }
        
        response = client.post(
            "/api/v2/analyze",
            json=request_data,
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have significant optimization
        assert len(data["suggestions"]) > 0
        assert data["metrics"]["token_reduction"] > 0
    
    def test_analyze_code_debugging_prompt(self):
        """Test debugging prompt optimization"""
        debug_prompt = "my code doesn't work please help fix the bug"
        
        request_data = {
            "prompt": debug_prompt,
            "target_model": "claude-3",
            "context": {
                "domain": "debugging"
            }
        }
        
        response = client.post(
            "/api/v2/analyze",
            json=request_data,
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should add specificity
        assert "specific" in data["optimized_prompt"].lower() or \
               "error" in data["optimized_prompt"].lower() or \
               "line" in data["optimized_prompt"].lower()
    
    def test_invalid_request(self):
        """Test invalid request handling"""
        # Empty prompt
        response = client.post(
            "/api/v2/analyze",
            json={"prompt": ""},
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 422
        
        # Missing prompt
        response = client.post(
            "/api/v2/analyze",
            json={},
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 422
    
    def test_metrics_calculation(self):
        """Test metrics are calculated correctly"""
        test_cases = [
            {
                "prompt": "please help me",
                "expected": {
                    "low_clarity": True,
                    "needs_specificity": True
                }
            },
            {
                "prompt": "Create TypeScript function parseJSON(input: string): Result<any, Error> with proper error handling",
                "expected": {
                    "high_clarity": True,
                    "good_specificity": True
                }
            }
        ]
        
        for test_case in test_cases:
            response = client.post(
                "/api/v2/analyze",
                json={"prompt": test_case["prompt"]},
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            metrics = data["metrics"]
            
            if test_case["expected"].get("low_clarity"):
                assert metrics["clarity_score"] < 70
            if test_case["expected"].get("high_clarity"):
                assert metrics["clarity_score"] > 70
            if test_case["expected"].get("needs_specificity"):
                assert metrics["specificity_score"] < 70
            if test_case["expected"].get("good_specificity"):
                assert metrics["specificity_score"] > 70


class TestOptimizations:
    """Test specific optimization patterns"""
    
    def test_removes_politeness(self):
        """Test removal of polite language"""
        polite_prompts = [
            "Could you please help me create a function?",
            "I would like you to implement a sorting algorithm",
            "Can you please write code for user authentication?"
        ]
        
        for prompt in polite_prompts:
            response = client.post(
                "/api/v2/analyze",
                json={"prompt": prompt},
                headers={"Authorization": "Bearer test-token"}
            )
            
            data = response.json()
            optimized = data["optimized_prompt"].lower()
            
            # Should remove polite words
            assert "please" not in optimized
            assert "could you" not in optimized
            assert "would like" not in optimized
    
    def test_adds_technical_specs(self):
        """Test addition of technical specifications"""
        vague_prompt = "create a function to validate email"
        
        response = client.post(
            "/api/v2/analyze",
            json={
                "prompt": vague_prompt,
                "context": {"domain": "code_generation"}
            },
            headers={"Authorization": "Bearer test-token"}
        )
        
        data = response.json()
        optimized = data["optimized_prompt"].lower()
        
        # Should add specifications
        assert any(keyword in optimized for keyword in [
            "return", "input", "output", "type", "parameter",
            "validates", "regex", "format", "@"
        ])
    
    def test_improves_structure(self):
        """Test structural improvements"""
        unstructured = "I need a React component that shows user profile with avatar and handles editing and saves to API"
        
        response = client.post(
            "/api/v2/analyze",
            json={"prompt": unstructured},
            headers={"Authorization": "Bearer test-token"}
        )
        
        data = response.json()
        optimized = data["optimized_prompt"]
        
        # Should have better structure (bullets, colons, or line breaks)
        assert any(char in optimized for char in [":", "-", "•", "\n"])


@pytest.fixture
async def async_client():
    """Async client fixture for async tests"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_async_analyze(async_client):
    """Test async analyze endpoint"""
    response = await async_client.post(
        "/api/v2/analyze",
        json={
            "prompt": "help me create an API endpoint",
            "target_model": "gpt-4"
        },
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "optimized_prompt" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
