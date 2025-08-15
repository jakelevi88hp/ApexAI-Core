"""
ApexAI-Core - AI automation stack for business operations.

This package provides a framework for building AI-powered applications
using local language models through Ollama.
"""

__version__ = "0.2.0"

from apexai_core.config import load_config, get_project_root
from apexai_core.utils import (
    check_ollama_availability,
    list_available_models,
    run_command,
    install_package,
    is_fastapi_code,
    create_file,
)
from apexai_core.di import container, get_service, register_defaults
from apexai_core.metrics import metrics, timed, counted, traced
from apexai_core.cache import memory_cache, disk_cache, memoized, disk_cached
from apexai_core.security import CodeSandbox, InputValidator, secure_execution_wrapper
from apexai_core.parallel import task_manager, run_in_thread, run_in_process

# Initialize dependency injection
register_defaults()

