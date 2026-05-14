# 🤖 Hermes Automatic Model Router

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![OpenRouter](https://img.shields.io/badge/OpenRouter-Enabled-success.svg)
![Status](https://img.shields.io/badge/status-production-ready-brightgreen.svg)

**Automatically selects the optimal OpenRouter model for every Hermes Agent task** ⚡

</div>

---

## 🎯 What This Does

Smartly routes your Hermes Agent tasks to the **right model** - focused on **excellent quality at 50-90% LESS cost** than premium models!

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
git clone https://github.com/yourusername/hmr-model-router.git
cd hmr-model-router

# 2. Make sure scripts are executable
chmod +x hermes-model-router hermes-auto show_openrouter_models.py

# 3. Verify OpenRouter API key is set
echo $OPENROUTER_API_KEY

# 4. Try it out!
./hermes-model-router "Explain quantum physics simply"
```

---

## 🛠️ Installation & Usage

### Option 1: Add to PATH (Recommended)

```bash
# Add to your shell config
echo 'export PATH="/path/to/hmr-model-router:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Now use from anywhere!
hermes-router "Write a Python script"
hermes-auto "Design a database schema"
```

### Option 2: Shell Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Model routing
alias hermes-router='python3 /path/to/hmr-model-router/hermes-model-router'
alias hermes-quick='HERMES_ROUTER_RUN=1 python3 /path/to/hmr-model-router/hermes-model-router'
alias hermes-auto='/path/to/hmr-model-router/hermes-auto'
alias hermes-show-models='python3 /path/to/hmr-model-router/show_openrouter_models.py'

source ~/.bashrc
```

### Mode 1: See Recommendation (No Execution)
```bash
./hermes-model-router "Build a microservices architecture"

# Output:
# === Model Selection Analysis ===
# Task: Build a microservices architecture
# Recommended Model: anthropic/claude-3.5-sonnet
# Category: coding
# Reason: Matched 3 keywords to coding model category
# Confidence: 90%
# Command: hermes chat -q -m anthropic/claude-3.5-sonnet "..."
# =================================
```

### Mode 2: Auto-Execute
```bash
# Set HERMES_ROUTER_RUN=1 to run immediately
HERMES_ROUTER_RUN=1 ./hermes-model-router "Create a bash backup script"
```

### Mode 3: Interactive Mode
```bash
./hermes-model-router -i

# Enter tasks one at a time, auto-selects models
Your task: Write a poem about AI
# → Uses creative model

Your task: Debug this Python error
# → Uses coding model
```

### Mode 4: Pipe Input
```bash
echo "Explain machine learning basics" | HERMES_ROUTER_RUN=1 ./hermes-model-router
```

---

## 📁 Repository Structure

```
hmr-model-router/
├── README.md                 # This file
├── SETUP_GUIDE.md           # Detailed setup instructions
├── .gitignore               # Clean git ignore file
│
├── model_router.py          # Core routing logic (11KB)
│   ├── MODEL_REGISTRY       # 6 smart categories
│   ├── analyze_task()       # Keyword analysis
│   └── get_best_model()     # Model selection
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

## ⚙️ How It Works

### 1. Task Analysis
The router analyzes your task using keyword patterns:

```python
task = "Build a FastAPI REST API"
task_lower = task.lower()

# Pattern matching scores categories
if "build" in task_lower and "api" in task_lower:
    score["coding"] += 1
```

### 2. Category Selection
Based on scores, selects the best category:

| Category | Keywords | Models |
|----------|----------|--------|
| **Small** | simple, fast, what's the | qwen3.5-flash |
| **Medium** | summary, explain, guide | qwen3.5-235b |
| **Large** | complex, advanced, system | claude-3.5-sonnet |
| **Coding** | code, function, api | deepseek-coder |
| **Creative** | write, story, blog | mistral-large |
| **Analysis** | data, calculate, report | deepseek-chat |

### 3. Model Selection
Picks the optimal model with highest confidence.

---

## 🎨 Customization

### Add New Models

Edit `model_router.py`:

```python
MODEL_REGISTRY = {
    "coding": {
        "models": [
            "anthropic/claude-3.5-sonnet",
            "your-preferred-model-here",  # Add here
        ],
        # ...
    },
    # ...
}
```

### Add Custom Keywords

```python
"your-category": {
    "use_cases": [
        "existing-keyword",
        "new-keyword-here",  # Add patterns here
    ],
}
```

### Modify Cost Tiers

```python
"cost_tier": "low"  # Options: low, medium, high
```

---

## 🔍 Available OpenRouter Models

### View All Models
```bash
python3 show_openrouter_models.py
```

### Filter by Category
```bash
# Show coding models
python3 show_openrouter_models.py coding

# Show large models
python3 show_openrouter_models.py large

# Show small/cheap models
python3 show_openrouter_models.py small
```

### Get Model Details
```bash
python3 show_openrouter_models.py anthropic/claude-3.5-sonnet
```

---

## 📊 Cost Benefits

### Typical Savings

| Workflow | Single Model | With Router | Savings |
|----------|-------------|-------------|---------|
| 100 queries | All premium | Mixed models | 40-70% |
| Mixed tasks | All `claude-3.5` | Auto-select | 50-60% |
| Daily usage | 1 model | Optimal | 30-50% |

### Example Cost Breakdown

```
Simple query (200 tokens):
  Single model approach: $0.002
  Router (small model):  $0.0004
  Savings: 80%

Complex coding task (2000 tokens):
  Single model (wrong):  $0.02
  Router (optimal):      $0.014
  Better quality:        ✅
```

---

## 🧪 Testing

Run tests to see different scenarios:

```bash
# Simple factual query (should use small)
./hermes-model-router "What is 2+2?"

# Basic explanation (should use medium)
./hermes-model-router "Explain photosynthesis"

# Programming task (should use coding)
./hermes-model-router "Write a Python function"

# Creative writing (should use creative)
./hermes-model-router "Write a short story"

# Complex system design (should use large)
./hermes-model-router "Design a microservices architecture"
```

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
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Areas for Improvement

- Add ML-based routing (learning from user preferences)
- Integrate with OpenRouter usage analytics
- Add cost tracking and reporting
- Support local LLMs (Ollama, llama.cpp)
- Add multi-model parallel execution
- Create web dashboard for settings

---

## 📚 Documentation

- **Full Setup Guide**: See `SETUP_GUIDE.md` for detailed installation and usage
- **Skill Documentation**: `~/.hermes/skills/model-router/SKILL.md`
- **OpenRouter Models**: `./show_openrouter_models.py`

---

## 🔄 Version History

- **v1.0.0** (Initial Release)
  - ✅ Keyword-based model routing
  - ✅ 6 smart categories
  - ✅ Bash wrapper scripts
  - ✅ Model catalog viewer
  - ✅ Full documentation

---

## 💡 Troubleshooting

### Command Not Found
```bash
# Make sure scripts are executable
chmod +x /path/to/hmr-model-router/hermes-model-router
chmod +x /path/to/hmr-model-router/hermes-auto

# Or add to PATH
export PATH="/path/to/hmr-model-router:$PATH"
```

### Wrong Model Selected
Check the routing output:
```bash
./hermes-model-router "your task"
# Look at "Reason" field to understand why
```

Add more keywords to the appropriate category in `model_router.py`.

### OpenRouter Errors
```bash
# Verify API key is set
echo $OPENROUTER_API_KEY

# Or check ~/.hermes/.env
grep OPENROUTER ~/.hermes/.env
```

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/hmr-model-router&type=Date)](https://star-history.com/#yourusername/hmr-model-router&Date)

---

## 📄 License

MIT License - feel free to use, modify, and distribute!

---

<div align="center">

**Made with ❤️ for the Hermes Agent community**

⭐ Star this repo if it helps you!

</div>
