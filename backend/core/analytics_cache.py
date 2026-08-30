from typing import Dict, Any, Tuple, Optional

class AnalyticsCache:
    # Structure: { (session_id, service_name): { cache_key_tuple: cached_value } }
    _cache: Dict[Tuple[Optional[str], str], Dict[Tuple[Any, ...], Any]] = {}

    @classmethod
    def get(cls, service_name: str, cache_key: Tuple[Any, ...], session_id: Optional[str] = None) -> Any:
        scope = (session_id, service_name)
        if scope not in cls._cache:
            return None
        return cls._cache[scope].get(cache_key)

    @classmethod
    def set(cls, service_name: str, cache_key: Tuple[Any, ...], value: Any, session_id: Optional[str] = None):
        scope = (session_id, service_name)
        if scope not in cls._cache:
            cls._cache[scope] = {}
        cls._cache[scope][cache_key] = value

    @classmethod
    def clear(cls, session_id: Optional[str] = None):
        if session_id is None:
            cls._cache.clear()
        else:
            keys_to_remove = [k for k in cls._cache if k[0] == session_id]
            for k in keys_to_remove:
                del cls._cache[k]
