#!/usr/bin/env python3
"""
Fetch and analyze OpenRouter model pricing data.
Run manually or use as reference for daily cron job.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system("pip3 install requests -q")
    import requests

API_URL = "https://openrouter.ai/api/v1/models"
OUTPUT_FOLDER = Path("/home/jphermans/hmr-model-router/.data")


def fetch_models():
    """Fetch all models from OpenRouter API."""
    print(f"Fetching models from {API_URL}...")
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json().get("data", [])


def analyze_models(models):
    """Analyze models and find best prices."""
    print(f"Analyzing {len(models)} models...")
    
    # Normalize pricing data
    normalized = []
    for model in models:
        model_id = model.get("id", "")
        name = model.get("name", model_id)
        
        pricing = model.get("pricing", {})
        # OpenRouter uses "prompt" for input and "completion" for output
        prompt_price = pricing.get("prompt", 0)  # input price per token
        completion_price = pricing.get("completion", 0)  # output price per token
        
        # Convert to per 1M tokens (OpenRouter uses per token)
        input_per_1m = float(prompt_price) * 1_000_000 if prompt_price else None
        output_per_1m = float(completion_price) * 1_000_000 if completion_price else None
        
        normalized.append({
            "id": model_id,
            "name": name,
            "input_price_per_1m": input_per_1m,
            "output_price_per_1m": output_per_1m,
            "context_length": model.get("context_length", 0),
            "top_provider": model.get("top_provider", {}).get("confidence", 0),
            "raw_pricing": pricing
        })
    
    # Filter to models with valid pricing
    # Exclude router models with negative or invalid pricing
    priced_models = [
        m for m in normalized 
        if m["input_price_per_1m"] is not None 
        and m["output_price_per_1m"] is not None
        and m["input_price_per_1m"] > 0
        and m["output_price_per_1m"] > 0
    ]
    
    # Find cheapest by input price
    cheapest_input = sorted(priced_models, key=lambda x: x["input_price_per_1m"] or float('inf'))[:10]
    
    # Find cheapest by output price
    cheapest_output = sorted(priced_models, key=lambda x: x["output_price_per_1m"] or float('inf'))[:10]
    
    # Find best value - cheapest models under $0.50 input
    under_50 = [m for m in priced_models if m["input_price_per_1m"] < 50]
    best_value = sorted(under_50, 
                       key=lambda x: x["input_price_per_1m"])[:20]  # First 20 cheapest
    
    # Group by price tier
    tiers = {
        "under_10_cents": [],
        "10_to_50_cents": [],
        "50_cents_to_1_dollar": [],
        "above_1_dollar": []
    }
    
    for m in priced_models:
        price = m["input_price_per_1m"]
        if price < 10:
            tiers["under_10_cents"].append(m)
        elif price < 50:
            tiers["10_to_50_cents"].append(m)
        elif price < 100:
            tiers["50_cents_to_1_dollar"].append(m)
        else:
            tiers["above_1_dollar"].append(m)
    
    return {
        "total_models": len(normalized),
        "priced_models": len(priced_models),
        "cheapest_input": cheapest_input[:10],
        "cheapest_output": cheapest_output[:10],
        "best_value_under_50_cents": best_value,
        "tiers": {k: len(v) for k, v in tiers.items()},
        "by_tier": tiers
    }


def format_price(price):
    """Format price in dollars."""
    if price is None:
        return "N/A"
    return f"${price:.2f}"


def get_model_use_case(model_id):
    """Recommended use case based on model ID."""
    model_lower = model_id.lower()
    
    # Coding models
    if "coder" in model_lower or "deepseek-coder" in model_lower:
        return "📝 Coding & programming tasks"
    
    # IBM & Llama - general purpose
    if "granite" in model_lower or "llama" in model_lower:
        return "🤖 General chat & simple tasks"
    
    # Mistral
    if "mistral" in model_lower:
        return "✨ Balanced performance"
    
    # Gemma
    if "gemma" in model_lower:
        return "📚 Summaries & explanations"
    
    # Phi
    if "phi" in model_lower:
        return "⚡ Fast simple queries"
    
    # DeepSeek
    if "deepseek" in model_lower:
        return "🧠 Complex reasoning & analysis"
    
    # Qwen
    if "qwen" in model_lower:
        return "💡 General tasks & multilingual"
    
    # Anthropic Claude
    if "claude" in model_lower:
        return "🏆 Premium quality"
    
    # OpenAI GPT
    if "gpt" in model_lower:
        return "🌟 High quality general use"
    
    return "📝 Good for general tasks"


def print_report(analysis):
    """Print human-readable report."""
    print("\n" + "="*80)
    print("🤖 OPENROUTER MODEL PRICING REPORT")
    print("="*80)
    
    print(f"\n📊 Summary:")
    print(f"  • Total models: {analysis['total_models']}")
    print(f"  • Models with pricing: {analysis['priced_models']}")
    print(f"  • Price tiers: {analysis['tiers']}")
    
    print(f"\n💰 Top 10 Cheapest Input:")
    for i, m in enumerate(analysis["cheapest_input"][:10], 1):
        usage = get_model_use_case(m['id'])
        print(f"  {i}. {m['name'][:50]}")
        print(f"     Input: {format_price(m['input_price_per_1m'])}/1M |")
        print(f"     Output: {format_price(m['output_price_per_1m'])}/1M")
        print(f"     💡 Best for: {usage}")
    
    print(f"\n⭐ Best Value (under $0.50 input):")
    for m in analysis["best_value_under_50_cents"][:10]:
        print(f"  • {m['name'][:50]} - {format_price(m['input_price_per_1m'])}/{format_price(m['output_price_per_1m'])}")
    
    print("\n" + "="*80)


def save_to_file(analysis, repo_path):
    """Save analysis to JSON file."""
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    
    data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "analysis": {
            "total_models": analysis["total_models"],
            "priced_models": analysis["priced_models"],
            "cheapest_input": [
                {"model": m["id"], "name": m["name"], "price_per_1m": m["input_price_per_1m"]}
                for m in analysis["cheapest_input"]
            ],
            "best_value_under_50_cents": [
                {
                    "model": m["id"],
                    "name": m["name"],
                    "input_per_1m": m["input_price_per_1m"],
                    "output_per_1m": m["output_price_per_1m"]
                }
                for m in analysis["best_value_under_50_cents"]
            ],
            "tiers": analysis["tiers"]
        }
    }
    
    output_file = OUTPUT_FOLDER / "model-pricing.json"
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n💾 Saved to: {output_file}")
    return data, output_file


def compare_with_previous(output_file):
    """Compare with previous data if exists."""
    if not output_file.exists():
        print("\n📝 First run - no previous data to compare")
        return "first_run", None
    
    with open(output_file) as f:
        previous = json.load(f)
    
    changes = {
        "pricing_updated": False,
        "new_models": False,
        "model_count_change": 0
    }
    
    return changes, previous


def get_telegram_summary(current_analysis, previous_data=None):
    """Generate Telegram message format."""
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Extract top 3 cheapest
    top3 = [m for m in sorted(current_analysis["cheapest_input"], key=lambda x: x["input_price_per_1m"] or float('inf'))[:3]]
    
    # Extract best value examples
    best_value = current_analysis["best_value_under_50_cents"][:3]
    
    # Check for new models
    new_model_count = 0
    if previous_data:
        prev_count = previous_data.get("analysis", {}).get("total_models", 0)
        curr_count = current_analysis["total_models"]
        new_model_count = curr_count - prev_count
    
    telegram_msg = f"""
🤖 Daily Model Pricing Update - {date}

📊 Summary:
• Total models: {current_analysis['total_models']}
• Models with pricing: {current_analysis['priced_models']}
• Price tiers:  
  - Under 10¢: {current_analysis['tiers'].get('under_10_cents', 0)}
  - 10-50¢: {current_analysis['tiers'].get('10_to_50_cents', 0)}
  - $0.50-1: {current_analysis['tiers'].get('50_cents_to_1_dollar', 0)}
  - Over $1: {current_analysis['tiers'].get('above_1_dollar', 0)}
• New models detected: {new_model_count}

💰 Top 3 Cheapest Models:
"""
    
    for i, m in enumerate(top3, 1):
        usage = get_model_use_case(m["id"])
        telegram_msg += f"{i}. {m['name'][:40]:<40} ${m['input_price_per_1m']:.2f}/M\n   💡 {usage}\n"
    
    telegram_msg += "\n⭐ Best Value (under $0.50):\n"
    for m in best_value:
        usage = get_model_use_case(m["id"])[:30]
        telegram_msg += f"• {m['name'][:40]:<40} ${m['input_price_per_1m']:.2f}/${m['output_price_per_1m']:.2f} ({usage})\n"
    
    telegram_msg += "\n📁 Full data: `.data/model-pricing.json`"
    
    return telegram_msg.strip()


def main():
    repo_path = "/home/jphermans/hmr-model-router"
    output_file = OUTPUT_FOLDER / "model-pricing.json"
    
    # Fetch data
    models = fetch_models()
    
    # Analyze
    analysis = analyze_models(models)
    
    # Print report
    print_report(analysis)
    
    # Save to file
    current_data, output_file = save_to_file(analysis, repo_path)
    
    # Compare with previous
    changes, previous_data = compare_with_previous(output_file)
    
    # Generate Telegram summary
    telegram_msg = get_telegram_summary(analysis, previous_data)
    
    # Print Telegram message
    print("\n" + "="*80)
    print("TELEGRAM MESSAGE:")
    print("="*80)
    print(telegram_msg)
    
    # If first run, mark that we need to commit
    if changes == "first_run":
        print("\n✅ This is the first run - commit and push data file")
    
    return 0


if __name__ == "__main__":
    main()
