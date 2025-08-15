"""
Metrics and monitoring module for ApexAI-Core.

This module provides metrics collection and monitoring capabilities
for the ApexAI-Core package using Prometheus and OpenTelemetry.
"""

import time
import logging
import functools
import threading
from typing import Dict, Any, Callable, Optional, Type, TypeVar, cast, Union

# Try to import Prometheus client
try:
    import prometheus_client as prom
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Try to import OpenTelemetry
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

logger = logging.getLogger(__name__)

# Type variables for function decorators
F = TypeVar('F', bound=Callable[..., Any])
T = TypeVar('T')


class Metrics:
    """
    Metrics collection and monitoring for ApexAI-Core.
    
    This class provides metrics collection and monitoring capabilities
    using Prometheus and OpenTelemetry.
    
    Attributes:
        enabled: Whether metrics collection is enabled
        prometheus_port: Port for the Prometheus HTTP server
        _counters: Dictionary of Prometheus counters
        _gauges: Dictionary of Prometheus gauges
        _histograms: Dictionary of Prometheus histograms
    """
    
    def __init__(self, enabled: bool = True, prometheus_port: int = 8000):
        """
        Initialize the Metrics instance.
        
        Args:
            enabled: Whether metrics collection is enabled
            prometheus_port: Port for the Prometheus HTTP server
        """
        self.enabled = enabled
        self.prometheus_port = prometheus_port
        
        # Initialize Prometheus metrics
        self._counters = {}
        self._gauges = {}
        self._histograms = {}
        
        # Initialize OpenTelemetry
        self._tracer = None
        
        if enabled:
            self._setup_metrics()
    
    def _setup_metrics(self) -> None:
        """Set up metrics collection."""
        # Set up Prometheus
        if PROMETHEUS_AVAILABLE and self.enabled:
            try:
                # Start Prometheus HTTP server
                prom.start_http_server(self.prometheus_port)
                logger.info(f"Prometheus metrics server started on port {self.prometheus_port}")
                
                # Create default metrics
                self._counters["code_generation_total"] = prom.Counter(
                    "code_generation_total",
                    "Total number of code generation requests",
                    ["model", "success"]
                )
                
                self._counters["code_execution_total"] = prom.Counter(
                    "code_execution_total",
                    "Total number of code execution requests",
                    ["type", "success"]
                )
                
                self._histograms["code_generation_duration_seconds"] = prom.Histogram(
                    "code_generation_duration_seconds",
                    "Duration of code generation requests in seconds",
                    ["model"]
                )
                
                self._histograms["code_execution_duration_seconds"] = prom.Histogram(
                    "code_execution_duration_seconds",
                    "Duration of code execution requests in seconds",
                    ["type"]
                )
                
                self._gauges["active_missions"] = prom.Gauge(
                    "active_missions",
                    "Number of active missions"
                )
                
            except Exception as e:
                logger.error(f"Failed to start Prometheus metrics server: {e}")
                self.enabled = False
        
        # Set up OpenTelemetry
        if OPENTELEMETRY_AVAILABLE and self.enabled:
            try:
                # Set up tracer provider
                provider = TracerProvider()
                processor = BatchSpanProcessor(ConsoleSpanExporter())
                provider.add_span_processor(processor)
                trace.set_tracer_provider(provider)
                
                # Create tracer
                self._tracer = trace.get_tracer("apexai_core")
                logger.info("OpenTelemetry tracer initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize OpenTelemetry: {e}")
                self._tracer = None
    
    def increment_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> None:
        """
        Increment a Prometheus counter.
        
        Args:
            name: Name of the counter
            labels: Labels for the counter
        """
        if not self.enabled or not PROMETHEUS_AVAILABLE:
            return
            
        try:
            if name in self._counters:
                if labels:
                    self._counters[name].labels(**labels).inc()
                else:
                    self._counters[name].inc()
        except Exception as e:
            logger.error(f"Failed to increment counter {name}: {e}")
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """
        Observe a value in a Prometheus histogram.
        
        Args:
            name: Name of the histogram
            value: Value to observe
            labels: Labels for the histogram
        """
        if not self.enabled or not PROMETHEUS_AVAILABLE:
            return
            
        try:
            if name in self._histograms:
                if labels:
                    self._histograms[name].labels(**labels).observe(value)
                else:
                    self._histograms[name].observe(value)
        except Exception as e:
            logger.error(f"Failed to observe histogram {name}: {e}")
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """
        Set a Prometheus gauge.
        
        Args:
            name: Name of the gauge
            value: Value to set
            labels: Labels for the gauge
        """
        if not self.enabled or not PROMETHEUS_AVAILABLE:
            return
            
        try:
            if name in self._gauges:
                if labels:
                    self._gauges[name].labels(**labels).set(value)
                else:
                    self._gauges[name].set(value)
        except Exception as e:
            logger.error(f"Failed to set gauge {name}: {e}")
    
    def create_span(self, name: str) -> Optional[Any]:
        """
        Create an OpenTelemetry span.
        
        Args:
            name: Name of the span
            
        Returns:
            An OpenTelemetry span or None if tracing is not available
        """
        if not self.enabled or not OPENTELEMETRY_AVAILABLE or not self._tracer:
            return None
            
        try:
            return self._tracer.start_as_current_span(name)
        except Exception as e:
            logger.error(f"Failed to create span {name}: {e}")
            return None


# Create a global metrics instance
metrics = Metrics(enabled=True)


def timed(name: str, labels: Optional[Dict[str, str]] = None) -> Callable[[F], F]:
    """
    Decorator to time a function and record the duration in a histogram.
    
    Args:
        name: Name of the histogram
        labels: Labels for the histogram
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                metrics.observe_histogram(name, duration, labels)
        return cast(F, wrapper)
    return decorator


def counted(name: str, labels: Optional[Dict[str, str]] = None) -> Callable[[F], F]:
    """
    Decorator to count function calls.
    
    Args:
        name: Name of the counter
        labels: Labels for the counter
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = func(*args, **kwargs)
                if labels:
                    metrics.increment_counter(name, {**labels, "success": "true"})
                else:
                    metrics.increment_counter(name, {"success": "true"})
                return result
            except Exception as e:
                if labels:
                    metrics.increment_counter(name, {**labels, "success": "false"})
                else:
                    metrics.increment_counter(name, {"success": "false"})
                raise
        return cast(F, wrapper)
    return decorator


def traced(name: str) -> Callable[[F], F]:
    """
    Decorator to trace a function with OpenTelemetry.
    
    Args:
        name: Name of the span
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with metrics.create_span(name) or nullcontext():
                return func(*args, **kwargs)
        return cast(F, wrapper)
    return decorator


class nullcontext:
    """A context manager that does nothing."""
    
    def __enter__(self) -> None:
        pass
        
    def __exit__(self, *args: Any) -> None:
        pass

