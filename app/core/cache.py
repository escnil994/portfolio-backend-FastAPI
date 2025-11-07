# app/core/cache.py

from typing import Optional, Any
import json
from datetime import timedelta


class CacheService:
    def __init__(self):
        self._cache = {}
        self._enabled = False
    
    def enable(self):
        self._enabled = True
    
    def disable(self):
        self._enabled = False
    
    async def get(self, key: str) -> Optional[Any]:
        if not self._enabled:
            return None
        return self._cache.get(key)
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[timedelta] = None
    ) -> None:
        if not self._enabled:
            return
        self._cache[key] = value
    
    async def delete(self, key: str) -> None:
        if not self._enabled:
            return
        self._cache.pop(key, None)
    
    async def clear(self) -> None:
        self._cache.clear()
    
    async def exists(self, key: str) -> bool:
        if not self._enabled:
            return False
        return key in self._cache


cache_service = CacheService()