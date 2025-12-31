"""
Multi-Model Orchestration System
Allows one AI to coordinate multiple specialized models for complex tasks
"""

import json
import logging
import re
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class TaskOrchestrator:
    """
    Orchestrates complex tasks across multiple specialized models
    """

    def __init__(self, router, ollama_url: str):
        self.router = router
        self.ollama_url = ollama_url

        # Define orchestrator model (the "brain")
        self.orchestrator_model = "qwen2.5:latest"  # Good at reasoning and planning

    async def is_complex_task(self, prompt: str) -> bool:
        """
        Determine if a task is complex enough to require orchestration
        """
        complex_indicators = [
            r"compare.*and",
            r"analyze.*from.*perspectives?",
            r"both.*and",
            r"first.*then",
            r"step.*by.*step",
            r"explain.*and.*implement",
            r"research.*and.*summarize",
            r"multiple",
            r"several",
            r"various",
        ]

        prompt_lower = prompt.lower()
        return any(re.search(pattern, prompt_lower) for pattern in complex_indicators)

    async def decompose_task(self, prompt: str, http_client) -> List[Dict[str, str]]:
        """
        Use orchestrator AI to break down complex task into subtasks
        """
        decomposition_prompt = f"""You are a task orchestration AI. Break down this complex request into 2-4 specific subtasks that can be handled by specialized models.

Available specialists:
- qwen2.5-coder:7b: Coding, debugging, algorithms
- mistral: Chess strategy, game analysis
- qwen2.5: Translation, multilingual tasks
- gemma2: Creative writing, stories
- mistral: General knowledge, explanations

User request: {prompt}

Respond with ONLY a JSON array of subtasks:
[
  {{"task": "brief description", "specialist": "model-name", "context": "what info is needed"}},
  ...
]"""

        payload = {
            "model": self.orchestrator_model,
            "messages": [{"role": "user", "content": decomposition_prompt}],
            "stream": False,
            "options": {"temperature": 0.3}  # Low temp for consistent planning
        }

        try:
            response = await http_client.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=30.0
            )
            result = response.json()
            content = result.get("message", {}).get("content", "[]")

            # Extract JSON from response (might have markdown code blocks)
            json_match = re.search(r'\[[\s\S]*\]', content)
            if json_match:
                subtasks = json.loads(json_match.group())
                logger.info(f"Orchestrator created {len(subtasks)} subtasks")
                return subtasks
            else:
                logger.warning("Failed to parse orchestration plan")
                return []

        except Exception as e:
            logger.error(f"Task decomposition failed: {e}")
            return []

    async def execute_subtask(
        self,
        subtask: Dict[str, str],
        http_client,
        context: str = ""
    ) -> str:
        """
        Execute a single subtask with the specified model
        """
        model = subtask.get("specialist", "mistral:latest")
        task_desc = subtask.get("task", "")

        # Build prompt with context from previous tasks
        full_prompt = task_desc
        if context:
            full_prompt = f"Context from previous analysis:\n{context}\n\nYour task:\n{task_desc}"

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": full_prompt}],
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 1024}
        }

        try:
            logger.info(f"Executing subtask with {model}: {task_desc[:50]}...")
            response = await http_client.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=60.0
            )
            result = response.json()
            return result.get("message", {}).get("content", "No response")

        except Exception as e:
            logger.error(f"Subtask execution failed: {e}")
            return f"Error executing subtask: {str(e)}"

    async def synthesize_results(
        self,
        original_prompt: str,
        subtask_results: List[Tuple[str, str]],
        http_client
    ) -> str:
        """
        Use orchestrator to combine results from all subtasks
        """
        results_text = "\n\n".join([
            f"**{task}**\n{result}"
            for task, result in subtask_results
        ])

        synthesis_prompt = f"""You are synthesizing results from multiple specialized AIs.

Original user request:
{original_prompt}

Results from specialists:
{results_text}

Provide a comprehensive, well-structured answer that combines these insights naturally.
Format with markdown for clarity."""

        payload = {
            "model": self.orchestrator_model,
            "messages": [{"role": "user", "content": synthesis_prompt}],
            "stream": False,
            "options": {"temperature": 0.5, "num_predict": 2048}
        }

        try:
            response = await http_client.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=60.0
            )
            result = response.json()
            final_answer = result.get("message", {}).get("content", "")

            # Add metadata footer
            specialists_used = [task for task, _ in subtask_results]
            footer = f"\n\n---\n*🤖 Multi-model orchestration | Subtasks: {len(specialists_used)}*"

            return final_answer + footer

        except Exception as e:
            logger.error(f"Result synthesis failed: {e}")
            # Fallback: just concatenate results
            return results_text + f"\n\n*Error in synthesis: {str(e)}*"

    async def orchestrate(self, prompt: str, http_client) -> Dict[str, Any]:
        """
        Main orchestration flow
        Returns: {
            "answer": final synthesized answer,
            "subtasks": list of subtask descriptions,
            "models_used": list of models involved
        }
        """
        logger.info(f"Starting orchestration for: {prompt[:100]}...")

        # Step 1: Decompose task
        subtasks = await self.decompose_task(prompt, http_client)

        if not subtasks:
            logger.info("No subtasks created, falling back to single model")
            return None

        # Step 2: Execute subtasks sequentially (could be parallel in future)
        results = []
        accumulated_context = ""

        for subtask in subtasks:
            result = await self.execute_subtask(subtask, http_client, accumulated_context)
            task_desc = subtask.get("task", "Subtask")
            results.append((task_desc, result))
            accumulated_context += f"\n{task_desc}: {result[:200]}..."  # Brief context

        # Step 3: Synthesize final answer
        final_answer = await self.synthesize_results(prompt, results, http_client)

        models_used = [subtask.get("specialist", "unknown") for subtask in subtasks]
        models_used.append(self.orchestrator_model)  # Add orchestrator itself

        return {
            "answer": final_answer,
            "subtasks": [s.get("task") for s in subtasks],
            "models_used": list(set(models_used)),  # Unique models
            "orchestration_steps": len(subtasks)
        }
