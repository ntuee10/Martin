#!/usr/bin/env python3
"""
Martin Demo Script
Quick demonstration of Martin's prompt optimization capabilities
"""

import requests
import json
from typing import Dict, Any
import time

# Configuration
API_URL = "http://localhost:8000/api/v2/analyze"
API_TOKEN = "demo-token"

# Demo prompts for different use cases
DEMO_PROMPTS = {
    "vague_function": {
        "prompt": "can you please help me create a function to process user data?",
        "description": "Vague function request"
    },
    "debug_request": {
        "prompt": "my code doesn't work, something is wrong with the user authentication",
        "description": "Unclear debugging request"
    },
    "api_design": {
        "prompt": "I need to build an API for managing blog posts with CRUD operations",
        "description": "API design request"
    },
    "react_component": {
        "prompt": "help me make a React component that shows a list of items with search functionality",
        "description": "React component request"
    },
    "performance": {
        "prompt": "Please optimize this function to run faster, it's too slow right now",
        "description": "Performance optimization request"
    }
}

def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_suggestion(suggestion: Dict[str, Any]):
    """Print a single suggestion"""
    print(f"  Type: {suggestion['type']}")
    print(f"  Original: {suggestion['original']}")
    print(f"  Suggested: {suggestion['suggested']}")
    print(f"  Explanation: {suggestion['explanation']}")
    print(f"  Token Delta: {suggestion['token_delta']}")
    print()

def analyze_prompt(prompt: str, target_model: str = "gpt-4") -> Dict[str, Any]:
    """Send prompt to Martin API for analysis"""
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    data = {
        "prompt": prompt,
        "target_model": target_model,
        "context": {
            "domain": "code_generation"
        },
        "options": {
            "aggressive_optimization": True
        }
    }
    
    try:
        response = requests.post(API_URL, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to Martin API")
        print("   Make sure the backend is running: python martin_grok3_v2.py")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_api_health() -> bool:
    """Check if the API is running"""
    try:
        response = requests.get("http://localhost:8000/api/v2/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Martin API is running")
            print(f"   Version: {data['version']}")
            print(f"   Mode: {data['mode']}")
            print(f"   Grok3: {'Connected' if data['grok3_connected'] else 'Demo Mode'}")
            return True
    except:
        pass
    
    print("❌ Martin API is not running")
    print("   Start it with: cd backend && python martin_grok3_v2.py")
    return False

def run_demo():
    """Run the Martin demo"""
    print_header("Martin Prompt Optimizer Demo")
    
    # Check API health
    if not check_api_health():
        return
    
    print("\nPress Enter to see each optimization, or 'q' to quit\n")
    
    # Demo each prompt
    for key, demo in DEMO_PROMPTS.items():
        print_header(demo["description"])
        print(f"Original prompt:\n  \"{demo['prompt']}\"\n")
        
        user_input = input("Press Enter to optimize (or 'q' to quit): ")
        if user_input.lower() == 'q':
            break
        
        # Analyze the prompt
        print("\n🔄 Analyzing with Martin...")
        start_time = time.time()
        
        result = analyze_prompt(demo["prompt"])
        if not result:
            continue
        
        elapsed_time = time.time() - start_time
        
        # Display results
        print(f"\n✨ Analysis complete in {elapsed_time:.2f}s\n")
        
        print("Optimized prompt:")
        print("-" * 40)
        print(result["optimized_prompt"])
        print("-" * 40)
        
        # Show metrics
        metrics = result["metrics"]
        print(f"\n📊 Metrics:")
        print(f"  Clarity Score: {metrics['clarity_score']:.0f}%")
        print(f"  Specificity Score: {metrics['specificity_score']:.0f}%")
        print(f"  Token Reduction: {metrics['token_reduction']} tokens")
        print(f"  Cost Savings: ${metrics['estimated_cost_savings']:.4f}")
        
        # Show suggestions
        if result["suggestions"]:
            print(f"\n💡 Suggestions ({len(result['suggestions'])}):")
            for i, suggestion in enumerate(result["suggestions"][:3]):
                print(f"\n  {i+1}. ", end="")
                print_suggestion(suggestion)
        
        # Show developer tips
        if result["developer_tips"]:
            print("🎯 Developer Tips:")
            for tip in result["developer_tips"]:
                print(f"  • {tip}")
        
        print()
    
    print_header("Demo Complete!")
    print("To use Martin in your browser:")
    print("1. Load the extension from extension/dist_v2/")
    print("2. Go to ChatGPT, Claude, or any supported platform")
    print("3. Start typing and watch Martin optimize your prompts!\n")

def test_specific_prompt():
    """Test a specific prompt interactively"""
    print_header("Test Your Own Prompt")
    
    if not check_api_health():
        return
    
    while True:
        print("\nEnter a prompt to optimize (or 'quit' to exit):")
        prompt = input("> ")
        
        if prompt.lower() in ['quit', 'exit', 'q']:
            break
        
        if len(prompt.strip()) < 10:
            print("Please enter a longer prompt (at least 10 characters)")
            continue
        
        print("\n🔄 Analyzing...")
        result = analyze_prompt(prompt)
        
        if result:
            print("\n✨ Optimized version:")
            print("-" * 40)
            print(result["optimized_prompt"])
            print("-" * 40)
            
            metrics = result["metrics"]
            print(f"\nImprovement: {metrics['overall_quality']:.0f}% | "
                  f"Tokens saved: {metrics['token_reduction']} | "
                  f"Cost saved: ${metrics['estimated_cost_savings']:.4f}")

def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_specific_prompt()
    else:
        run_demo()

if __name__ == "__main__":
    main()
