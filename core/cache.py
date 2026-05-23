from datetime import datetime, timedelta
from functools import wraps
import json
import os

class Cache:
    def __init__(self, expire_hours=24):
        self._cache = {}
        self.expire_hours = expire_hours

    def set(self, key, value, expire_hours=None):
        expire_at = datetime.now() + timedelta(hours=expire_hours or self.expire_hours)
        self._cache[key] = {
            'value': value,
            'expire_at': expire_at
        }

    def get(self, key):
        if key not in self._cache:
            return None
        
        cache_data = self._cache[key]
        if datetime.now() > cache_data['expire_at']:
            del self._cache[key]
            return None
            
        return cache_data['value']

    def delete(self, key):
        if key in self._cache:
            del self._cache[key]

cache = Cache()

def cached(expire_hours=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            result = cache.get(key)
            
            if result is None:
                result = func(*args, **kwargs)
                cache.set(key, result, expire_hours)
                
            return result
        return wrapper
    return decorator