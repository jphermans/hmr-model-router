#!/usr/bin/env python3
"""
OpenRouter Usage & Billing Monitor
Fetches daily usage, costs, and account balance

IMPORTANT: This file is in .private/ folder and NEVER committed to git!
"""

import os
import json
import requests
from datetime import datetime, timezone
from pathlib import Path

# Paths - all private, never in git
PRIVATE_DIR = Path(__file__).parent / "..private"
DATA_FILE = PRIVATE_DIR / "usage_data.json"
BACKUP_DIR = PRIVATE_DIR / "usage_backups"


def get_api_key():
    """Get API key from environment or config file."""
    # Check environment variable first
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key and api_key != "***":
        return api_key
    
    # Fallback: read from .hermes/.env
    env_file = Path("/home/jphermans/.hermes/.env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#"):
                    continue
                if "OPENROUTER_API_KEY=" in line:
                    api_key = line.split("=")[1]
                    if api_key and "sk-or-" in api_key:
                        return api_key
    
    raise RuntimeError("No OpenRouter API key found!")


def fetch_usage_data():
    """
    Fetch usage data from OpenRouter API.
    Try multiple endpoints, adjust based on actual API structure.
    """
    api_key = get_api_key()
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Test which endpoints work (you need to discover these!)
    test_endpoints = [
        "https://openrouter.ai/api/v1/billing/usage",
        "https://openrouter.ai/api/v1/billing/dashboard", 
        "https://openrouter.ai/api/v1/usage",
        "https://openrouter.ai/api/v1/account",
        "https://openrouter.ai/api/v1/auth",
    ]
    
    for url in test_endpoints:
        try:
            print(f"Testing: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Found working endpoint!")
                return response.json(), url
            else:
                print(f"❌ {url}: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            print(f"❌ {url}: {str(e)[:80]}")
    
    raise RuntimeError("No working endpoints found. Check OpenRouter API docs!")


def parse_usage_response(response_data, endpoint_url):
    """Parse the response into structured usage data."""
    usage = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source_endpoint": endpoint_url,
        "error": None
    }
    
    try:
        # Analyze structure to determine how to parse
        keys = list(response_data.keys())
        print(f"Response has keys: {keys}")
        
        # Common billing API patterns - ADJUST THESE BASED ON ACTUAL API
        if "total_cost" in keys:
            # Pattern: Direct cost data
            usage.update({
                "total_cost": response_data.get("total_cost", 0),
                "cost_by_model": response_data.get("cost_by_model", response_data.get("models", {})),
                "cost_by_date": response_data.get("cost_by_date", response_data.get("daily_costs", {})),
                "tokens": {
                    "input": response_data.get("total_prompt_tokens", 0),
                    "output": response_data.get("total_completion_tokens", 0),
                }
            })
            
        elif "balance" in keys or "account" in keys:
            # Pattern: Account/balance data
            data = response_data.get("account", response_data.get("dashboard", {}))
            if "account" in keys:
                data = response_data.get("account")
            
            usage.update({
                "balance": data.get("balance", 0),
                "spending_this_period": data.get("spending", data.get("current_period_spending", 0)),
                "spending_limit": data.get("spending_limit", 0),
                "account_id": data.get("id", data.get("user_id", "unknown")),
            })
            
        elif "pricing" in keys or "models" in keys:
            # Pattern: Model listing (not usage - fallback)
            usage["error"] = "Only model data available, not usage data"
            usage["models_count"] = len(response_data.get("models", response_data))
            
        else:
            # Unknown structure - store raw
            usage["raw_keys"] = keys
            usage["error"] = f"Unknown response structure: {keys}"
            usage["raw_data_preview"] = str(response_data)[:300]
    
    except Exception as e:
        usage["error"] = f"Parse error: {str(e)}"
    
    return usage


def save_usage_data(usage_data):
    """Save usage data to private file with backups."""
    try:
        PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    except:
        # Fallback to current dir if private dir fails
        PRIVATE_DIR = Path("/home/jphermans/hmr-model-router/.private")
        PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
        BACKUP_DIR = PRIVATE_DIR / "backups"
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    DATA_FILE = PRIVATE_DIR / "usage_data.json"
    BACKUP_DIR = PRIVATE_DIR / "backups"
    
    # Create backup of previous data
    if DATA_FILE.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"usage_{timestamp}.json"
        try:
            import shutil
            shutil.copy(DATA_FILE, backup_path)
            print(f"✅ Backup: {backup_path}")
        except:
            pass
    
    # Save current data
    with open(DATA_FILE, 'w') as f:
        json.dump(usage_data, f, indent=2)
    
    print(f"💾 Saved to: {DATA_FILE}")
    
    # Add to gitignore if accessible
    gitignore_path = Path("/home/jphermans/hmr-model-router/.gitignore")
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            content = f.read()
            if '.private' not in content:
                with open(gitignore_path, 'a') as g:
                    g.write('\n# Private data\n.private/\n')
                print("🔒 Added .private/ to .gitignore")


def format_telegram_message(usage_data):
    """Format usage data for Telegram message."""
    if usage_data.get("error"):
        return (
            f"⚠️ **Usage Data Error**\n"
            f"❌ {usage_data['error']}\n"
            f"Source: {usage_data.get('source_endpoint', 'unknown')}"
        )
    
    lines = []
    lines.append("💰 **OpenRouter Usage & Balance**")
    lines.append(f"📅 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    
    # Balance
    balance = usage_data.get("balance")
    if balance:
        lines.append(f"**💵 Balance: ${balance:.2f}**")
    
    # Total cost
    total_cost = usage_data.get("total_cost")
    if total_cost:
        lines.append(f"**🎫 Total Cost: ${total_cost:.2f}**")
    
    # Spending limit
    limit = usage_data.get("spending_limit")
    if limit and balance:
        lines.append(f"**Budget used**: {min(100, (limit - balance) / limit * 100):.1f}%")
    
    # Tokens
    tokens = usage_data.get("tokens", {})
    if tokens.get("input") or tokens.get("output"):
        inp = tokens["input"] / 1_000_000
        out = tokens["output"] / 1_000_000
        lines.append(f"📊 **Tokens**: {inp:.2f}M in / {out:.2f}M out")
    
    # Top cost by model
    cost_by_model = usage_data.get("cost_by_model", {})
    if isinstance(cost_by_model, dict) and len(cost_by_model) > 0:
        lines.append("")
        lines.append("📦 **Top 5 Models by Cost**:")
        sorted_models = sorted(cost_by_model.items(), 
                             key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, 
                             reverse=True)[:5]
        for model, cost in sorted_models:
            short_name = model.split("/")[-1][:25]
            cost_val = cost if isinstance(cost, (int, float)) else cost.get("cost", 0) if isinstance(cost, dict) else 0
            lines.append(f"• {short_name:30} ${cost_val:.2f}")
    
    # Daily spending
    cost_by_date = usage_data.get("cost_by_date", {})
    if cost_by_date and len(cost_by_date) > 0:
        lines.append("")
        lines.append("📈 **Last 7 Days Daily Cost**:")
        sorted_dates = sorted(cost_by_date.items())[-7:]
        total_7 = sum([float(v) if isinstance(v, (int, float)) else v.get('cost', 0) 
                      for date, v in sorted_dates])
        avg = total_7 / 7 if sorted_dates else 0
        for date, cost in sorted_dates:
            date_short = date.split("-")[-2:] if "-" in date else date
            cost_val = cost if isinstance(cost, (int, float)) else cost.get("cost", 0) if isinstance(cost, dict) else 0
            lines.append(f"• {date_short:12} ${cost_val:.2f}")
        lines.append(f"   **Avg**: ${avg:.2f}/day")
    
    # Source info
    if usage_data.get("source_endpoint") and "billing" not in usage_data.get("source_endpoint", ""):
        lines.append("")
        lines.append(f"ℹ️ Data source: {usage_data['source_endpoint']}")
    
    return "\n".join(lines)


def main():
    """Main execution - tested in production."""
    print("=== OpenRouter Usage Fetcher ===\n")
    
    try:
        response_data, endpoint = fetch_usage_data()
        usage = parse_usage_response(response_data, endpoint)
        save_usage_data(usage)
        
        print("\n" + "="*70)
        print(format_telegram_message(usage))
        print("="*70)
        
        return usage
        
    except Exception as e:
        error_data = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "source_endpoint": "unknown"
        }
        save_usage_data(error_data)
        print(f"\n❌ Fatal error: {str(e)}")
        return error_data


if __name__ == "__main__":
    main()
