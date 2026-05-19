# 🐍 Quick Copy-Paste Integration

## 1-Liner for Every Response

Just add **ONE LINE** to every place your bot sends a response:

```python
response = append_cost_to_telegram_response(response)
```

---

## Complete Bot Example

Replace these 2 lines:

```python
# BEFORE (your current code):
await update.message.reply_text(response)

# AFTER (with cost tracking):
from telegram_cost_tracker import append_cost_to_telegram_response
response = append_cost_to_telegram_response(response)
await update.message.reply_text(response)
```

---

## Minimal Working Example

```python
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import sys
from pathlib import Path

# ✅ Add this
sys.path.insert(0, str(Path.home() / ".hermes" / "scripts"))
from telegram_cost_tracker import append_cost_to_telegram_response

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get your response
    response = "Hello! How can I help?"  # Replace with your logic
    
    # ✅ Add cost tracking
    response = append_cost_to_telegram_response(response)
    
    # Send to Telegram
    await update.message.reply_text(response)

# Your existing bot setup...
```

---

## What You Get

✅ Every response shows cost in **EUR (€)**  
✅ 7-day spending summary  
✅ Model identification  
✅ USD equivalent shown  
✅ Automatic logging  

**Cost**: ~0.04 cents per query (€0.000449)

---

## Troubleshooting

### Import Error?
```bash
# Verify file exists
ls -la ~/.hermes/scripts/telegram_cost_tracker.py
```

### No costs showing?
- Check `~/.hermes/usage_log.json` has entries
- Verify you're calling `append_cost_to_telegram_response()`

### Wrong model?
- Model auto-detected from recent log
- Or provide explicitly: `append_cost_to_telegram_response(response, "your-model")`
