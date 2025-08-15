"""
Caching module for ApexAI-Core.

This module provides caching capabilities for the ApexAI-Core package.
It includes a simple in-memory cache and a disk-based cache.
"""

import os
import json
import time
import hashlib
import logging
import functools
import threading
from typing import Dict, Any, Callable, Optional, TypeVar, cast, Union, Tuple

logger = logging.getLogger(__name__)

# Type variables for function decorators
F = TypeVar('F', bound=Callable[..., Any])
T = TypeVar('T')


class Cache:
    """
    Base cache interface.
    
    This class defines the interface for all cache implementations.
    """
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        raise NotImplementedError
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
        """
        raise NotImplementedError
    
    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
        """
        raise NotImplementedError
    
    def clear(self) -> None:
        """Clear all values from the cache."""
        raise NotImplementedError


class MemoryCache(Cache):
    """
    In-memory cache implementation.
    
    This class implements a simple in-memory cache with optional TTL.
    
    Attributes:
        _cache: Dictionary of cached values
        _expiry: Dictionary of expiry times
        _lock: Thread lock for thread safety
    """
    
    def __init__(self):
        """Initialize the MemoryCache with empty dictionaries."""
        self._cache: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        with self._lock:
            if key not in self._cache:
                return None
                
            # Check if the value has expired
            if key in self._expiry and time.time() > self._expiry[key]:
                self.delete(key)
                return None
                
            return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
        """
        with self._lock:
            self._cache[key] = value
            
            if ttl is not None:
                self._expiry[key] = time.time() + ttl
    
    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                
            if key in self._expiry:
                del self._expiry[key]
    
    def clear(self) -> None:
        """Clear all values from the cache."""
        with self._lock:
            self._cache.clear()
            self._expiry.clear()


class DiskCache(Cache):
    """
    Disk-based cache implementation.
    
    This class implements a disk-based cache with optional TTL.
    
    Attributes:
        cache_dir: Directory for cache files
        _lock: Thread lock for thread safety
    """
    
    def __init__(self, cache_dir: str = ".cache"):
        """
        Initialize the DiskCache.
        
        Args:
            cache_dir: Directory for cache files
        """
        self.cache_dir = cache_dir
        self._lock = threading.RLock()
        
        # Create cache directory if it doesn't exist
        try:
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir)
                logger.debug(f"Created cache directory: {self.cache_dir}")
        except OSError as e:
            logger.error(f"Failed to create cache directory {self.cache_dir}: {e}")
            raise
    
    def _get_cache_path(self, key: str) -> str:
        """
        Get the file path for a cache key.
        
        Args:
            key: Cache key
            
        Returns:
            File path for the cache key
        """
        # Hash the key to create a valid filename
        hashed_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hashed_key}.json")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        cache_path = self._get_cache_path(key)
        
        with self._lock:
            if not os.path.exists(cache_path):
                return None
                
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                    
                # Check if the value has expired
                if "expiry" in cache_data and time.time() > cache_data["expiry"]:
                    self.delete(key)
                    return None
                    
                return cache_data["value"]
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Failed to read cache file {cache_path}: {e}")
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
        """
        cache_path = self._get_cache_path(key)
        
        with self._lock:
            try:
                cache_data = {
                    "value": value,
                }
                
                if ttl is not None:
                    cache_data["expiry"] = time.time() + ttl
                    
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f)
            except (IOError, TypeError) as e:
                logger.error(f"Failed to write cache file {cache_path}: {e}")
    
    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
        """
        cache_path = self._get_cache_path(key)
        
        with self._lock:
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                except OSError as e:
                    logger.error(f"Failed to delete cache file {cache_path}: {e}")
    
    def clear(self) -> None:
        """Clear all values from the cache."""
        with self._lock:
            try:
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith(".json"):
                        os.remove(os.path.join(self.cache_dir, filename))
            except OSError as e:
                logger.error(f"Failed to clear cache directory {self.cache_dir}: {e}")


# Create global cache instances
memory_cache = MemoryCache()
disk_cache = DiskCache()


def cached(cache: Cache, ttl: Optional[int] = None) -> Callable[[F], F]:
    """
    Decorator to cache function results.
    
    Args:
        cache: Cache instance to use
        ttl: Time to live in seconds (optional)
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create a cache key from the function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # Try to get the result from the cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
                
            # Call the function and cache the result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
            
        return cast(F, wrapper)
    return decorator


def memoized(func: F) -> F:
    """
    Decorator to memoize function results in memory.
    
    This is a convenience decorator that uses the memory_cache.
    
    Args:
        func: Function to memoize
        
    Returns:
        Decorated function
    """
    return cached(memory_cache)(func)


def disk_cached(ttl: Optional[int] = None) -> Callable[[F], F]:
    """
    Decorator to cache function results on disk.
    
    This is a convenience decorator that uses the disk_cache.
    
    Args:
        ttl: Time to live in seconds (optional)
        
    Returns:
        Decorated function
    """
    return cached(disk_cache, ttl)

