"""
Pytest configuration and fixtures for ApexAI-Core tests.

This module provides shared fixtures and configuration for all test modules.
"""

import os
import sys
import pytest
import tempfile
import shutil
from unittest.mock import patch, Mock

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multi_model_agent import MultiModelAgent
from god_code_agent_ollama import GODCodeAgentOllama


@pytest.fixture
def temp_project_dir():
    """Create a temporary directory for project files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_ollama_api():
    """Mock the Ollama API responses."""
    with patch('god_code_agent_ollama.requests.post') as mock_post:
        # Setup default mock response
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'print("hello from mock")'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        yield mock_post


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls."""
    with patch('subprocess.run') as mock_run:
        # Setup default mock response
        mock_process = Mock()
        mock_process.stdout = "Mock subprocess output"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        yield mock_run


@pytest.fixture
def god_agent(temp_project_dir):
    """Create a GODCodeAgentOllama instance with a temporary project directory."""
    agent = GODCodeAgentOllama(
        project_root=temp_project_dir,
        max_cycles=3,
        verbose=False
    )
    return agent


@pytest.fixture
def multi_agent(temp_project_dir):
    """Create a MultiModelAgent instance with a temporary project directory."""
    # Patch GODCodeAgentOllama to avoid actual initialization
    with patch('multi_model_agent.GODCodeAgentOllama') as mock_god_agent:
        # Setup the mock to return a properly configured mock object
        mock_instance = Mock()
        mock_god_agent.return_value = mock_instance
        
        # Create the MultiModelAgent
        agent = MultiModelAgent(
            models={"code": "test-code-model", "general": "test-general-model"},
            project_root=temp_project_dir,
            max_cycles=3,
            verbose=False
        )
        
        # Replace the mocked agent with a real one for better integration testing
        agent.agent = GODCodeAgentOllama(
            project_root=temp_project_dir,
            max_cycles=3,
            verbose=False
        )
        
        return agent


@pytest.fixture
def mock_environment():
    """Mock environment variables."""
    original_environ = os.environ.copy()
    
    # Set test environment variables
    test_env = {
        'PROJECT_ROOT': '/tmp/test_project',
        'MAX_CYCLES': '3',
        'OLLAMA_BASE_URL': 'http://test-ollama:11434',
        'OLLAMA_MODEL': 'test-model'
    }
    
    with patch.dict(os.environ, test_env, clear=True):
        yield test_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_environ)


@pytest.fixture
def disable_logging():
    """Disable logging during tests."""
    import logging
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)

