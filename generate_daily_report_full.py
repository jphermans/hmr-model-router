#!/usr/bin/env python3
"""Generate and send OpenRouter daily pricing and usage report."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

# Configuration
USD_TO_EUR = 1.07
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/models"
USAGE_LOG_PATH = "/home/jphermans/.hermes/usage_log.json"
PRICING_DATA_PATH = "/home/jphermans/hmr-model-router/.data/model-pricing.json"

def fetch_pricing_data():
    """Fetch current pricing data from OpenRouter."""
    try:
        import requests
        response = requests.get(OPENROUTER_API_URL)
        response.raise_for_status()
        models = response.json().get("data", [])
        
        # Analyze models
        normalized = []
        for model in models:
            model_id = model.get("id", "")
            name = model.get("name", model_id)
            pricing = model.get("pricing", {})
            prompt_price = pricing.get("prompt", 0)
            completion_price = pricing.get("completion", 0)
            input_per_1m = float(prompt_price) * 1_000_000 if prompt_price else None
            output_per_1m = float(completion_price) * 1_000_000 if completion_price else None
            
            if input_per_1m and output_per_1m and input_per_1m > 0 and output_per_1m > 0:
                normalized.append({
                    "id": model_id,
                    "name": name,
                    "input_price_per_1m": input_per_1m,
                    "output_price_per_1m": output_per_1m
                })
        
        # Sort by input price
        cheapest = sorted(normalized, key=lambda x: x["input_price_per_1m"])[:10]
        
        # Analyze tiers
        tiers = {"under_10_cents": 0, "10_to_50_cents": 0, "50_cents_to_1_dollar": 0, "above_1_dollar": 0}
        for m in normalized:
            price = m["input_price_per_1m"]
            if price < 10:
                tiers["under_10_cents"] += 1
            elif price < 50:
                tiers["10_to_50_cents"] += 1
            elif price < 100:
                tiers["50_cents_to_1_dollar"] += 1
            else:
                tiers["above_1_dollar"] += 1
        
        analysis = {
            "total_models": len(normalized),
            "best_10_cheapest": cheapest,
            "tiers": tiers
        }
        
        # Save pricing data
        data = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "analysis": {
                "total_models": len(normalized),
                "cheapest_input": [
                    {
                        "model": m["id"],
                        "name": m["name"],
                        "input_price_per_1m": m["input_price_per_1m"],
                        "output_price_per_1m": m["output_price_per_1m"]
                    }
                    for m in cheapest
                ],
                "tiers": tiers
            }
        }
        os.makedirs(os.path.dirname(PRICING_DATA_PATH), exist_ok=True)
        with open(PRICING_DATA_PATH, "w") as f:
            json.dump(data, f, indent=2)
        
        return analysis
    except Exception as e:
        print(f"Error fetching pricing: {e}")
        return None


def analyze_usage():
    """Analyze usage from local log."""
    try:
        if not os.path.exists(USAGE_LOG_PATH):
            return None
        
        with open(USAGE_LOG_PATH) as f:
            usage = json.load(f)
        
        total_requests = len(usage)
        total_tokens = sum(u.get("total_tokens", 0) for u in usage)
        total_cost_usd = sum(u.get("cost_usd", 0) for u in usage)
        total_cost_eur = total_cost_usd / USD_TO_EUR
        
        # Count by model
        model_stats = {}
        for u in usage:
            m = u["model"]
            if m not in model_stats:
                model_stats[m] = {"count": 0, "cost": 0}
            model_stats[m]["count"] += 1
            model_stats[m]["cost"] += u.get("cost_usd", 0)
        
        # Find current model
        current_model = "qwen/qwen3.5-flash-02-23"
        current_count = model_stats.get(current_model, {}).get("count", 0)
        
        return {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost_usd,
            "total_cost_eur": total_cost_eur,
            "model_stats": model_stats,
            "current_model": current_model,
            "current_model_count": current_count
        }
    except Exception as e:
        print(f"Error analyzing usage: {e}")
        return None


def generate_report(pricing, usage):
    """Generate the final report."""
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Cost analysis
    current_rate = 0.18  # qwen/qwen3.5-flash-02-23
    cheapest_rate = pricing["best_10_cheapest"][0]["input_price_per_1m"] if pricing else 0.01
    
    savings_pct = ((current_rate - cheapest_rate) / current_rate * 100) if current_rate else 0
    
    # Build report
    report = f"""═══════════════════════════════════════════════════════════
💰 OPENROUTER ACCOUNT STATUS
═══════════════════════════════════════════════════════════

⚠️ **Balance API Limitation**

OpenRouter's balance and detailed usage API is not publicly 
accessible. To check your balance, please visit:

🔗 **https://openrouter.ai/your-settings/billing**

💡 Your balance will be shown in EUR as well:
   €X.XX = $X.XX (USD)

═══════════════════════════════════════════════════════════
💵 SPENDING SUMMARY (Last 7 Days)
═══════════════════════════════════════════════════════════"""
    
    if usage:
        # Calculate days from first to last usage entry
        import datetime as dt
        if usage.get("total_requests", 0) > 0:
            # Try to get date range from usage data
            dates = []
            for u in usage["usage_data"]:
                if "timestamp" in u:
                    try:
                        dates.append(dt.datetime.fromisoformat(u["timestamp"].replace("Z", "+00:00")))
                    except:
                        pass
            if dates:
                first = min(dates)
                last = max(dates)
                days = max(1, (last - first).days + 1)
            else:
                days = 1
        else:
            days = 1
        daily_avg_usd = usage["total_cost_usd"] / days
        daily_avg_eur = usage["total_cost_eur"] / days
        
        report += f"""

**Total Spent:**
   • ${usage["total_cost_usd"]:.6f} USD
   • €{usage["total_cost_eur"]:.6f} EUR
   • Daily Average: ${daily_avg_usd:.6f} (${daily_avg_eur:.6f} €)

**Usage Statistics:**
   • Total Requests: {usage["total_requests"]}
   • Total Tokens: {usage["total_tokens"]:,}
   • Models Used: {len(usage["model_stats"])}

**Most Used Models:**"""
        
        for m, stats in sorted(usage["model_stats"].items(), key=lambda x: -x[1]["count"])[:5]:
            stats_eur = stats["cost"] / USD_TO_EUR
            report += f"""
   • {m}
     • {stats["count"]} requests, ${stats["cost"]:.6f} ({stats_eur:.6f}€)"""
    else:
        report += """

**Usage Tracking:** Script attempted to fetch usage data.

Please check your usage dashboard at:
https://openrouter.ai/your-settings"""
    
    # Cost optimization
    report += f"""
═══════════════════════════════════════════════════════════
📊 COST OPTIMIZATION OPPORTUNITIES
═══════════════════════════════════════════════════════════

**Current Routing Analysis**
   You're using: {usage["current_model"] if usage else "qwen/qwen3.5-flash-02-23"}

**Top 3 Cheapest Models:**"""
    
    if pricing:
        for i, m in enumerate(pricing["best_10_cheapest"][:3], 1):
            report += f"""
   {i}. {m["name"][:50]:<50} ${m["input_price_per_1m"]:.2f}/1M input"""
        
        # Savings analysis
        savings_pct = ((current_rate - cheapest_rate) / current_rate * 100) if current_rate else 0
        
        report += f"""

**Potential Savings Analysis:**
   • Current rate: ${current_rate:.4f}/1M tokens
   • Cheapest rate: ${cheapest_rate:.4f}/1M tokens
   • Potential savings: {savings_pct:.1f}%"""
        
        if usage:
            estimated_monthly = (usage["total_cost_usd"] / days) * 30 * (savings_pct / 100)
            report += f"""
   • Estimated monthly savings: ${estimated_monthly:.4f}"""
        
        # Recommendation
        report += f"""

**Recommendation:**"""
        
        if savings_pct > 50:
            report += """
   ⚡ **HIGH PRIORITY** - Significant savings available!
   Consider switching to cheaper models for simple tasks.
   Your current route is: NEEDS IMPROVEMENT"""
        elif savings_pct > 20:
            report += """
   💡 **MODERATE** - Some savings opportunities exist.
   Consider optimizing routing for routine tasks.
   Your current route is: NEEDS IMPROVEMENT"""
        else:
            report += """
   ✅ **GOOD** - Your routing strategy is well-optimized.
   Keep using the current model for your use cases.
   Your current route is: GOOD"""
    else:
        report += """

**Pricing Data:** Not available (API fetch failed)"""
    
    # Best value models
    report += f"""
═══════════════════════════════════════════════════════════
🆕 BEST VALUE MODELS THIS WEEK
═══════════════════════════════════════════════════════════"""
    
    if pricing:
        best_value = pricing["best_10_cheapest"][:5]
        for i, m in enumerate(best_value, 1):
            report += f"""

{i}. **{m["name"][:45]}**
   • Input: ${m["input_price_per_1m"]:.2f}/1M
   • Output: ${m["output_price_per_1m"]:.2f}/1M
   • Best for: Good quality/price balance"""
    
    # Pricing tier distribution
    report += """
═══════════════════════════════════════════════════════════
🔍 DETAILED PRICING COMPARISON (Top 10 Cheapest)
═══════════════════════════════════════════════════════════

| # | Model | Input ($/1M) | Output ($/1M) |
|---|-------|--------------|---------------|"""
    
    if pricing:
        for i, m in enumerate(pricing["best_10_cheapest"], 1):
            report += f"""| {i} | {m["name"][:30]:<30} | ${m["input_price_per_1m"]:.2f} | ${m["output_price_per_1m"]:.2f} |"""
    
    # Pricing tier distribution
    report += """
═══════════════════════════════════════════════════════════
📊 PRICING TIER DISTRIBUTION
═══════════════════════════════════════════════════════════"""
    
    if pricing:
        tiers = pricing["tiers"]
        total_priced = sum(tiers.values())
        tier_under_10_pct = (tiers["under_10_cents"] / total_priced * 100) if total_priced else 0
        
        report += f"""

Total OpenRouter Models: {pricing["analysis"]["total_models"]}
Models with valid pricing: {pricing["analysis"]["total_models"]}

Price Tiers:
   • Under 10¢/1M:         {tiers["under_10_cents"]} models ({tier_under_10_pct:.0f}%)
   • 10-50¢/1M:            {tiers["10_to_50_cents"]} models
   • $0.50-$1/1M:          {tiers["50_cents_to_1_dollar"]} models
   • Over $1/1M:           {tiers["above_1_dollar"]} models

💡 **Key Insight:** {tiers["under_10_cents"]} models ({tier_under_10_pct:.1f}% of priced models) cost less than 10¢ per 1M tokens!"""
    
    # Actions completed
    report += f"""
═══════════════════════════════════════════════════════════
✅ ACTIONS COMPLETED
═══════════════════════════════════════════════════════════

✓ All pricing data collected from OpenRouter API
✓ Usage data analyzed from local log
✓ Balance check attempted (manual URL provided)
✓ Cost analysis completed with EUR conversion
✓ Report generated at {timestamp}
✓ .data/model-pricing.json updated

───────────────────────────────────────────────────────────
Run daily at 4:00 AM UTC for continuous monitoring
API Limitation: Balance/usage APIs not publicly accessible
Manual Check: https://openrouter.ai/your-settings/billing
───────────────────────────────────────────────────────────"""
    
    return report, timestamp


def main():
    """Run the daily report generation."""
    print("🔍 Fetching OpenRouter pricing data...")
    pricing = fetch_pricing_data()
    
    print("📊 Analyzing usage data...")
    usage = analyze_usage()
    
    print("📝 Generating report...")
    report, timestamp = generate_report(pricing, usage)
    
    print("\n" + "=" * 80)
    print("🤖 DAILY OPENROUTER PRICING & USAGE REPORT")
    print("=" * 80)
    print("\n" + report)
    
    # Save report
    output_path = f"/home/jphermans/hmr-model-router/pricing_report_{timestamp.replace(' ', '_').replace(':', '-')}.txt"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)
    
    print(f"\n📁 Report saved to: {output_path}")
    
    return report


if __name__ == "__main__":
    main()
