"""
Intelligent routing logic for Ollama Gateway
Routes prompts to the best local model based on content analysis
"""

import json
from typing import Dict, Optional


class IntelligentRouter:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path) as f:
            self.config = json.load(f)

        self.models = self.config["models"]
        self.default_model = self.config["default_model"]

    def route(self, prompt: str, user_model: Optional[str] = None) -> tuple[str, str]:
        """
        Routes a prompt to the best model

        Returns:
            tuple[str, str]: (model_name, reason)
        """
        # User explicitly specified a model
        if user_model and user_model in self.models:
            return user_model, "User preference"

        prompt_lower = prompt.lower()

        # Score each model based on tag matches
        scores = {}
        for model_name, model_info in self.models.items():
            score = 0
            matched_tags = []

            for tag in model_info["tags"]:
                if tag.lower() in prompt_lower:
                    score += 10
                    matched_tags.append(tag)

            # Bonus for high priority models
            score += 4 - model_info["priority"]

            if score > 0:
                scores[model_name] = {
                    "score": score,
                    "tags": matched_tags,
                    "role": model_info["role"],
                }

        # Select best model
        if scores:
            best_model = max(scores.items(), key=lambda x: x[1]["score"])
            model_name = best_model[0]
            reason = f"Best for {best_model[1]['role']} (matched: {', '.join(best_model[1]['tags'][:3])})"
            return model_name, reason

        # Long prompts (>4000 chars) -> use reasoning model
        if len(prompt) > 4000:
            reasoning_models = [
                m for m, info in self.models.items() if info["role"] in ["reasoning", "creative"]
            ]
            if reasoning_models:
                return reasoning_models[0], "Long prompt - reasoning required"

        # Default
        return self.default_model, "Default general model"

    def get_available_models(self) -> Dict:
        """Returns list of configured models"""
        return {
            "models": [
                {
                    "name": name,
                    "role": info["role"],
                    "priority": info["priority"],
                    "tags": info["tags"],
                }
                for name, info in self.models.items()
            ],
            "default": self.default_model,
        }
