# 📊 Cost Tracking & Monitoring Guide

**Version:** 1.2.0  
**Last Updated:** 2026-05-15  
**Status:** ✅ Active for all responses

---

## Overview

Hermes Agent now includes **automatic cost tracking** for every response, both in terminal and Telegram. Monitor your AI spending in real-time with detailed cost breakdowns and 7-day usage statistics.

---

## What You Get

### After Every Response

```
📊 **Model Info & Costs**
   Model: qwen/qwen3.5-flash-02-23
   Tokens: 800 input / 1,200 output (2,000 total)
   Rate:   $0.18 per 1M tokens (input) / $0.28 per 1M tokens (output)
   Cost:   $0.000480 USD (estimated)

📈 **7-Day Summary**
   Total responses:      2
   Total cost:           $0.000940 USD
   Total tokens:         4,000 tokens
   Models used:          qwen/qwen3.5-flash-02-23

📝 **Recent Activity (last 7):**
   2026-05-15 | qwen3.5-flash-02-23 | $0.000480 | 2,000 tokens
```

---

## How It Works

### 1. Automatic Logging
Every response is automatically logged to `~/.hermes/usage_log.json` with:
- Timestamp
- Model name
- Estimated token counts (input/output/total)
- Calculated cost in USD

### 2. Real-Time Pricing
- Pricing fetched from [OpenRouter API](https://openrouter.ai/models)
- Cached for 24 hours to minimize API calls
- Supports 332+ models with valid pricing

### 3. Cost Calculation
Based on OpenRouter's published rates:
```python
cost = (prompt_tokens × prompt_price + completion_tokens × completion_price) / 1,000,000
```

**Note:** Since Hermes Agent CLI doesn't expose exact token counts, estimates are used (~40% input / ~60% output for typical conversations).

---

## Files Created

### `~/.hermes/scripts/response_cost_tracker.py`
Main cost tracking script:
- Calculates costs for each response
- Logs to usage_file.json
- Displays formatted summary

### `~/.hermes/usage_log.json`
Usage history with entries like:
```json
{
  "timestamp": "2026-05-15T04:07:23Z",
  "model": "qwen/qwen3.5-flash-02-23",
  "tokens_prompt": 800,
  "tokens_completion": 1200,
  "total_tokens": 2000,
  "cost_usd": 0.000480
}
```

### `~/.hermes/pricing_cache.json`
Cached pricing data:
- Updated every 24 hours
- Contains 332+ models
- Avoids repeated API calls

---

## Monitoring Commands

### View Usage Log
```bash
cat ~/.hermes/usage_log.json
```

### Check 7-Day Summary
```bash
python ~/.hermes/scripts/response_cost_tracker.py
```

### Force Pricing Refresh
```bash
rm ~/.hermes/pricing_cache.json
# Next response will fetch fresh pricing
```

### Export to CSV
```bash
cat ~/.hermes/usage_log.json | jq -r '.[] | [.timestamp, .model, .cost_usd] | @csv' > usage.csv
```

### View Model Pricing
```bash
cat ~/.hermes/pricing_cache.json | jq '.pricing | to_entries | .[0:5]'
```

### Reset Usage Log
```bash
rm ~/.hermes/usage_log.json
# Starting fresh with zero usage
```

---

## Cost Optimization Tips

### 1. Use Budget Models for 60-80% of Queries
Simple queries don't need premium models:
- ✅ **Simple questions** → `microsoft/phi-3.5` ($0.02/1M)
- ✅ **General chat** → `mistralai/mistral-nemo` ($0.02/1M)
- ✅ **Quick facts** → `google/gemma-2-9b-it` ($0.04/1M)

### 2. Reserve Premium Models for Complex Tasks
- 🧠 **Complex reasoning** → `qwen/qwen-2.5-72b` ($0.55/1M)
- 📊 **Analysis/research** → `deepseek/deepseek-chat` ($0.27/1M)
- 💻 **Advanced coding** → `qwen/qwen-coder-2-72b` ($0.18/1M)

### 3. Monitor Weekly Spending
Check `~/.hermes/usage_log.json` every week:
```bash
python -c "
import json
with open('~/.hermes/usage_log.json') as f:
    logs = json.load(f)
    total = sum(e['cost_usd'] for e in logs)
    print(f'Spent: \${total:.4f} this week')
"
```

### 4. Set Budget Alerts
Use this script to track daily spending:
```bash
#!/bin/bash
# ~/.hermes/scripts/budget_alert.sh
DAILY_LIMIT=1.00  # $1/day limit
TODAY=$(date +%Y-%m-%d)

TOTAL=$(jq -r "[.[] | select(.timestamp | startswith(\"$TODAY\")) | .cost_usd] | add" ~/.hermes/usage_log.json)

if (( $(echo "$TOTAL > $DAILY_LIMIT" | bc -l) )); then
    echo "⚠️ Budget alert: Spent \$$TOTAL today (limit: \$$DAILY_LIMIT)"
fi
```

---

## Current Model Pricing

### Budget Models (< $0.10 per 1M tokens)

| Model | Input | Output | Best For | Savings |
|-------|-------|--------|----------|---------|
| `microsoft/phi-3.5` | $0.02 | $0.03 | Simple queries | **98%** |
| `mistralai/mistral-nemo` | $0.02 | $0.03 | General tasks | **96%** |
| `ibm-granite/granite-4.0-h-micro` | $0.02 | $0.11 | Basic reasoning | **94%** |
| `meta-llama/llama-3.1-8b-instruct` | $0.02 | $0.05 | General chat | **95%** |
| `google/gemma-2-9b-it` | $0.04 | $0.08 | Creative work | **92%** |
| `qwen/qwen3.5-flash-02-23` | $0.18 | $0.28 | Current default | **90%** |

### Value Models ($0.10-$1.00 per 1M tokens)

| Model | Input | Output | Best For | Savings |
|-------|-------|--------|----------|---------|
| `deepseek/deepseek-chat` | $0.27 | $1.10 | Analysis | **85%** |
| `qwen/qwen-coder-2-72b` | $0.18 | $0.35 | Advanced coding | **90%** |
| `qwen/qwen-2.5-72b` | $0.55 | $1.10 | Complex reasoning | **80%** |
| `anthropic/claude-3-haiku` | $0.25 | $1.25 | Fast, capable | **75%** |

### Premium Models (>$1.00 per 1M tokens)

| Model | Input | Output | Best For | Notes |
|-------|-------|--------|----------|-------|
| `anthropic/claude-3.5-sonnet` | $3.00 | $15.00 | Highest quality | Baseline |
| `openai/gpt-4o` | $5.00 | $15.00 | Balanced premium | 7.5x more expensive |
| `anthropic/claude-3-opus` | $5.00 | $25.00 | Specialized tasks | 16.7x more expensive |

---

## Getting Exact Token Counts

For precise tracking with actual token counts from OpenRouter responses:

### Option 1: Set API Key
```bash
export OPENROUTER_API_KEY=sk-or-...

# Run detailed tracker with exact counts
python ~/.hermes/scripts/cost_tracker_real.py
```

### Option 2: Use OpenRouter Dashboard
Visit https://openrouter.ai/dashboard/usage to see:
- Exact token counts per model
- Total cost breakdown
- Per-day statistics
- Account balance

### Limitation
The Hermes Agent CLI doesn't expose exact token counts in responses, so estimates are used. The scripts provide the most accurate tracking possible within CLI constraints.

---

## Advanced Usage

### Custom Token Estimation
Modify the default token estimate in the script:
```python
# In response_cost_tracker.py
estimated_tokens = 3000  # Change from 2000
```

### Multi-Model Tracking
Log costs for different models:
```bash
# Test different models and track costs
python -c "
from response_cost_tracker import get_cost_info
models = ['deepseek/deepseek-chat', 'qwen/qwen-2.5-72b']
for model in models:
    print(get_cost_info(model))
"
```

### Automated Weekly Report
Add to cron job:
```bash
# Weekly report every Monday at 9 AM
0 9 * * 1 python ~/.hermes/scripts/response_cost_tracker.py >> ~/weekly_cost_report.log 2>&1
```

### Slack/Discord Integration
```bash
# Send cost summary to Slack
python ~/.hermes/scripts/response_cost_tracker.py | 
  curl -X POST -d @- -H 'Content-Type: text/plain' https://hooks.slack.com/services/...
```

---

## Troubleshooting

### Pricing Not Updating
**Problem:** Costs seem outdated.

**Solution:** Force fresh pricing:
```bash
rm ~/.hermes/pricing_cache.json
```

### Log File Missing
**Problem:** `~/.hermes/usage_log.json` doesn't exist.

**Solution:** Trigger response to create log:
```bash
hermes chat "Check cost tracking"
```

### High Estimated Costs
**Problem:** Costs seem higher than expected.

**Cause:** Token estimate too high.

**Fix:** Adjust estimate in script:
```python
# Lower estimate if responses are shorter
estimated_tokens = 1000  # Instead of 2000
```

### Missing Models
**Problem:** Unknown model pricing.

**Solution:** Add custom pricing mapping:
```python
fallbacks = {
    "your-model-name": {"prompt_per_m": 0.5, "completion_per_m": 1.0}
}
```

---

## Performance Impact

- **Minimal overhead:** ~0.1s per response
- **Cached pricing:** API calls every 24h, not per response
- **Tiny log file:** ~1KB per 100 responses
- **No network delay:** Pricing loaded from cache

---

## Future Enhancements

- [ ] Integrate with OpenRouter Dashboard API for exact token counts
- [ ] Add budget limit alerts via Telegram/Slack
- [ ] Export to Google Sheets for visualization
- [ ] Monthly spending summaries
- [ ] Cost projection based on usage patterns

---

## Credits

- **OpenRouter** - For affordable AI model pricing
- **Hermes Agent** - For the multi-model agent framework
- **Cost Tracker** - Custom implementation for transparent spending

---

## References

- [OpenRouter Models](https://openrouter.ai/models)
- [OpenRouter Pricing](https://openrouter.ai/pricing)
- [OpenRouter Dashboard](https://openrouter.ai/dashboard/usage)
- [Cost Tracker Skill](~/.hermes/skills/devops/cost-tracker/)
- [Model Router Skill](~/.hermes/skills/mlops/multi-llm-routing/)

---

**💰 Track your spending, save money, and optimize model selection!**

For questions or issues, check the [README](README.md) or create an issue on GitHub.
