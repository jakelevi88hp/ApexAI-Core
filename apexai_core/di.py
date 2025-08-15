"""
Dependency Injection module for ApexAI-Core.

This module provides a simple dependency injection container for the ApexAI-Core package.
It allows for better testability and flexibility by decoupling component dependencies.
"""

import logging
from typing import Dict, Any, Callable, Optional, Type, TypeVar, cast

logger = logging.getLogger(__name__)

T = TypeVar('T')


class DIContainer:
    """
    A simple dependency injection container.
    
    This container allows registering and resolving dependencies,
    making it easier to swap implementations for testing or configuration.
    
    Attributes:
        _services: Dictionary mapping service types to their factory functions
    """
    
    def __init__(self):
        """Initialize the DIContainer with an empty services dictionary."""
        self._services: Dict[Type, Callable[..., Any]] = {}
        
    def register(self, service_type: Type[T], factory: Callable[..., T]) -> None:
        """
        Register a service factory function for a given type.
        
        Args:
            service_type: The type to register
            factory: A factory function that creates an instance of the service
        """
        self._services[service_type] = factory
        logger.debug(f"Registered service: {service_type.__name__}")
        
    def register_instance(self, service_type: Type[T], instance: T) -> None:
        """
        Register an existing instance for a given type.
        
        Args:
            service_type: The type to register
            instance: An instance of the service
        """
        self._services[service_type] = lambda: instance
        logger.debug(f"Registered instance: {service_type.__name__}")
        
    def resolve(self, service_type: Type[T]) -> T:
        """
        Resolve a service instance for a given type.
        
        Args:
            service_type: The type to resolve
            
        Returns:
            An instance of the requested service
            
        Raises:
            KeyError: If the service type is not registered
        """
        if service_type not in self._services:
            raise KeyError(f"Service not registered: {service_type.__name__}")
            
        return cast(T, self._services[service_type]())
        
    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        logger.debug("Cleared all registered services")


# Create a global container instance
container = DIContainer()


def register_defaults() -> None:
    """Register default service implementations."""
    from apexai_core.agents.god_code_agent import GODCodeAgentOllama
    from apexai_core.agents.multi_model_agent import MultiModelAgent
    from apexai_core.agents.async_agent import AsyncAgent
    
    # Register default implementations
    container.register(GODCodeAgentOllama, lambda: GODCodeAgentOllama())
    container.register(MultiModelAgent, lambda: MultiModelAgent())
    container.register(AsyncAgent, lambda: AsyncAgent())
    
    logger.debug("Registered default service implementations")


def get_service(service_type: Type[T]) -> T:
    """
    Get a service instance for a given type.
    
    This is a convenience function for resolving services from the global container.
    
    Args:
        service_type: The type to resolve
        
    Returns:
        An instance of the requested service
    """
    return container.resolve(service_type)

