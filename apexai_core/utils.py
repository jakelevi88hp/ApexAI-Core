"""
Utility functions for ApexAI-Core.

This module provides utility functions for the ApexAI-Core package.
"""

import os
import sys
import logging
import subprocess
from typing import List, Tuple, Optional, Any

logger = logging.getLogger(__name__)


def check_ollama_availability(base_url: str = "http://localhost:11434") -> bool:
    """
    Check if Ollama is available at the specified URL.
    
    Args:
        base_url: Base URL for the Ollama API
        
    Returns:
        True if Ollama is available, False otherwise
    """
    import requests
    
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.warning(f"Ollama not available at {base_url}: {e}")
        return False


def list_available_models(base_url: str = "http://localhost:11434") -> List[str]:
    """
    List available models in Ollama.
    
    Args:
        base_url: Base URL for the Ollama API
        
    Returns:
        List of available model names
        
    Raises:
        ConnectionError: If Ollama is not available
    """
    import requests
    
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get("models", [])
        return [model["name"] for model in models]
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to list models: {e}")
        raise ConnectionError(f"Failed to connect to Ollama at {base_url}: {e}")


def run_command(command: List[str], timeout: int = 60, cwd: Optional[str] = None) -> Tuple[bool, str]:
    """
    Run a command and return the result.
    
    Args:
        command: Command to run as a list of strings
        timeout: Timeout in seconds
        cwd: Working directory for the command
        
    Returns:
        Tuple of (success: bool, output: str)
    """
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr}")
        return False, e.stderr
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after {timeout} seconds")
        return False, f"Command timed out after {timeout} seconds"
    except Exception as e:
        logger.error(f"Unexpected error running command: {e}")
        return False, str(e)


def install_package(package_name: str) -> bool:
    """
    Install a Python package using pip.
    
    Args:
        package_name: Name of the package to install
        
    Returns:
        True if installation was successful, False otherwise
    """
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Successfully installed package: {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install package {package_name}: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error installing package {package_name}: {e}")
        return False


def is_fastapi_code(code: str) -> bool:
    """
    Check if the code appears to be a FastAPI application.
    
    Args:
        code: Python code to analyze
        
    Returns:
        True if code appears to be a FastAPI application
    """
    return ("FastAPI" in code or "uvicorn" in code) and ("app = FastAPI()" in code)


def create_file(file_path: str, content: str) -> bool:
    """
    Create a file with the specified content.
    
    Args:
        file_path: Path to the file to create
        content: Content to write to the file
        
    Returns:
        True if file creation was successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Write content to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        logger.debug(f"Created file: {file_path}")
        return True
    except IOError as e:
        logger.error(f"Failed to create file {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error creating file {file_path}: {e}")
        return False

