"""
Parallel execution module for ApexAI-Core.

This module provides parallel execution capabilities for the ApexAI-Core package.
It includes thread pools, process pools, and async task management.
"""

import os
import time
import asyncio
import logging
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future
from typing import Dict, List, Set, Tuple, Optional, Any, Union, Callable, TypeVar, Generic

logger = logging.getLogger(__name__)

# Type variables
T = TypeVar('T')
R = TypeVar('R')


class Task(Generic[T]):
    """
    A task that can be executed in parallel.
    
    This class represents a task that can be executed in parallel,
    with support for cancellation, progress tracking, and result retrieval.
    
    Attributes:
        id: Unique identifier for the task
        status: Current status of the task
        progress: Progress of the task (0-100)
        result: Result of the task (if completed)
        error: Error message (if failed)
    """
    
    def __init__(self, task_id: str, func: Callable[..., T], *args, **kwargs):
        """
        Initialize a Task.
        
        Args:
            task_id: Unique identifier for the task
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        """
        self.id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.status = "pending"
        self.progress = 0
        self.result = None
        self.error = None
        self.future = None
        self.start_time = None
        self.end_time = None
    
    def execute(self) -> T:
        """
        Execute the task.
        
        Returns:
            Result of the task
        """
        self.status = "running"
        self.start_time = time.time()
        
        try:
            self.result = self.func(*self.args, **self.kwargs)
            self.status = "completed"
            return self.result
        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            logger.error(f"Task {self.id} failed: {e}")
            raise
        finally:
            self.end_time = time.time()
            self.progress = 100
    
    def cancel(self) -> bool:
        """
        Cancel the task.
        
        Returns:
            True if the task was cancelled, False otherwise
        """
        if self.status in ["pending", "running"]:
            self.status = "cancelled"
            
            if self.future and not self.future.done():
                return self.future.cancel()
                
            return True
        
        return False
    
    def get_duration(self) -> Optional[float]:
        """
        Get the duration of the task in seconds.
        
        Returns:
            Duration in seconds or None if the task hasn't started or completed
        """
        if self.start_time is None:
            return None
            
        end_time = self.end_time or time.time()
        return end_time - self.start_time
    
    def __str__(self) -> str:
        """
        Get a string representation of the task.
        
        Returns:
            String representation of the task
        """
        return f"Task(id={self.id}, status={self.status}, progress={self.progress})"


class TaskManager:
    """
    Manager for parallel tasks.
    
    This class manages the execution of parallel tasks using thread pools,
    process pools, or asyncio tasks.
    
    Attributes:
        max_workers: Maximum number of worker threads or processes
        tasks: Dictionary of tasks by ID
        thread_pool: ThreadPoolExecutor for thread-based tasks
        process_pool: ProcessPoolExecutor for process-based tasks
    """
    
    def __init__(self, max_workers: Optional[int] = None):
        """
        Initialize a TaskManager.
        
        Args:
            max_workers: Maximum number of worker threads or processes
        """
        self.max_workers = max_workers or min(32, os.cpu_count() + 4)
        self.tasks: Dict[str, Task] = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=self.max_workers)
        self._lock = threading.RLock()
    
    def submit_thread_task(self, task_id: str, func: Callable[..., T], *args, **kwargs) -> Task[T]:
        """
        Submit a task to be executed in a thread pool.
        
        Args:
            task_id: Unique identifier for the task
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Task object
        """
        with self._lock:
            task = Task(task_id, func, *args, **kwargs)
            future = self.thread_pool.submit(task.execute)
            task.future = future
            self.tasks[task_id] = task
            return task
    
    def submit_process_task(self, task_id: str, func: Callable[..., T], *args, **kwargs) -> Task[T]:
        """
        Submit a task to be executed in a process pool.
        
        Args:
            task_id: Unique identifier for the task
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Task object
        """
        with self._lock:
            task = Task(task_id, func, *args, **kwargs)
            future = self.process_pool.submit(task.execute)
            task.future = future
            self.tasks[task_id] = task
            return task
    
    async def submit_async_task(self, task_id: str, func: Callable[..., T], *args, **kwargs) -> Task[T]:
        """
        Submit a task to be executed as an asyncio task.
        
        Args:
            task_id: Unique identifier for the task
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Task object
        """
        with self._lock:
            task = Task(task_id, func, *args, **kwargs)
            
            # Create a wrapper coroutine
            async def wrapper():
                task.status = "running"
                task.start_time = time.time()
                
                try:
                    task.result = await func(*args, **kwargs)
                    task.status = "completed"
                except Exception as e:
                    task.status = "failed"
                    task.error = str(e)
                    logger.error(f"Async task {task_id} failed: {e}")
                    raise
                finally:
                    task.end_time = time.time()
                    task.progress = 100
                
                return task.result
            
            # Create an asyncio task
            asyncio_task = asyncio.create_task(wrapper())
            task.future = asyncio_task
            self.tasks[task_id] = task
            return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task to get
            
        Returns:
            Task object or None if not found
        """
        return self.tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task by ID.
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            True if the task was cancelled, False otherwise
        """
        task = self.get_task(task_id)
        if task:
            return task.cancel()
        return False
    
    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks.
        
        Returns:
            List of all tasks
        """
        return list(self.tasks.values())
    
    def get_active_tasks(self) -> List[Task]:
        """
        Get all active tasks.
        
        Returns:
            List of active tasks
        """
        return [task for task in self.tasks.values() if task.status in ["pending", "running"]]
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shut down the task manager.
        
        Args:
            wait: Whether to wait for tasks to complete
        """
        self.thread_pool.shutdown(wait=wait)
        self.process_pool.shutdown(wait=wait)


# Create a global task manager
task_manager = TaskManager()


def run_in_thread(func: Callable[..., T]) -> Callable[..., Future[T]]:
    """
    Decorator to run a function in a thread.
    
    Args:
        func: Function to run in a thread
        
    Returns:
        Decorated function that returns a Future
    """
    def wrapper(*args, **kwargs) -> Future[T]:
        return task_manager.thread_pool.submit(func, *args, **kwargs)
    return wrapper


def run_in_process(func: Callable[..., T]) -> Callable[..., Future[T]]:
    """
    Decorator to run a function in a separate process.
    
    Args:
        func: Function to run in a process
        
    Returns:
        Decorated function that returns a Future
    """
    def wrapper(*args, **kwargs) -> Future[T]:
        return task_manager.process_pool.submit(func, *args, **kwargs)
    return wrapper

