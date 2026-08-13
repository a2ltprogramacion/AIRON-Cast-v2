#!/usr/bin/env python3
"""
API Router — OpenCode ⊕ AIRON-Cast Fusion
Fallback chain de modelos gratuitos + caché Engram.
"""
import json
import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

# Fallback chain priorizado (gratuito)
FALLBACK_CHAIN = [
    {"provider": "nvidia", "model": "nemotron-3-ultra", "api_base": "https://integrate.api.nvidia.com/v1"},
    {"provider": "openrouter", "model": "deepseek/deepseek-chat-v3-0324:free", "api_base": "https://openrouter.ai/api/v1"},
    {"provider": "openrouter", "model": "qwen/qwen3-235b-a22b:free", "api_base": "https://openrouter.ai/api/v1"},
    {"provider": "openrouter", "model": "moonshotai/kimi-k2:free", "api_base": "https://openrouter.ai/api/v1"},
    {"provider": "openrouter", "model": "minimax/minimax-m1:free", "api_base": "https://openrouter.ai/api/v1"},
]

class APIRouter:
    def __init__(self, cache_backend=None):
        self.cache_backend = cache_backend  # Engram memory manager
        self.current_index = 0
        self.call_counts = {i: 0 for i in range(len(FALLBACK_CHAIN))}
    
    def get_next_model(self) -> Dict:
        """Obtiene siguiente modelo en la cadena de fallback."""
        if self.current_index >= len(FALLBACK_CHAIN):
            raise RuntimeError("Todos los modelos de fallback agotados")
        
        model = FALLBACK_CHAIN[self.current_index]
        self.call_counts[self.current_index] += 1
        return model
    
    def fallback(self, error: Exception = None) -> Dict:
        """Avanza al siguiente modelo en la cadena."""
        print(f"FALLBACK: Modelo {self.current_index} falló ({error}), cambiando...", file=__import__('sys').stderr)
        self.current_index += 1
        if self.current_index >= len(FALLBACK_CHAIN):
            raise RuntimeError("Sin modelos disponibles")
        return self.get_next_model()
    
    def cache_key(self, messages: List[Dict], model: str, params: Dict) -> str:
        """Genera clave de caché determinística."""
        content = json.dumps({
            "messages": messages,
            "model": model,
            "params": {k: v for k, v in params.items() if k not in ["stream", "stream_options"]}
        }, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get_cached(self, key: str) -> Optional[Dict]:
        """Obtiene respuesta cacheada."""
        if not self.cache_backend:
            return None
        # TODO: Implementar via Engram response_cache table
        return None
    
    def set_cached(self, key: str, response: Dict) -> None:
        """Guarda respuesta en caché."""
        if not self.cache_backend:
            return
        # TODO: Implementar via Engram response_cache table
        pass
    
    def reset_chain(self):
        """Reinicia al primer modelo."""
        self.current_index = 0


# Instancia global
_router = APIRouter()

def get_router() -> APIRouter:
    return _router


if __name__ == "__main__":
    router = APIRouter()
    for i, m in enumerate(FALLBACK_CHAIN):
        print(f"{i}: {m['provider']}/{m['model']}")