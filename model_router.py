#!/usr/bin/env python3
"""
Hermes Model Router - Automatically selects the best OpenRouter model for the task.

This script analyzes incoming tasks and routes them to different models based on:
- Task complexity
- Domain (coding, creative, research, general, etc.)
- Required capabilities (reasoning, speed, cost-efficiency)

Usage:
    hermes route "your task here"          # Interactive chat with model auto-selection
    echo "your task" | python3 model_router.py  # Pipe text to auto-select model
"""

import json
import sys
import os
from typing import Optional, Dict, List, Tuple

# Model registry - customize with your own models and criteria
MODEL_REGISTRY = {
    # ===== LARGE / HEAVY MODELS (Complex reasoning, coding, research) =====
    "large": {
        "models": [
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-sonnet-4",
            "xai/grok-3-beta",
            "deepseek/deepseek-chat",
            "qwen/qwen-2.5-72b-instruct",
        ],
        "priority": 1,
        "use_cases": [
            "build a", "create a complete", "complete system", "full", "complex", "advanced",
            "coding", "programming", "software", "engineering", "architecture", "research",
            "analysis", "math", "reasoning", "multi-step", "complicated",
            "debug", "debugging", "optimize", "optimize", "refactor",
            "documentation", "api", "develop", "microservice", "scalable",
            "deploy", "production", "enterprise", "enterprise-grade", "secure",
            "authentication", "authorization", "oauth", "jwt", "encryption",
            "migration", "refactoring", "rewrite", "restructure", "rearchitect",
            "performance", "bottleneck", "optimization", "profiling"
        ],
        "cost_tier": "high",
        "description": "Best for complex reasoning, advanced coding, research, and multi-step tasks"
    },
    
    # ===== MEDIUM MODELS (Balanced performance and cost) =====
    "medium": {
        "models": [
            "qwen/qwen3.5-235b-a22b-instruct-2507",
            "google/gemma-3-27b-it",
            "mistralai/mistral-medium-2505",
            "meta-llama/llama-3.1-405b-instruct",
        ],
        "priority": 2,
        "use_cases": [
            "general", "summar", "write an email", "draft",
            "translate", "convert to", "convert ", "format", "rewrite", "summarize",
            "summary", "overview", "brief", "guide", "tutorial",
            "help with", "assist me", "create a", "design a", "plan a",
            "compare", "list", "describe", "explain", "what does", "how does",
            "difference", "similar", "opposite", "example", "examples"
        ],
        "cost_tier": "medium",
        "description": "Good balance of quality and cost for general tasks"
    },
    
    # ===== SMALL / FAST MODELS (Quick tasks, simple queries) =====
    "small": {
        "models": [
            "qwen/qwen3.5-flash-02-23",
            "mistralai/mistral-nemo-2407",
            "microsoft/wizardlm-2-8x22b",
            "gryphe/mythomax-l2-13b",
        ],
        "priority": 3,
        "use_cases": [
            "hello", "hi", "hey", "thanks", "thank you",
            "quick", "simple", "fast", "short", "yes", "no",
            "format", "names", "count",
            "spelling", "grammar", "capitalize", "lowercase", "uppercase",
            "translate", "definition", "synonym", "antonym",
            "check", "is it", "is this", "verify", "confirm",
            "what is the", "what's the", "capital of", "population of",
            "age of", "when was", "who is", "simple", "basic",
            "short", "brief", "one word", "two words"
        ],
        "cost_tier": "low",
        "description": "Fast and cheap for simple queries and quick tasks"
    },
    
    # ===== CODING-SPECIALIZED =====
    "coding": {
        "models": [
            "anthropic/claude-3.5-sonnet",
            "deepseek/deepseek-coder-33b-instruct",
            "qwen/qwen-coder-2",
            "meta-llama/llama-3.3-70b-instruct",
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
            "regex", "regexp", "parsing", "parsing code"
        ],
        "cost_tier": "medium-high",
        "description": "Top choice for programming and software development tasks"
    },
    
    # ===== CREATIVE/WRITING =====
    "creative": {
        "models": [
            "anthropic/claude-3.5-sonnet",
            "mistralai/mistral-large-latest",
            "qwen/qwen2.5-72b-instruct",
            "cohere/command-r-plus-08-2024",
        ],
        "priority": 2,
        "use_cases": [
            "write a", "write an", "article", "blog", "story",
            "fiction", "creative", "poem", "poetry", "song",
            "lyric", "script", "dialogue", "scene", "character",
            "marketing", "ad", "advertisement", "copy", "sales",
            "email", "letter", "proposal", "pitch", "presentation",
            "content", "social media", "twitter", "tweet", "linkedin"
        ],
        "cost_tier": "medium",
        "description": "Best for creative writing, marketing, and content creation"
    },
    
    # ===== ANALYSIS/DATA =====
    "analysis": {
        "models": [
            "anthropic/claude-3.5-sonnet",
            "qwen/qwen2.5-72b-instruct",
            "deepseek/deepseek-chat",
            "google/gemma-2-27b-it",
        ],
        "priority": 2,
        "use_cases": [
            "analyze", "data", "statistics", "statistic",
            "calculate", "compute", "math", "formula",
            "chart", "graph", "visualize", "chart",
            "table", "csv", "json", "excel", "spreadsheet",
            "report", "summary", "insight", "pattern",
            "trend", "forecast", "predict", "comparison",
            "benchmark", "perf", "performance"
        ],
        "cost_tier": "medium",
        "description": "Strong for data analysis and quantitative tasks"
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
    # Default to first model, could implement usage tracking for smart selection
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
    model_cmd = f"hermes chat -q -m {model} \"{task}\""
    
    print(f"=== Model Selection Analysis ===")
    print(f"Task: {task}")
    print(f"Recommended Model: {model}")
    print(f"Category: {analysis['category']}")
    print(f"Reason: {analysis['reason']}")
    print(f"Confidence: {analysis['confidence']:.0%}")
    print(f"Command: {model_cmd}")
    print(f"================================")
    
    return model_cmd


def interactive_route_task():
    """Interactive mode - prompt user for task and auto-route."""
    print("\n=== Hermes Model Router ===")
    print("Enter your task (type 'quit' to exit):\n")
    
    while True:
        task = input("Your task: ").strip()
        
        if task.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
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
