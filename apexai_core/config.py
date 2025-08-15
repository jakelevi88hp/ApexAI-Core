"""
Configuration module for ApexAI-Core.

This module provides configuration management for the ApexAI-Core package.
It loads configuration from environment variables and .env files.
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Try to import dotenv for .env file support
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default configuration values
DEFAULT_CONFIG = {
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "OLLAMA_MODEL": "codellama:instruct",
    "MAX_CYCLES": 7,
    "PROJECT_ROOT": "apex_auto_project",
    "LOG_LEVEL": "INFO",
}


def load_config(env_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from environment variables and .env files.
    
    Args:
        env_file: Path to .env file (optional)
        
    Returns:
        Dictionary of configuration values
    """
    # Load .env file if available
    if DOTENV_AVAILABLE:
        if env_file and os.path.exists(env_file):
            load_dotenv(env_file)
            logger.debug(f"Loaded configuration from {env_file}")
        else:
            # Try to load from default locations
            for env_path in [".env", ".env.local", ".env.development"]:
                if os.path.exists(env_path):
                    load_dotenv(env_path)
                    logger.debug(f"Loaded configuration from {env_path}")
                    break
    else:
        logger.debug("python-dotenv not installed, skipping .env file loading")
    
    # Load configuration from environment variables with fallbacks
    config = {}
    for key, default_value in DEFAULT_CONFIG.items():
        env_value = os.getenv(key)
        if env_value is not None:
            # Convert to appropriate type based on default value
            if isinstance(default_value, int):
                try:
                    config[key] = int(env_value)
                except ValueError:
                    logger.warning(f"Invalid value for {key}: {env_value}, using default: {default_value}")
                    config[key] = default_value
            elif isinstance(default_value, float):
                try:
                    config[key] = float(env_value)
                except ValueError:
                    logger.warning(f"Invalid value for {key}: {env_value}, using default: {default_value}")
                    config[key] = default_value
            elif isinstance(default_value, bool):
                config[key] = env_value.lower() in ("true", "1", "yes", "y", "t")
            else:
                config[key] = env_value
        else:
            config[key] = default_value
    
    # Set up logging level
    logging.getLogger().setLevel(getattr(logging, config["LOG_LEVEL"]))
    
    return config


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path to the project root directory
    """
    config = load_config()
    project_root = Path(config["PROJECT_ROOT"])
    
    # Create project directory if it doesn't exist
    if not project_root.exists():
        project_root.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created project directory: {project_root}")
    
    return project_root


# Load configuration on module import
CONFIG = load_config()

