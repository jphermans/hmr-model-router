# 📱 Telegram Integration Guide

Use your Hermes Model Router with Telegram! Automatically route tasks to the best budget-friendly OpenRouter models through your Telegram bot.

---

## 🚀 Quick Setup

### Step 1: Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts
3. Choose a name (e.g., "My AI Assistant")
4. Choose a username (e.g., "myai_bot")
5. **Save the API token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Example:**
```
/send: /newbot
Name: My AI Assistant Bot
Username: myai_telegram_bot
Token: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

---

### Step 2: Install Hermes Telegram Gateway

```bash
cd /home/jphermans

# Install Telegram gateway for Hermes
hermes gateway install telegram

# Or configure manually
hermes gateway setup telegram
```

**During setup, you'll be prompted for:**
- ✅ Bot token (from BotFather)
- ✅ Allowed chats (optional, leave empty for all chats)
- ✅ Commands and features

---

### Step 3: Configure with Model Router

Create a Telegram command that uses the model router:

**Option A: Add to `~/.bashrc`**
```bash
# Telegram bot wrapper using your router
alias tg-hermes='hermes chat --platform telegram -s model-router'
```

**Option B: Create a custom script**
```bash
nano ~/telegram-hermes-router.sh
```

```bash
#!/bin/bash
# Telegram command to use with Hermes router

# Get the command and use router
TASK="$*"
SCRIPT_DIR="/home/jphermans/hmr-model-router"

# Use the router to get the best model
MODEL=$(cd $SCRIPT_DIR && python3 hermes-model-router "Analyze this: $TASK" | grep "Recommended Model:" | awk '{print $3}')

# Run hermes with that model
hermes chat -q -m "$MODEL" "$TASK"
```

```bash
chmod +x ~/telegram-hermes-router.sh
```

---

### Step 4: Configure Hermes for Telegram

Edit hermes config to enable router skills on Telegram:

```bash
hermes config edit
```

Add to your Telegram platform config:

```yaml
platforms:
  telegram:
    skills:
      - model-router  # Auto-load model router for telegram
    toolsets:
      - cronjob       # For scheduling
      - delegation    # For complex tasks
```

---

## 💬 Available Telegram Commands

### Basic Commands

```
/start         - Start the bot and show help
/help          - List all available commands
/new           - Start a fresh session
/continue      - Resume previous session
/rollback      - Undo last action
/title [name]  - Name the session
```

### Model Router Commands

```
/route [task]  - Show which model would be used (no execution)
/auto [task]   - Use model router and auto-execute
/cheap [task]  - Force budget models only
/premium [task]- Force premium models
```

### Configuration Commands

```
/models        - Show available models and prices
/costs         - Show current token usage and costs
/reset         - Reset session and reload config
```

---

## 🤖 Example Usage

### Send to Bot:
```
What's the capital of France?
```

**Bot responds automatically** with the best budget model (likely `microsoft/phi-3.5` or `qwen/qwen2.5-coder-32b`).

### Use Router Command:
```
/route Build a FastAPI REST API
```

**Output:**
```
=== Model Selection Analysis 🚀 ===
Task: Build a FastAPI REST API
Recommended Model: qwen/qwen2.5-coder-32b-instruct
Cost Tier: coding → very-low
Reason: Matched 2 keywords to coding model category
Confidence: 100%
Command: hermes chat -q -m qwen/qwen2.5-coder-32b-instruct "Build a FastAPI REST API"
```

### Auto-Execute:
```
/auto Write a Python script to backup files
```

**Bot executes immediately** with the optimal budget model!

---

## ⚙️ Advanced Configuration

### Use Cron for Scheduled Telegram Reports

```bash
# Add to crontab
crontab -e

# Daily summary of model usage (9 AM)
0 9 * * * cd /home/jphermans && hermes insights --days 1 | \
  send_message 'telegram' 'Daily AI Report: Check your usage stats'
```

### Create Commands for Specific Tasks

```bash
# Create a file with task-specific commands
cat > ~/telegram-commands.txt << 'EOF'
/coding - Use coding model for development
/writing - Use creative model for writing
/analysis - Use analysis model for data
/simple - Use smallest/cheapest model
EOF
```

### Auto-Reply Messages

Add auto-replies for common tasks:

```yaml
# In ~/.hermes/config.yaml
platforms:
  telegram:
    auto_confirm:
      - "hello"
      - "hi"
      - "help"
      - "What is 2+2?"
      - "What's the weather?"
    routing:
      coding_tasks: "qwen/qwen2.5-coder-32b"
      general: "qwen/qwen2.5-72b"
```

---

## 🎭 Interactive Session Example

**You send:** `Hello bot!`

**Bot replies:**
```
👋 Hello! I'm your budget-friendly AI assistant!

I use optimized models like:
• DeepSeek Chat ($0.27) - Complex reasoning
• Qwen Coder 32B ($0.18) - Programming
• Mistral Nemo ($0.15) - Creative work
• Microsoft Phi 3.5 ($0.02) - Simple queries

Try these commands:
• /route [task] - See model selection
• /models - View all available models
• /help - All commands

What can I help you with today? 🤖
```

**You send:** `/route Create a Python web scraper`

**Bot replies:**
```
=== Model Selection 🚀 ===
Task: Create a Python web scraper
Recommended Model: qwen/qwen2.5-coder-32b-instruct
Cost: $0.18/M tokens (90% cheaper than alternatives!)

Executing...

💻 Sure! Here's a Python web scraper using requests and BeautifulSoup...
```

---

## 🔧 Troubleshooting

### Bot Not Responding
```bash
# Check Telegram status
hermes gateway status telegram

# Restart gateway
hermes gateway restart telegram

# Check logs
tail -n 50 ~/.hermes/logs/gateway.log
```

### Wrong Model Selected
```bash
# See what's selected
hermes-model-router "your task"

# Adjust routing in model_router.py
# Edit the keyword patterns for better matching
```

### Token Errors
```bash
# Verify your OpenRouter API key
echo $OPENROUTER_API_KEY

# Or check config
cat ~/.hermes/.env | grep OPENROUTER
```

### Commands Not Working
```bash
# Check command aliases
alias | grep hermes

# Check skills are loaded
hermes skills list model-router

# Reload config
hermes config reload
```

---

## 🎁 Bonus: Telegram Features

### 1. Voice Messages
Enable voice-to-speech for hands-free use:

```bash
hermes config set stt.enabled true
hermes config set stt.provider groq  # Free tier available
```

### 2. Image Analysis
Send images for analysis (OCR, vision):

```bash
# Just send an image to the bot!
/hermes-vision [image]
```

### 3. File Processing
Send documents for summarization:

```bash
/send: /summary [document]
```

### 4. Multilingual Support
Hermes supports 100+ languages automatically:

```bash
/switch [language]  # e.g., /switch Spanish
```

---

## 📊 Expected Costs

### Example Monthly Usage

| Task Type | Model | Messages/Month | Cost/Month |
|-----------|-------|----------------|------------|
| Simple queries | Microsoft Phi 3.5 | 1000 | **$0.20** |
| Coding help | Qwen Coder 32B | 500 | **$4.50** |
| Complex tasks | DeepSeek Chat | 200 | **$5.40** |
| Writing | Mistral Nemo | 300 | **$4.50** |
| **Total** | | **2000** | **~$14.60/month** |

**Compare to premium models (~$200-500/month):**
```
💰 Savings: 93-97%!
```

---

## 🌟 Pro Tips

### 1. Use `/route` Before Complex Tasks
See the model selection before executing.

### 2. Create Session Presets
For consistent experiences:
```bash
/hermes -s coding-session    # Pre-configured for Python work
/hermes -s general-session   # For chat and learning
```

### 3. Monitor Your Costs
```bash
hermes insights --days 7
```

### 4. Batch Simple Queries
Send multiple simple queries at once for efficiency.

### 5. Use Cron for Automation
Schedule daily reports, backups, or maintenance.

---

## 🔐 Security Notes

### Protect Your Bot
1. **Don't share bot token publicly**
2. **Set allowed chats** (optional but recommended)
3. **Monitor usage** to prevent abuse
4. **Use rate limiting** in your config

### API Key Security
```bash
# Keep your tokens private
chmod 600 ~/.hermes/.env

# Don't commit to GitHub
echo ~/.hermes/.env >> .gitignore
```

---

## 📚 Resources

- **Hermes Docs**: https://hermes-agent.nousresearch.com/docs
- **OpenRouter Models**: https://openrouter.ai/models
- **Model Router Repo**: https://github.com/jphermans/hmr-model-router
- **Telegram BotFather**: @BotFather on Telegram

---

**🎉 Your Telegram AI assistant is configured and ready to save you 60-90% on costs!**
