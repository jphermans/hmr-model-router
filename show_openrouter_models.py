#!/usr/bin/env python3
"""
Show all available OpenRouter models with pricing and details.
Requires OPENROUTER_API_KEY to be set.
"""

import os
import sys
import requests
import json

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/models"

def get_openrouter_models():
    """Fetch all OpenRouter models."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY environment variable not set.")
        print("Please set it with: export OPENROUTER_API_KEY='your-key'")
        print("Or check ~/.hermes/.env")
        return []
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(OPENROUTER_API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return data.get("data", [])
    
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to fetch models: {e}")
        return []


def format_price(price_usd):
    """Format price for display."""
    if price_usd is None:
        return "N/A"
    return f"${price_usd:.6f}/M"


def display_models(models):
    """Display models in a formatted table."""
    if not models:
        print("No models found or unable to fetch.")
        return
    
    # Group by provider
    providers = {}
    for model in models:
        provider = model.get("id", "unknown").split("/")[0] if "/" in model.get("id", "unknown") else "other"
        
        if provider not in providers:
            providers[provider] = []
        
        providers[provider].append(model)
    
    # Sort providers by number of models
    sorted_providers = sorted(providers.items(), key=lambda x: len(x[1]), reverse=True)
    
    print(f"\n{'='*80}")
    print(f"OpenRouter Models ({len(models)} total, {len(providers)} providers)")
    print(f"{'='*80}\n")
    
    for provider, model_list in sorted_providers[:20]:  # Show top 20 providers
        print(f"\n📦 {provider.upper()} ({len(model_list)} models)")
        print(f"{'─'*80}")
        
        for i, model in enumerate(model_list[:15], 1):  # Show up to first 15 per provider
            model_id = model.get("id", "N/A")
            model_name = model.get("name", model_id)
            
            pricing = model.get("pricing", {})
            prompt_price = format_price(pricing.get("prompt"))
            completion_price = format_price(pricing.get("completion"))
            
            # Get context length
            context_len = model.get("context_length", 0)
            context_str = f"{context_len:,}" if context_len else "N/A"
            
            # Description
            description = model.get("description", "")[:50] + "..." if len(model.get("description", "")) > 50 else model.get("description", "")
            
            # Display format
            print(f"\n  {i}. {model_id}")
            print(f"     Name: {model_name}")
            print(f"     Pricing: Prompt ${prompt_price} | Completion ${completion_price}")
            print(f"     Context: {context_str:,} tokens")
            if description:
                print(f"     Desc: {description}")
    
    print(f"\n{'='*80}")
    print(f"Full list: {len(models)} models across {len(providers)} providers")
    print(f"{'='*80}\n")


def get_specific_model(model_id):
    """Get details for a specific model."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set")
        return
    
    try:
        url = f"{OPENROUTER_API_URL}/{model_id}"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        model = data.get("data", {})
        
        print(f"\nModel: {model.get('id')}")
        print(f"Name: {model.get('name')}")
        print(f"Description: {model.get('description')}")
        
        pricing = model.get("pricing", {})
        print(f"Prompt Price: ${pricing.get('prompt', 'N/A')} per M tokens")
        print(f"Completion Price: ${pricing.get('completion', 'N/A')} per M tokens")
        print(f"Context Length: {model.get('context_length', 'N/A')}")
        print(f"Top Provider: {model.get('top_provider', {}).get('name', 'N/A')}")
        
    except Exception as e:
        print(f"ERROR: {e}")


def filter_by_category(category):
    """Filter models by category keywords."""
    models = get_openrouter_models()
    
    if not models:
        return
    
    # Category search terms
    keywords = {
        "large": ["sonnet", "claude", "max", "pro", "premium", "72b", "405b", "235b"],
        "coding": ["coder", "code", "programming", "development"],
        "creative": ["command", "r", "mistral-large", "creative"],
        "medium": ["gemma", "medium", "nova", "3.5", "35b", "70b"],
        "small": ["flash", "nemo", "mini", "lite", "turbo", "8b", "13b", "small"],
        "analyst": ["deepseek", "math", "reasoning", "analytics"]
    }
    
    search_terms = keywords.get(category.lower(), [])
    
    print(f"\n{'='*80}")
    print(f"Models matching category '{category}'")
    print(f"{'='*80}\n")
    
    for model in models:
        model_id = model.get("id", "").lower()
        model_name = model.get("name", "").lower()
        
        if any(term in model_id or term in model_name for term in search_terms):
            pricing = model.get("pricing", {})
            print(f"  {model.get('id')}")
            print(f"    → {model.get('name')}: $ {pricing.get('prompt')} prompt / ${pricing.get('completion')} completion")

def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        # Specific model ID
        if arg and not arg.startswith("-"):
            print(f"Fetching details for: {arg}")
            get_specific_model(arg)
            return
        
        # Filter by category
        if arg in ["large", "coding", "creative", "medium", "small", "analysis"]:
            filter_by_category(arg)
            return
        
        # Help/usage
        if arg == "-h" or arg == "--help":
            print("Usage: show_openrouter_models.py [options]")
            print("\nOptions:")
            print("  (none)          - List all models")
            print("  model-id        - Show details for specific model")
            print("  large           - Show large models")
            print("  coding          - Show coding models")
            print("  creative        - Show creative models")
            print("  medium          - Show medium models")
            print("  small           - Show small models")
            print("  analysis        - Show analysis models")
            return
    
    # Default: list all models
    models = get_openrouter_models()
    display_models(models)


if __name__ == "__main__":
    main()
