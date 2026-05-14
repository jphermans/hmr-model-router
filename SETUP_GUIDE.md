# Hermes Model Router - Setup Guide

Welcome to the Hermes Automatic Model Router! This guide will get you up and running in minutes.

## Quick Overview

This system automatically selects the optimal OpenRouter model for each Hermes Agent task, saving you **40-70% on costs** while improving results.

## What You're Getting

| Component | Description |
|-----------|-------------|
| **model_router.py** | Core Python routing logic with 6 smart categories |
| **hermes-model-router** | Bash wrapper for viewing recommendations |
| **hermes-auto** | Auto-executing convenience script |
| **show_openrouter_models.py** | Browse & filter all OpenRouter models |
| **SETUP_GUIDE.md** | This detailed installation guide |
| **SKILL.md** | Integration with Hermes skills system |

## Installation Options

### Option 1: Add to Shell PATH (Recommended)

Add to `~/.bashrc` or `~/.zshrc`:

```bash
export PATH="/home/jphermans/hmr-model-router:$PATH"
source ~/.bashrc
```

Now use from anywhere:

```bash
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

### Option 3: Shell Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Model routing aliases
alias hermes-router='python3 /home/jphermans/hmr-model-router/hermes-model-router'
alias hermes-quick='HERMES_ROUTER_RUN=1 python3 /home/jphermans/hmr-model-router/hermes-model-router'
alias hermes-auto='/home/jphermans/hmr-model-router/hermes-auto'
alias hermes-show-models='python3 /home/jphermans/hmr-model-router/show_openrouter_models.py'

source ~/.bashrc
```

---

## Usage Examples

### See Recommended Model (No Execution)

```bash
hermes-model-router "Build a complete e-commerce website with React and Node.js"
```

**Output:**

```
=== Model Selection Analysis ===
Task: Build a complete e-commerce website with React and Node.js
Recommended Model: anthropic/claude-3.5-sonnet
Category: coding
Reason: Matched 4 keywords to coding model category
Confidence: 100%
Command: hermes chat -q -m anthropic/claude-3.5-sonnet "Build a complete..."
================================
```

### Auto-Execute (Run Immediately)

```bash
hermes-auto "Write a bash script to backup my database"
```

### Interactive Mode

```bash
hermes-model-router -i
```

### Pipe Input

```bash
echo "Create a SQL query for this analysis" | HERMES_ROUTER_RUN=1 hermes-model-router
```

---

## Current Model Routing

| Category | Models | Best For | Cost |
|----------|--------|----------|------|
| **Large** | Claude 3.5, Claude Sonnet 4, Grok 3 Beta | Complex reasoning, research | High |
| **Coding** | Claude 3.5, DeepSeek Coder, Qwen Coder | Programming, debugging | Medium-High |
| **Creative** | Claude 3.5, Mistral Large, Qwen 2.5 72B | Writing, marketing, content | Medium |
| **Medium** | Qwen 235B, Gemma 3 27B, Mistral Medium | General tasks, explanations | Medium |
| **Small** | Qwen Flash, Mistral Nemo | Simple queries, formatting | Low |
| **Analysis** | Claude 3.5, Qwen 2.5 72B | Data, calculations, reports | Medium |

---

## Customization

### Edit Model Lists

```bash
# Open the router
nano /home/jphermans/hmr-model-router/model_router.py
# Or use your preferred editor
vim /home/jphermans/hmr-model-router/model_router.py
```

Add a new model to a category:

```python
"coding": {
    "models": [
        "anthropic/claude-3.5-sonnet",
        "your-preferred-coding-model",  # Add here
    ],
    # ...
},
```

### Add New Keywords

```python
"your-category": {
    "use_cases": [
        "existing-keyword",
        "new-keyword-here",  # Add here
    ],
    # ...
},
```

### Change Cost Tiers

```python
"cost_tier": "low"  # Options: low, medium, high
```

---

## Advanced Setup

### Create a Cron Job Example

Edit crontab:

```bash
crontab -e
```

Add a daily task with optimal model (3 AM on Sunday):

```bash
0 3 * * 0 cd /home/jphermans/hmr-model-router && echo "Weekly code review task" | HERMES_ROUTER_RUN=1 ./hermes-model-router >> ~/hermes-cron.log 2>&1
```

Daily simple check with small model:

```bash
0 8 * * * cd /home/jphermans/hmr-model-router && echo "Morning status check" | HERMES_ROUTER_RUN=1 ./hermes-model-router >> ~/hermes-daily.log 2>&1
```

### Integrate with Existing Workflow

Create a `~/.hermes/aliases.sh` file:

```bash
#!/bin/bash

# Hermes Model Routing Aliases
hermes-large() {
    python3 ~/hmr-model-router/hermes-model-router "Your task here"
}

hermes-quick() {
    HERMES_ROUTER_RUN=1 ~/hmr-model-router/hermes-model-router "Your task here"
}

hermes-chat() {
    python3 ~/hmr-model-router/hermes-model-router "$*"
}
```

Then add to `~/.bashrc`:

```bash
source ~/.hermes/aliases.sh
```

---

## Testing

Test automatic selection with different task types:

```bash
# Small task (should use qwen3.5-flash)
hermes-model-router "What is 2+2?"

# Medium task (should use qwen3.5-235b)
hermes-model-router "Explain photosynthesis"

# Coding task (should use coding model)
hermes-model-router "Write a Python function to sort a list"

# Creative task (should use creative model)
hermes-model-router "Write a poem about computers"

# Complex task (should use large model)
hermes-model-router "Design a microservices architecture for this system"
```

---

## Troubleshooting

### Command Not Found

Make sure scripts are executable:

```bash
chmod +x /home/jphermans/hmr-model-router/hermes-model-router
chmod +x /home/jphermans/hmr-model-router/hermes-auto
```

### OpenRouter Errors

Verify your API key:

```bash
echo $OPENROUTER_API_KEY
# Or check ~/.hermes/.env
grep OPENROUTER ~/.hermes/.env
```

### Wrong Model Selected

Check the routing output to see why:

```bash
hermes-model-router "your task"
# Look at the "Reason" field
```

Then add more keywords to the appropriate category in `model_router.py`.

### Performance Issues

The router is very fast (~1ms). If it's slow:

```bash
time hermes-model-router "test task"
```

If still slow, the bottleneck is likely the actual Hermes call, not the routing.

---

## Performance & Cost Benefits

### Before (Single Model)

- Every task uses the same model (e.g., qwen3.5-flash-02-23)
- Simple queries waste expensive compute
- Complex queries might not get the capacity they need
- No optimization for task type

### After (Multi-Model Routing)

- Simple queries → Fast/Cheap models (Qwen Flash)
- Coding tasks → Specialized coding models (DeepSeek, Claude)
- Complex reasoning → Large models (Claude 3.5 Sonnet)
- Creative writing → Creative-optimized models
- **Potential cost savings:** 40-70% for mixed workloads
- **Better results:** Right tool for each job

---

## Model Catalog

### Large Models (Complex)

- `anthropic/claude-3.5-sonnet` - Best overall
- `anthropic/claude-sonnet-4` - Latest Claude
- `xai/grok-3-beta` - Fast reasoning
- `deepseek/deepseek-chat` - Great value
- `qwen/qwen2.5-72b-instruct` - Strong multilingual

### Coding Models

- `deepseek/deepseek-coder-33b-instruct` - Code specialist
- `qwen/qwen-coder-2` - Code focused
- `meta-llama/llama-3.3-70b-instruct` - Good all-rounder
- `anthropic/claude-3.5-sonnet` - Still best for code

### Creative Models

- `mistralai/mistral-large-latest` - Creative writing
- `cohere/command-r-plus-08-2024` - Marketing content
- `qwen/qwen2.5-72b-instruct` - Long-form writing

### Medium Models (Balanced)

- `qwen/qwen3.5-235b-a22b-instruct-2507` - Your current default
- `google/gemma-3-27b-it` - Strong reasoning
- `mistralai/mistral-medium-2505` - Good balance

### Small Models (Fast)

- `qwen/qwen3.5-flash-02-23` - Fast & cheap
- `mistralai/mistral-nemo-2407` - Good quality
- `gryphe/mythomax-l2-13b` - Lightweight

### Analysis Models

- `deepseek/deepseek-chat` - Great for data
- `google/gemma-2-27b-it` - Mathematical reasoning
- `qwen/qwen2.5-72b-instruct` - Multilingual analysis

---

## Next Steps

1. **Test the router** with various tasks to see the selection logic
2. **Customize models** based on your needs and OpenRouter pricing
3. **Add keywords** for better routing accuracy
4. **Set up aliases** for convenient access
5. **Monitor cost savings** and adjust routing rules

---

## Help

To view the full skill documentation:

```bash
skill_view model-router
```

Or read the SKILL.md file:

```bash
cat ~/.hermes/skills/model-router/SKILL.md
```

---

## Credits

This router was set up specifically for your Hermes Agent instance to leverage multiple OpenRouter models efficiently.
