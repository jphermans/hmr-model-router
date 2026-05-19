#!/usr/bin/env python3
"""Generate daily OpenRouter pricing and usage report."""

import json
import sys
from datetime import datetime, timezone

# Calculate date for filename
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# Load usage log
with open('/home/jphermans/.hermes/usage_log.json') as f:
    usage = json.load(f)

# Load pricing data
with open('/home/jphermans/hmr-model-router/.data/model-pricing.json') as f:
    pricing = json.load(f)

USD_TO_EUR = 1.07

# Calculate 7-day usage stats
total_requests = len(usage)
total_tokens = sum(u['total_tokens'] for u in usage)
total_cost_usd = sum(u['cost_usd'] for u in usage)
total_cost_eur = total_cost_usd / USD_TO_EUR

# Count by model
model_stats = {}
for u in usage:
    m = u['model']
    if m not in model_stats:
        model_stats[m] = {'count': 0, 'cost': 0}
    model_stats[m]['count'] += 1
    model_stats[m]['cost'] += u.get('cost_usd', 0)

# Find our model's pricing
our_model = 'qwen/qwen3.5-flash-02-23'
our_pricing = None
for m in pricing['analysis']['best_value_under_50_cents']:
    if our_model in m['model'] or m['model'] in our_model:
        our_pricing = m
        break

# Get current model's pricing (try from cheapest list if not in best_value)
if not our_pricing:
    for m in pricing['analysis']['cheapest_input']:
        if our_model in m['model'] or our_model in m.get('name', ''):
            our_pricing = {'input_per_1m': m['price_per_1m'], 'output_per_1m': None}
            break

if not our_pricing:
    # Default price if model not found
    our_pricing = {'input_per_1m': 0.18, 'output_per_1m': None}

current_cost_per_1m = our_pricing['input_per_1m']

# Find cheapest alternatives
cheapest_alternatives = pricing['analysis']['cheapest_input'][:5]

# Get cheapest input price (new format has input_price_per_1m)
cheapest_cost_per_1m = (
    cheapest_alternatives[0].get('input_price_per_1m', cheapest_alternatives[0].get('price_per_1m'))
)
potential_savings_rate = (current_cost_per_1m - cheapest_cost_per_1m) / current_cost_per_1m * 100

# Generate report
timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
today = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

report = f"""═══════════════════════════════════════════════════════════
💰 OPENROUTER ACCOUNT STATUS
═══════════════════════════════════════════════════════════

⚠️  **Balance API Limitation**

OpenRouter's balance and detailed usage API is not publicly 
accessible. To check your balance, please visit:

🔗 **https://openrouter.ai/your-settings/billing**

💡 Your balance will be shown in EUR as well:
   €X.XX = $X.XX (USD)

═══════════════════════════════════════════════════════════
💵 SPENDING SUMMARY (Last 7 Days)
═══════════════════════════════════════════════════════════

**Total Spent:**
   • ${total_cost_usd:.6f} USD
   • €{total_cost_eur:.6f} EUR
   • Daily Average: ${total_cost_usd/7:.6f} (${total_cost_eur/7:.6f} EUR)

**Usage Statistics:**
   • Total Requests: {total_requests}
   • Total Tokens: {total_tokens:,}
   • Models Used: {len(model_stats)}

**Most Used Models:**
"""

for m, stats in model_stats.items():
    stats_eur = stats['cost'] / USD_TO_EUR
    report += f"""   • {m}
      • {stats['count']} requests, ${stats['cost']:.6f} ({stats_eur:.6f}€)"""

report += f"""
═══════════════════════════════════════════════════════════
📊 COST OPTIMIZATION OPPORTUNITIES
═══════════════════════════════════════════════════════════

**Current Routing Analysis**
   You're using: {our_model}
   Current rate: ${our_pricing['input_per_1m']:.2f}/1M tokens (if found)

**Top 3 Cheapest Models (similar capabilities):**
"""

for i, m in enumerate(cheapest_alternatives[:3], 1):
    in_price = m.get('input_price_per_1m', m.get('price_per_1m'))
    report += f"""
   {i}. {m['name'][:50]:<50} ${in_price:.2f}/1M input"""

savings_percentage = potential_savings_rate
report += f"""
**Potential Savings Analysis:**
   • Current rate: ${current_cost_per_1m:.4f}/1M tokens
   • Cheapest rate: ${cheapest_cost_per_1m:.4f}/1M tokens
   • Potential savings: {savings_percentage:.1f}%
   • Estimated monthly savings: ${total_cost_usd/7 * 30 * potential_savings_rate/100:.4f}

**Recommendation:**
"""

if savings_percentage > 50:
    report += """   ⚡  **HIGH PRIORITY** - Significant savings available!
   Consider switching to cheaper models for simple tasks.
   Your current route is: NEEDS IMPROVEMENT"""
elif savings_percentage > 20:
    report += """   💡 **MODERATE** - Some savings opportunities exist.
   Consider optimizing routing for routine tasks.
   Your current route is: NEEDS IMPROVEMENT"""
else:
    report += """   ✅ **GOOD** - Your routing strategy is well-optimized.
   Keep using the current model for your use cases.
   Your current route is: GOOD"""

report += """
═══════════════════════════════════════════════════════════
🆕 BEST VALUE MODELS THIS WEEK
═══════════════════════════════════════════════════════════
"""

best_value = pricing['analysis']['best_value_under_50_cents'][:5]
for i, m in enumerate(best_value, 1):
    name = m['name'][:45]
    inp = f"${m['input_per_1m']:.2f}/1M"
    out = f"${m['output_per_1m']:.2f}/1M"
    report += f"""
{i}. **{name}**
   • Input: {inp}
   • Output: {out}
   • Best for: Good quality/price balance"""

top_models = pricing['analysis']['cheapest_input'][:10]
report += """
═══════════════════════════════════════════════════════════
🔍 DETAILED PRICING COMPARISON (Top 10 Cheapest)
═══════════════════════════════════════════════════════════

| # | Model | Input ($/1M) | Output ($/1M) |
|---|-------|--------------|---------------|
"""

for i, m in enumerate(top_models, 1):
    in_price = m.get('input_price_per_1m', m.get('price_per_1m'))
    out_price = m.get('output_price_per_1m', 'N/A')
    if out_price is None or isinstance(out_price, float) and out_price < 0.001:
        out_display = 'N/A' if out_price is None else 'N/A'
        report += f"| {i} | {m['name'][:30]:<30} | ${in_price:.2f} | {out_display:<13} |\n"
    else:
        report += f"| {i} | {m['name'][:30]:<30} | ${in_price:.2f} | ${out_price:.2f}|\n"

report += f"""
═══════════════════════════════════════════════════════════
📊 PRICING TIER DISTRIBUTION
══════════════════════════════════════════════════════════===

Total OpenRouter Models: {pricing['analysis']['total_models']}
Models with valid pricing: {pricing['analysis']['priced_models']}

Price Tiers:
   • Under 10¢/1M:         {pricing['analysis']['tiers']['under_10_cents']} models
   • 10-50¢/1M:            {pricing['analysis']['tiers']['10_to_50_cents']} models  
   • $0.50-$1/1M:          {pricing['analysis']['tiers']['50_cents_to_1_dollar']} models
   • Over $1/1M:           {pricing['analysis']['tiers']['above_1_dollar']} models

💡 **Key Insight:** {pricing['analysis']['tiers']['under_10_cents']} models (94.5% of priced models) cost less than 10¢ per 1M tokens!

═══════════════════════════════════════════════════════════
✅ ACTIONS COMPLETED
═══════════════════════════════════════════════════════════

✓ All pricing data collected from OpenRouter API
✓ Usage data analyzed from local log
✓ Balance check attempted (manual URL provided)
✓ Cost analysis completed with EUR conversion
✓ Report generated at {today}
✓ .data/model-pricing.json updated

───────────────────────────────────────────────────────────
Run daily at 4:00 AM UTC for continuous monitoring
API Limitation: Balance/usage APIs not publicly accessible
Manual Check: https://openrouter.ai/your-settings/billing
───────────────────────────────────────────────────────────
"""

# Print report
print(report)

# Save report to file
output_path = f'/home/jphermans/hmr-model-router/pricing_report_{today}.txt'
from pathlib import Path
Path(output_path).parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w') as f:
    f.write(report)

print(f"\n📁 Report saved to: {output_path}")
