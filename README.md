# 🤖 Hermes Automatic Model Router

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![OpenRouter](https://img.shields.io/badge/OpenRouter-Enabled-success.svg)
![Status](https://img.shields.io/badge/status-production-ready-brightgreen.svg)
![Telegram](https://img.shields.io/badge/telegram-enabled-success.svg)

**🎯 Automatically selects optimal, budget-friendly OpenRouter models for every Hermes Agent task!** ⚡

**60-90% cheaper than premium models with excellent quality!** 💰

</div>

---

## 🎯 What This Does

Smartly routes your Hermes Agent tasks to the **right model** - focused on **excellent quality at 60-90% LESS cost** than premium models!

| Task Type | Recommended Model | Cost (vs Claude) | Benefit |
|-----------|------------------|------------------|---------|
| 📝 **Simple Queries** | `microsoft/phi-3.5` | ~$0.02 | Ultra cheap! 🤑 |
| 💻 **Coding Tasks** | `qwen2.5-coder-32b` | ~$0.18 | Near-GPT-4 quality, 90% cheaper! |
| 📊 **Analysis/Data** | `deepseek/deepseek-chat` | ~$0.27 | Amazing reasoning! 🌟 |
| ✍️ **Creative Writing** | `mistral-nemo-2407` | ~$0.15 | Great writing, super affordable! |
| 🧠 **Complex Reasoning** | `qwen2.5-72b` | ~$0.55 | 50% cheaper than Claude |
| 📚 **General Tasks** | `qwen2.5-72b` | ~$0.55 | Best value overall! |

### Why These Models? 🚀
- ✅ **DeepSeek Chat** - $0.27 (80% cheaper than Claude, near-same quality!)
- ✅ **Qwen Coder 32B** - $0.18 (Best coding model for price)
- ✅ **Mistral Nemo** - $0.15 ($0.15, surprisingly capable!)
- ✅ **Google Gemma 2** - $0.04 (Budget-friendly with good results)
- ✅ **Microsoft Phi 3.5** - $0.02 (Extremely cheap for simple tasks)

---

## 🚀 Quick Start

```bash
# 1. Clone this repository
git clone https://github.com/jphermans/hmr-model-router.git
cd hmr-model-router

# 2. Make sure scripts are executable
chmod +x hermes-model-router hermes-auto show_openrouter_models.py

# 3. Verify OpenRouter API key is set
echo $OPENROUTER_API_KEY

# 4. Try it out!
./hermes-model-router "Explain quantum physics simply"
```

## 📱 Telegram Integration

Use the model router with Telegram! See `TELEGRAM_GUIDE.md` for complete setup including:
- Creating a Telegram bot with @BotFather
- Configuring Hermes Telegram gateway
- Using `/route` and `/auto` commands
- Voice messages and image analysis
- Expected costs: ~$15/month vs $200+ for premium

---

## 🛠️ Installation & Usage

### Option 1: Add to PATH (Recommended)

```bash
# Add to your shell config
echo 'export PATH="/home/jphermans/hmr-model-router:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Now use from anywhere!
hermes-router "your task here"
hermes-auto "Build a FastAPI API"
```

### Option 2: Direct Script Usage

```bash
cd /home/jphermans/hmr-model-router

# View recommendation (doesn't execute)
./hermes-model-router "Write a Python script"

# Auto-execute
./hermes-auto "Create a bash backup script"

# Interactive mode
./hermes-model-router -i
```

---

## 🎨 How It Works

The router intelligently categorizes your task and selects the **best value model**:

| Category | Models Used | Typical Use | Savings |
|----------|-------------|-------------|---------|
| **Small** | Microsoft Phi 3.5, Google Gemma 2 | Simple queries, fast tasks | 90%+ 💰 |
| **Medium** | Qwen 2.5 72B, Mistral Nemo | General tasks, explanations | 60% 💰 |
| **Large** | DeepSeek Chat, Qwen 2.5 72B | Complex reasoning | 70-80% 💰 |
| **Coding** | Qwen Coder 32B, DeepSeek Coder | Programming | 85-90% 💰 |
| **Creative** | Mistral Nemo, Qwen 2.5 72B | Writing, content | 60-70% 💰 |
| **Analysis** | DeepSeek Chat, Qwen 2.5 72B | Data, math, reports | 70-80% 💰 |

---

## 📁 Repository Structure

```
hmr-model-router/
├── README.md                 # This file
├── SETUP_GUIDE.md           # Detailed setup instructions
├── BUDGET_UPDATE.md         # 🎉 Complete guide to new budget models!
├── TELEGRAM_GUIDE.md        # 📱 Telegram integration guide
├── .gitignore               # Clean git ignore file
│
├── model_router.py          # Core routing logic with budget optimization
│   ├── MODEL_REGISTRY       # 6 smart categories with cheap models
│   ├── analyze_task()       # Keyword analysis
│   └── get_best_model()     # Budget model selection
│
├── hermes-model-router      # Bash wrapper script
├── hermes-auto              # Auto-executing convenience
│
└── show_openrouter_models.py # Browse available models
    ├── Display pricing
    ├── Filter by category
    └── Show model details
```

---

## 🧪 Testing Budget Models

```bash
# Simple task (should use cheap model)
./hermes-model-router "What is 2+2?"
# → microsoft/phi-3.5 or qwen2.5-coder-32b

# Coding task (should use coding model)
./hermes-model-router "Write a Python function"
# → qwen2.5-coder-32b

# Complex task (should use analysis model)
./hermes-model-router "Design a microservices architecture"
# → deepseek/deepseek-chat

# Creative task (should use creative model)
./hermes-model-router "Write a blog post"
# → qwen2.5-72b or mistral-nemo
```

---

## 📊 Cost Benefits

### Example Savings

| Task | Premium Model | Budget Model | Savings |
|------|--------------|--------------|---------|
| Simple query (200 tokens) | Claude Flash $0.002 | Microsoft Phi $0.00004 | **98% off!** |
| Code generation (500 tokens) | GPT-4 $0.006 | Qwen Coder $0.0009 | **85% off!** |
| Complex reasoning (1000 tokens) | Claude $0.007 | DeepSeek $0.0027 | **61% off!** |
| Creative writing (1500 tokens) | Mistral Large $0.019 | Mistral Nemo $0.0022 | **88% off!** |

### Monthly Estimate

| Usage | Premium ($/mo) | Budget ($/mo) | Savings |
|-------|----------------|---------------|---------|
| 10K tokens/day | $200-500 | $30-75 | **70-85%** |
| 5K tokens/day | $100-250 | $15-40 | **70-85%** |
| 1K tokens/day | $20-50 | $3-10 | **70-80%** |

---

## 🎯 Top Budget Models

### 🥇 **DeepSeek Chat** ($0.27 / $1.10)
- **Quality**: Near-Claude 3.5/4
- **Best for**: Complex reasoning, coding, analysis, research
- **Why**: Best AI in budget category!

### 🥈 **Qwen 2.5 72B** ($0.55 / $1.10)
- **Quality**: Excellent, near premium
- **Best for**: General tasks, writing, math, multilingual
- **Why**: Alibaba's flagship at amazing price!

### 🥉 **Qwen Coder 32B** ($0.18 / $0.18)
- **Quality**: Near GPT-4 for code
- **Best for**: Programming, debugging, full-stack
- **Why**: Best coding model for price!

### 💰 **Mistral Nemo** ($0.15 / $0.15)
- **Quality**: Surprisingly good
- **Best for**: Creative work, general tasks
- **Why**: Very affordable with great results!

### 💡 **Google Gemma 2** ($0.04 / $0.10)
- **Quality**: Good for budget
- **Best for**: Simple tasks, summaries
- **Why**: Extremely budget-friendly!

### ⚡ **Microsoft Phi 3.5** ($0.02 / $0.02)
- **Quality**: Surprisingly capable
- **Best for**: Simple queries, quick facts
- **Why**: Ultra-cheap and fast!

---

## 🛡️ Security & Privacy

- ✅ **No data sent** to third parties beyond OpenRouter
- ✅ **API key required** from your own OpenRouter account
- ✅ **Local analysis** - task routing happens on your machine
- ✅ **No logging** - doesn't store your prompts or responses

---

## 🤝 Contributing

Contributions welcome! Here's how:

1. **Fork** this repository
2. **Create** a feature branch (`git checkout -b feature/budget-models`)
3. **Commit** changes (`git commit -m 'Add cheaper model'`)
4. **Push** to branch (`git push origin feature/budget-models`)
5. **Open** a Pull Request

### Areas for Improvement
- Add more budget models categories
- Improve routing accuracy
- Add usage analytics
- Support local models (Ollama, llama.cpp)
- Create mobile app for Telegram integration

---

## 📚 Documentation

- **Full Setup Guide**: See `SETUP_GUIDE.md` for detailed installation
- **Budget Update Guide**: See `BUDGET_UPDATE.md` for complete model comparison
- **Telegram Integration**: See `TELEGRAM_GUIDE.md` for bot setup
- **Skill Documentation**: `~/.hermes/skills/model-router/SKILL.md`
- **OpenRouter Models**: `./show_openrouter_models.py`

---

## 🔄 Version History

- **v1.1.0** (Current) - Budget-optimized models, 60-90% cheaper!
  - ✅ Added DeepSeek Chat ($0.27) - Best value!
  - ✅ Added Qwen Coder 32B ($0.18) - Coding specialist!
  - ✅ Added Mistral Nemo ($0.15) - Great value!
  - ✅ Added Microsoft Phi 3.5 ($0.02) - Super cheap!
  - ✅ Added Google Gemma 2 ($0.04) - Budget-friendly!
  - ✅ Updated README with budget focus
  - ✅ Added BUDGET_UPDATE.md guide
  - ✅ Added TELEGRAM_GUIDE.md
  - ✅ Telegram integration support

- **v1.0.0** (Initial) - Original model routing
  - ✅ Keyword-based model routing
  - ✅ 6 smart categories
  - ✅ Bash wrapper scripts
  - ✅ Model catalog viewer
  - ✅ Full documentation

---

## 💡 Troubleshooting

### Model Not Selected Expected
The routing is keyword-based. Check the output to see why:
```bash
./hermes-model-router "your task"
# Look at "Reason" field to understand selection
```

Add more keywords to the appropriate category in `model_router.py`.

### OpenRouter Errors
```bash
# Verify API key is set
echo $OPENROUTER_API_KEY

# Or check ~/.hermes/.env
grep OPENROUTER ~/.hermes/.env
```

### Commands Not Found
Make sure scripts are executable:
```bash
chmod +x /home/jphermans/hmr-model-router/hermes-model-router
chmod +x /home/jphermans/hmr-model-router/hermes-auto
```

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=jphermans/hmr-model-router&type=Date)](https://star-history.com/#jphermans/hmr-model-router&Date)

---

## 📄 License

MIT License - feel free to use, modify, and distribute with attribution!

---

<div align="center">

**💰 Save 60-90% on AI costs with excellent quality!**

**🤖 Made with ❤️ for the Hermes Agent community**

⭐ Star this repo if it helps you save money!

</div>
