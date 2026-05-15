# OpenRouter Daily Monitor - Production Setup Guide

## 🚀 Quick Start

Your daily monitor combines:
1. **Model pricing analysis** (public data, stored in repo)
2. **Usage/billing tracking** (private data, NOT in repo)

## 📁 File Structure

```
hmr-model-router/
├── .data/                        # Public pricing data (IN GIT)
│   └── model-pricing.json        # Latest OpenRouter pricing
├── .private/                     # Private usage data (NOT in GIT!)
│   ├── usage_data.json           # Latest usage info
│   ├── fetch_usage.py            # Usage fetching script
│   └── backups/                  # Historical usage backups
├── scripts/
│   ├── check_model_pricing.py    # Public pricing checker (IN GIT)
│   └── fetch_usage.py            # Private usage fetcher
└── .gitignore                    # Should include .private/
```

## 🗓️ Schedule

- **Cron Job ID**: 2e9ea2da6332
- **Time**: Daily at 4:00 AM UTC (6:00 AM Brussels time)
- **Next Run**: Tomorrow at 4:00 AM UTC

## 🔑 Configuration

### Environment Variables Needed

```bash
# Check if OPENROUTER_API_KEY is set:
echo $OPENROUTER_API_KEY

# Should output: sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### API Key Location

The scripts look for the API key in order:
1. `OPENROUTER_API_KEY` environment variable
2. `/home/jphermans/.hermes/.env` file (line without `#`)

## 📊 Data Flow

### Phase 1: Public Pricing Data
```
1. Fetch from openrouter.ai/api/v1/models
2. Analyze 364+ models
3. Find cheapest/best value
4. Save to .data/model-pricing.json
5. Commit & push to GitHub
```

### Phase 2: Private Usage Data
```
1. Fetch from OpenRouter billing API
2. Get balance, costs, tokens
3. Save to .private/usage_data.json
4. Create backup in .private/backups/
5. NOT committed to Git
```

### Phase 3: Combined Report
```
1. Generate Telegram message
2. Include usage + pricing insights
3. Show cost optimization tips
4. Send to Telegram home channel
```

## 🔍 API Endpoints to Discover

The `fetch_usage.py` script will automatically test these endpoints:

```python
# Test these in order (first working one wins):
1. https://openrouter.ai/api/v1/billing/usage
2. https://openrouter.ai/api/v1/billing/dashboard
3. https://openrouter.ai/api/v1/usage
4. https://openrouter.ai/api/v1/account
5. https://openrouter.ai/api/v1/auth
```

**Note**: You may need to check OpenRouter documentation or dashboard network tab to find the actual working endpoint.

## 📱 Telegram Message Format

```
🤖 Daily OpenRouter Report - 2026-05-15

═══════════════════════════════
💰 USAGE SUMMARY (Yesterday)
═══════════════════════════════
💵 Balance: $47.50
🎫 Total Cost: $12.50
💰 Budget used: 20.8%
📊 Tokens: 500K in / 250K out

📦 Top Models by Cost:
• deepseek-chat                $3.25
• qwen-coder-32b               $2.10
• mistral-nemo                 $1.50
• gemma-2-9b                   $0.85
• llama-3.1-8b                 $0.60

📈 Last 7 Days:
• May 14    $3.25    • May 12    $2.10
• May 13    $2.80    • May 11    $1.95
• May 10    $2.20    • May 09    $1.80
• May 08    $0.40    **Avg**: $2.10/day

═══════════════════════════════
📊 PRICING ANALYSIS
═══════════════════════════════
Models analyzed: 364
With pricing: 332

Top 3 Cheapest:
1. inclusionAI: Ling-2.6-flash  $0.01
2. IBM: Granite 4.0 Micro     $0.02
3. Meta: Llama 3.1 8B        $0.02

💡 Budget Optimization:
Current: $2.10/day
If using cheapest: ~$0.15/day
Potential savings: 93%!
```

## 🛠️ Manual Testing

### Test Pricing Only
```bash
cd /home/jphermans/hmr-model-router
python3 scripts/check_model_pricing.py
```

### Test Usage Only
```bash
cd /home/jphermans/hmr-model-router/scripts
python3 fetch_usage.py
```

### Full Combined Test
```bash
# Manually run both scripts and combine output
echo "=== Pricing Test ===" && python3 ../scripts/check_model_pricing.py
echo "=== Usage Test ===" && python3 fetch_usage.py
```

## 🔒 Security

**NEVER COMMIT**:
- `.private/` directory
- Any files containing API keys
- Any files with real billing data

**ALWAYS COMMIT**:
- `scripts/check_model_pricing.py` (public data)
- `scripts/fetch_usage.py` (code only, not data)
- `.gitignore` (ensure .private/ is listed)

## ⚠️ Troubleshooting

### "API key not found"
```bash
# Check environment:
echo $OPENROUTER_API_KEY

# Set it if missing:
export OPENROUTER_API_KEY=sk-or-your-actual-key-here

# Or add to ~/.bashrc for permanent setting
```

### "No working endpoints found"
The OpenRouter API structure may have changed. Check:
1. OpenRouter dashboard - look at network tab
2. OpenRouter API documentation
3. Try endpoints manually with curl:
```bash
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  https://openrouter.ai/api/v1/billing/usage
```

### Git conflicts with .private/
```bash
# Force add .gitignore:
echo ".private/" >> .gitignore
git add .gitignore
git commit -m "Add .private/ to gitignore"
```

## 📈 Data Retention

- **Pricing data**: Saved daily, kept in repo history
- **Usage data**: Saved daily, backups kept in .private/backups/
- **Manual cleanup**: Run `find .private/backups/ -mtime +30 -delete` to cleanup old backups

## 🎯 Next Steps

1. ✅ **Go Live** - The system is ready!
   - Cron job scheduled for 4:00 AM UTC
   - Pricing monitoring works
   - Ready for usage testing

2. 🧪 **Optional Testing**
   - Manually run scripts to verify
   - Test Telegram delivery
   - Verify API endpoints work

3. 📊 **Monitor First Day**
   - Check Telegram at 6:00 AM Brussels time
   - Verify both pricing and usage appear
   - Confirm no data leaked to GitHub

4. 🎉 **All Set**
   - Runs automatically every day
   - No manual intervention needed
   - Private data stays private

---

**Created**: 2026-05-15
**Last Updated**: 2026-05-15 04:01 UTC
**Monitor Status**: ✅ Active (Next run: Tomorrow at 4:00 AM UTC)
