#!/usr/bin/env python3
"""
Hermes Model Router - Optimized for BEST VALUE (good quality, low cost) ✅

This script analyzes incoming tasks and routes them to different OpenRouter models based on:
- Task complexity
- Domain (coding, creative, research, general, etc.)
- Required capabilities (reasoning, speed, cost-efficiency)

FOCUSED ON: Excellent quality models at 50-90% LESS than premium!

Usage:
    hermes-model-router "your task here"          # Interactive chat with model auto-selection
    echo "your task" | python3 model_router.py   # Pipe text to auto-select model

🎯 KEY MODEL UPDATES:
• DeepSeek Chat: $0.27/$1.10 - AMAZING value! Near-Claude quality
• Qwen 2.5 72B: $0.55/$1.10 - Excellent reasoning, 50% cheaper than Claude
• Qwen Coder 32B: $0.18/$0.18 - Best coding model for the price!
• Mistral Nemo: $0.15/$0.15 - Surprisingly capable, super affordable
• Google Gemma 2: $0.04/$0.10 - Budget-friendly with good results
• Microsoft Phi 3.5: $0.02 - Extremely cheap for simple tasks
"""

import json
import sys
import os
from typing import Optional, Dict, List, Tuple

# Model registry - OPTIMIZED FOR BEST VALUE (good quality, low cost)
MODEL_REGISTRY = {
    # ===== LARGE / HEAVY MODELS (Complex reasoning, coding, research) =====
    "large": {
        "models": [
            "deepseek/deepseek-chat",           # ~$0.27/$1.10 - AMAZING value! Great reasoning
            "qwen/qwen-2.5-72b-instruct",       # ~$0.55/$1.10 - Excellent multilingual
            "mistralai/pixtral-12b-2409",       # ~$0.15/$0.60 - Fast & capable
            "qwen/qwen-2.5-coder-32b-instruct", # ~$0.18/$0.18 - Best coding model!
            "nexusflow/starling-lm-7b-beta",    # ~$0.10/$0.00 - Free tier available
        ],
        "priority": 1,
        "use_cases": [
            "build a", "create a complete", "complete system", "full", "complex", "advanced",
            "coding", "programming", "software", "engineering", "architecture", "research",
            "analysis", "math", "reasoning", "multi-step", "complicated",
            "debug", "debugging", "optimize", "refactor",
            "documentation", "api", "develop", "microservice", "scalable",
            "deploy", "production", "enterprise", "secure",
            "authentication", "authorization", "jwt", "encryption",
            "migration", "refactoring", "rewrite", "restructure", "rearchitect",
            "performance", "bottleneck", "optimization"
        ],
        "cost_tier": "medium-low",
        "description": "Best value for complex tasks - DeepSeek offers amazing quality at 80% less cost than Claude"
    },
    
    # ===== MEDIUM MODELS (Balanced performance and cost) =====
    "medium": {
        "models": [
            "qwen/qwen2.5-72b-instruct",        # ~$0.55/$1.10 - Fantastic quality!
            "mistralai/mistral-nemo-2407",      # ~$0.15/$0.15 - Excellent value!
            "google/gemma-2-9b-it",             # ~$0.04/$0.10 - Super cheap!
            "qwen/qwen2.5-coder-32b-instruct",  # ~$0.18/$0.18 - Also good for general!
            "meta-llama/llama-3.1-8b-instruct", # ~$0.05/$0.05 - Very affordable
        ],
        "priority": 2,
        "use_cases": [
            "general", "summar", "write an email", "draft",
            "translate", "convert to", "convert ", "format", "rewrite", "summarize",
            "summary", "overview", "brief", "guide", "tutorial",
            "help with", "assist me", "create a", "design a", "plan a",
            "compare", "list", "describe", "explain", "what does", "how does",
            "difference", "similar", "opposite", "example", "examples",
            "learn about", "understand", "teach me", "simple explanation"
        ],
        "cost_tier": "low",
        "description": "Perfect balance of quality and cost - 60-80% cheaper than premium"
    },
    
    # ===== SMALL / FAST MODELS (Quick tasks, simple queries) =====
    "small": {
        "models": [
            "qwen/qwen2.5-coder-32b-instruct",  # ~$0.18 - Actually better than flash!
            "microsoft/phi-3.5-mini-instruct",  # ~$0.02 - Super cheap!
            "mistralai/mistral-nemo-2407",      # ~$0.15 - Still great value
            "google/gemma-2-2b-it",             # ~$0.02 - Extremely budget!
            "qwen/qwen2.5-3b-instruct",         # ~$0.02 - Tiny but mighty!
            "meta-llama/llama-3.2-3b-instruct", # ~$0.02 - Very fast!
        ],
        "priority": 3,
        "use_cases": [
            "hello", "hi", "hey", "thanks", "thank you",
            "quick", "simple", "fast", "short", "yes", "no",
            "format", "names", "count",
            "spelling", "grammar", "capitalize", "lowercase", "uppercase",
            "translate", "definition", "synonym", "antonym",
            "check", "is it", "is this", "verify", "confirm",
            "what is", "what's", "capital of", "population of",
            "age of", "when was", "who is", "simple", "basic",
            "short", "brief", "one word", "two words", "3 words",
            "list 5", "list 10", "top 3", "5 examples"
        ],
        "cost_tier": "very-low",
        "description": "Super fast and cheap - some models as low as 2 cents per million tokens!"
    },
    
    # ===== CODING-SPECIALIZED =====
    "coding": {
        "models": [
            "qwen/qwen2.5-coder-32b-instruct",  # ~$0.18/$0.18 - AMAZING coding model!
            "deepseek/deepseek-coder-33b-instruct", # ~$0.23/$0.23 - Excellent!
            "mistralai/mistral-nemo-2407",      # ~$0.15/$0.15 - Surprisingly good!
            "meta-llama/llama-3.3-70b-instruct", # ~$0.57/$0.92 - Top tier
            "qwen/qwen-coder-2-7b-instruct",    # ~$0.02/$0.02 - Budget coding!
        ],
        "priority": 1,
        "use_cases": [
            "code", "function", "class", "def ", "def(\n", "import",
            "package", "module", "library", "framework", "api",
            "database", "sql", "query", "docker", "kubernetes", "k8s",
            "ci/cd", "pipeline", "deployment", "build", "test",
            "unit test", "integration test", "pytest", "jest",
            "python", "javascript", "typescript", "react", "vue",
            "node", "express", "django", "flask", "fastapi",
            "bash", "shell", "script", "automation", "scripting",
            "regex", "regexp", "parsing", "parsing code", "git",
            "web", "backend", "frontend", "full stack", "devops"
        ],
        "cost_tier": "very-low",
        "description": "Best coding models at fraction of Claude cost - 90% cheaper!"
    },
    
    # ===== CREATIVE/WRITING =====
    "creative": {
        "models": [
            "qwen/qwen2.5-72b-instruct",        # ~$0.55/$1.10 - Great for writing!
            "mistralai/mistral-nemo-2407",      # ~$0.15/$0.15 - Excellent creative!
            "google/gemma-2-9b-it",             # ~$0.04/$0.10 - Budget creative!
            "meta-llama/llama-3.1-8b-instruct", # ~$0.05/$0.05 - Very affordable
            "qwen/qwen2.5-coder-32b-instruct",  # ~$0.18/$0.18 - Also writes well!
        ],
        "priority": 2,
        "use_cases": [
            "write a", "write an", "article", "blog", "story",
            "fiction", "creative", "poem", "poetry", "song",
            "lyric", "script", "dialogue", "scene", "character",
            "marketing", "ad", "advertisement", "copy", "sales",
            "email", "letter", "proposal", "pitch", "presentation",
            "content", "social media", "twitter", "tweet", "linkedin",
            "resume", "cv", "cover letter", "essay", "composition",
            "description", "caption", "post", "thread"
        ],
        "cost_tier": "low",
        "description": "Quality writing at 50-70% less than premium models"
    },
    
    # ===== ANALYSIS/DATA =====
    "analysis": {
        "models": [
            "deepseek/deepseek-chat",           # ~$0.27/$1.10 - Best reasoning value!
            "qwen/qwen2.5-72b-instruct",        # ~$0.55/$1.10 - Great math!
            "mistralai/mistral-nemo-2407",      # ~$0.15/$0.15 - Good analysis!
            "google/gemma-2-9b-it",             # ~$0.04/$0.10 - Budget math!
            "qwen/qwen2.5-coder-32b-instruct",  # ~$0.18/$0.18 - Surprisingly good!
        ],
        "priority": 2,
        "use_cases": [
            "analyze", "data", "statistics", "statistic",
            "calculate", "compute", "math", "formula",
            "chart", "graph", "visualize", "table",
            "csv", "json", "excel", "spreadsheet",
            "report", "summary", "insight", "pattern",
            "trend", "forecast", "predict", "comparison",
            "benchmark", "perf", "performance", "evaluate",
            "review", "assessment", "metrics", "kpi"
        ],
        "cost_tier": "low",
        "description": "Excellent analytical capability at fraction of premium cost"
    }
}

# Task type detection patterns
TASK_ANALYSIS_PROMPT = """Analyze this task and return a JSON object with the recommended model category.

Task: {task}

Return ONLY JSON in this format:
{{
    "category": "large" | "medium" | "small" | "coding" | "creative" | "analysis",
    "confidence": 0.0-1.0,
    "reason": "short explanation"
}}"""


def analyze_task(task: str) -> Dict:
    """
    Simple keyword-based task analysis for model routing.
    For more sophisticated routing, you can use an LLM here.
    """
    task_lower = task.lower().strip()
    scores = {cat: 0 for cat in MODEL_REGISTRY}
    
    # Count keyword matches
    for category, config in MODEL_REGISTRY.items():
        for keyword in config["use_cases"]:
            if keyword.lower() in task_lower:
                scores[category] += 1
    
    # Find best category
    best_category = max(scores, key=scores.get)
    
    # Calculate confidence
    total_matches = sum(scores.values())
    confidence = min(1.0, total_matches / 5.0)  # Normalize
    
    # Always return at least small models if nothing matched
    if total_matches == 0:
        best_category = "medium"  # Default to balanced
        confidence = 0.3
    
    return {
        "category": best_category,
        "confidence": confidence,
        "reason": f"Matched {scores[best_category]} keywords to {best_category} model category",
        "all_scores": scores
    }


def get_best_model(category: str) -> str:
    """Get the best model from a category based on usage count."""
    models = MODEL_REGISTRY[category]["models"]
    # Default to first model (best value), could implement usage tracking for smart selection
    return models[0]


def route_task(task: str) -> Tuple[str, Dict]:
    """
    Route a task to a model and return the model name + analysis.
    """
    analysis = analyze_task(task)
    category = analysis["category"]
    model = get_best_model(category)
    
    analysis["selected_model"] = model
    return model, analysis


def build_chat_command(task: str) -> str:
    """Build the hermes command with the selected model."""
    model, analysis = route_task(task)
    
    # Add comment to show selection
    model_cmd = f"hermes chat -q -m {model} \"\" {task} \"\""
    
    print(f"=== Model Selection Analysis 🚀 ===")
    print(f"Task: {task}")
    print(f"Recommended Model: {model}")
    print(f"Cost Tier: {analysis['category']} → {MODEL_REGISTRY[analysis['category']]['cost_tier']}")
    print(f"Reason: {analysis['reason']}")
    print(f"Confidence: {analysis['confidence']:.0%}")
    print(f"Command: {model_cmd}")
    print(f"========================================")
    # Show example pricing for the selected model
    print(f"💡 Tip: This model is 50-90% cheaper than premium alternatives!")
    print(f"========================================")
    
    return model_cmd


def interactive_route_task():
    """Interactive mode - prompt user for task and auto-route."""
    print("\n=== 🚀 Hermes Model Router (Budget-Optimized) ===")
    print("Enter your task (type 'quit' to exit):\n")
    
    while True:
        task = input("Your task: ").strip()
        
        if task.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye! Happy coding! 💻")
            break
        
        if not task:
            print("Please enter a task.\n")
            continue
        
        try:
            model_cmd = build_chat_command(task)
            # Execute the command
            os.system(model_cmd)
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n")


def pipe_mode():
    """Read from stdin and route."""
    for line in sys.stdin:
        task = line.strip()
        if task:
            model_cmd = build_chat_command(task)
            # If piping, just output the command
            # Set HERMES_ROUTER_RUN=1 to auto-execute
            if os.getenv("HERMES_ROUTER_RUN") == "1":
                os.system(model_cmd)
            else:
                print(f"# Execute: {model_cmd}")


def main():
    if len(sys.argv) > 1:
        # Command line mode
        task = " ".join(sys.argv[1:])
        model_cmd = build_chat_command(task)
        if os.getenv("HERMES_ROUTER_RUN") == "1":
            os.system(model_cmd)
    elif sys.stdin.isatty():
        # Interactive mode
        interactive_route_task()
    else:
        # Pipe mode
        pipe_mode()


if __name__ == "__main__":
    main()
