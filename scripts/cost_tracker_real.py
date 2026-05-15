#!/usr/bin/env python3
"""
OpenRouter Model Router - Cost Tracking Tool
Tracks actual model usage and costs from OpenRouter API.
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import requests

# Configuration
HOME_DIR = Path.home()
HERMES_DIR = HOME_DIR / ".hermes"
USAGE_LOG = HERMES_DIR / "usage_log.json"
PRICING_CACHE = HERMES_DIR / "pricing_cache.json"
CACHE_EXPIRY_HOURS = 24

# OpenRouter API endpoints
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
# Usage endpoint requires auth: https://openrouter.ai/api/v1/dashboard/usage


class OpenRouterCostTracker:
    """Track model usage and costs from OpenRouter."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if api_key else {}
    
    def fetch_pricing(self, force_refresh: bool = False) -> Dict[str, Dict[str, float]]:
        """Fetch pricing from OpenRouter API for all models."""
        
        # Check cache first
        if not force_refresh and PRICING_CACHE.exists():
            with open(PRICING_CACHE, 'r') as f:
                cache = json.load(f)
            
            cache_time = datetime.fromisoformat(cache["timestamp"].replace("Z", ""))
            if datetime.utcnow() - cache_time < timedelta(hours=CACHE_EXPIRY_HOURS):
                return cache["pricing"]
        
        print("Fetching pricing from OpenRouter API...")
        
        try:
            response = requests.get(OPENROUTER_MODELS_URL, headers={"User-Agent": "OpenRouter-CostTracker/1.0"})
            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code}")
            
            models = response.json()
            pricing = {}
            
            for model in models:
                model_id = model["id"]
                model_pricing = model.get("pricing", {})
                
                # Skip router models (negative pricing)
                prompt_price = model_pricing.get("prompt", 0)
                completion_price = model_pricing.get("completion", 0)
                
                if prompt_price < 0 or completion_price < 0:
                    continue
                
                # Store per-1M pricing
                pricing[model_id] = {
                    "prompt_per_m": float(prompt_price) * 1_000_000,
                    "completion_per_m": float(completion_price) * 1_000_000
                }
            
            # Cache the result
            cache_data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "pricing": pricing
            }
            with open(PRICING_CACHE, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            return pricing
            
        except Exception as e:
            print(f"Failed to fetch pricing: {e}")
            return {}
    
    def get_model_pricing(self, model_id: str, pricing_cache: Dict) -> Optional[Dict]:
        """Get pricing for a specific model."""
        if model_id in pricing_cache:
            return pricing_cache[model_id]
        
        # Search in cached models for similar names
        for cached_id, data in pricing_cache.items():
            if model_id.replace(":", "-") in cached_id or cached_id.replace(":", "-") in model_id:
                pricing_cache[model_id] = data
                return data
        
        return None
    
    def calculate_cost(self, tokens_prompt: int, tokens_completion: int, model_id: str, pricing_cache: Dict) -> float:
        """Calculate cost for given token counts."""
        pricing = self.get_model_pricing(model_id, pricing_cache)
        
        if not pricing:
            # Use default Flash pricing as fallback
            return (tokens_prompt + tokens_completion) * 0.0000002  # ~$0.20 per 1M tokens
        
        cost = (tokens_prompt * pricing["prompt_per_m"] + 
                tokens_completion * pricing["completion_per_m"]) / 1_000_000
        
        return round(cost, 6)
    
    def fetch_usage_stats(self, api_key: str) -> List[Dict]:
        """Fetch usage statistics from OpenRouter Dashboard API."""
        
        # Attempt to fetch usage (this endpoint may vary)
        try:
            # Try different possible endpoints
            endpoints = [
                "https://openrouter.ai/api/v1/dashboard/usage",
                "https://openrouter.ai/api/dashboard/usage",
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, headers={"Authorization": f"Bearer {api_key}"})
                    if response.status_code == 200:
                        print(f"Fetched usage from {endpoint}")
                        return response.json()
                except:
                    continue
            
            print("Usage endpoint not accessible with current API key")
            return []
            
        except Exception as e:
            print(f"Failed to fetch usage: {e}")
            return []
    
    def log_interaction(self, model: str, tokens_prompt: int, tokens_completion: int) -> Dict:
        """Log a model interaction."""
        
        # Load pricing cache
        pricing_cache = {}
        if PRICING_CACHE.exists():
            with open(PRICING_CACHE, 'r') as f:
                cache = json.load(f)
                pricing_cache = cache.get("pricing", {})
        
        # Calculate cost
        cost = self.calculate_cost(tokens_prompt, tokens_completion, model, pricing_cache)
        
        # Create log entry
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "model": model,
            "tokens_prompt": tokens_prompt,
            "tokens_completion": tokens_completion,
            "total_tokens": tokens_prompt + tokens_completion,
            "cost_usd": cost
        }
        
        # Append to usage log
        if USAGE_LOG.exists():
            with open(USAGE_LOG, 'r') as f:
                try:
                    log_data = json.load(f)
                except:
                    log_data = []
        else:
            log_data = []
        
        log_data.append(entry)
        
        with open(USAGE_LOG, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        return entry
    
    def get_7day_stats(self) -> Dict[str, Any]:
        """Get 7-day usage statistics."""
        
        if not USAGE_LOG.exists():
            return {"count": 0, "total_cost": 0.0, "total_tokens": 0, "models": []}
        
        cutoff = datetime.utcnow() - timedelta(days=7)
        
        with open(USAGE_LOG, 'r') as f:
            try:
                log_data = json.load(f)
            except:
                return {"count": 0, "total_cost": 0.0, "total_tokens": 0, "models": []}
        
        filtered = []
        for entry in log_data:
            try:
                entry_time = datetime.fromisoformat(entry["timestamp"].replace("Z", ""))
                if entry_time > cutoff:
                    filtered.append(entry)
            except:
                continue
        
        total_cost = sum(e["cost_usd"] for e in filtered)
        total_tokens = sum(e["total_tokens"] for e in filtered)
        models = list(set(e["model"] for e in filtered))
        
        return {
            "count": len(filtered),
            "total_cost": round(total_cost, 6),
            "total_tokens": total_tokens,
            "models": models
        }


def main():
    """Example usage."""
    tracker = OpenRouterCostTracker()
    
    # Fetch pricing
    pricing = tracker.fetch_pricing()
    print(f"Fetched pricing for {len(pricing)} models")
    
    # Example: log a test interaction
    # (You would get actual token counts from OpenRouter response)
    # entry = tracker.log_interaction("qwen/qwen3.5-flash-02-23", 500, 300)
    # print(f"Logged: {entry}")
    
    # Get stats
    stats = tracker.get_7day_stats()
    print(f"7-day stats: {stats}")


if __name__ == "__main__":
    main()
