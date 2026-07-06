from typing import Dict, Any, Tuple

class AnalyticsCache:
    # Structure: { service_name: { cache_key_tuple: cached_value } }
    _cache: Dict[str, Dict[Tuple[Any, ...], Any]] = {}

    @classmethod
    def get(cls, service_name: str, cache_key: Tuple[Any, ...]) -> Any:
        if service_name not in cls._cache:
            return None
        return cls._cache[service_name].get(cache_key)

    @classmethod
    def set(cls, service_name: str, cache_key: Tuple[Any, ...], value: Any):
        if service_name not in cls._cache:
            cls._cache[service_name] = {}
        cls._cache[service_name][cache_key] = value

    @classmethod
    def clear(cls):
        cls._cache.clear()
