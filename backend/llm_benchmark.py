import os
import time
import logging
import asyncio
from typing import Dict, Any, List
import json
from datetime import datetime
import ollama
import openai
from .config import settings

logger = logging.getLogger(__name__)

class LLMBenchmark:
    def __init__(self):
        self.benchmark_results = {}
        self.optimal_config = {}
        self.test_prompts = [
            "Explain why a patient with CKD stage 4 should avoid NSAIDs.",
            "What are the key considerations for managing diabetes in elderly patients?",
            "Explain the risks of QT prolongation with certain medications."
        ]

    async def run_benchmarks(self) -> Dict[str, Any]:
        """Run benchmarks for all available LLM models"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "models": {}
        }

        # Test OpenAI if available
        if settings.OPENAI_API_KEY:
            try:
                openai_results = await self._benchmark_openai()
                results["models"]["openai"] = openai_results
            except Exception as e:
                logger.error(f"OpenAI benchmark failed: {str(e)}")

        # Test Ollama models
        try:
            ollama_results = await self._benchmark_ollama()
            results["models"]["ollama"] = ollama_results
        except Exception as e:
            logger.error(f"Ollama benchmark failed: {str(e)}")

        # Determine optimal configuration
        self.optimal_config = self._determine_optimal_config(results)
        
        # Save results
        self._save_benchmark_results(results)
        
        return results

    async def _benchmark_openai(self) -> Dict[str, Any]:
        """Benchmark OpenAI model performance"""
        results = {
            "model": settings.OPENAI_MODEL,
            "latency": [],
            "success_rate": 0,
            "errors": []
        }

        for prompt in self.test_prompts:
            try:
                start_time = time.time()
                response = await openai.ChatCompletion.acreate(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a clinical decision support system."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=150
                )
                latency = time.time() - start_time
                results["latency"].append(latency)
            except Exception as e:
                results["errors"].append(str(e))

        results["success_rate"] = len(results["latency"]) / len(self.test_prompts)
        results["avg_latency"] = sum(results["latency"]) / len(results["latency"]) if results["latency"] else float('inf')
        
        return results

    async def _benchmark_ollama(self) -> Dict[str, Any]:
        """Benchmark Ollama model performance"""
        results = {
            "model": settings.OLLAMA_MODEL,
            "latency": [],
            "success_rate": 0,
            "errors": []
        }

        for prompt in self.test_prompts:
            try:
                start_time = time.time()
                response = ollama.generate(
                    model=settings.OLLAMA_MODEL,
                    prompt=prompt,
                    system="You are a clinical decision support system.",
                    temperature=0.7,
                    max_tokens=150
                )
                latency = time.time() - start_time
                results["latency"].append(latency)
            except Exception as e:
                results["errors"].append(str(e))

        results["success_rate"] = len(results["latency"]) / len(self.test_prompts)
        results["avg_latency"] = sum(results["latency"]) / len(results["latency"]) if results["latency"] else float('inf')
        
        return results

    def _determine_optimal_config(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the optimal LLM configuration based on benchmark results"""
        optimal = {
            "model": None,
            "avg_latency": float('inf'),
            "success_rate": 0
        }

        for model_type, model_results in results["models"].items():
            if (model_results["success_rate"] > optimal["success_rate"] or
                (model_results["success_rate"] == optimal["success_rate"] and
                 model_results["avg_latency"] < optimal["avg_latency"])):
                optimal = {
                    "model": f"{model_type}:{model_results['model']}",
                    "avg_latency": model_results["avg_latency"],
                    "success_rate": model_results["success_rate"]
                }

        return optimal

    def _save_benchmark_results(self, results: Dict[str, Any]):
        """Save benchmark results to encrypted storage"""
        try:
            # Create benchmark directory if it doesn't exist
            os.makedirs("benchmarks", exist_ok=True)
            
            # Save results with timestamp
            filename = f"benchmarks/llm_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Benchmark results saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save benchmark results: {str(e)}")

    def get_optimal_config(self) -> Dict[str, Any]:
        """Get the optimal LLM configuration"""
        return self.optimal_config 