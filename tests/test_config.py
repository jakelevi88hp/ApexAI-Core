"""
Tests for the config module.
"""

import os
import pytest
from unittest.mock import patch
from apexai_core.config import load_config, get_project_root, DEFAULT_CONFIG


def test_load_config_defaults():
    """Test that load_config returns default values when no environment variables are set."""
    # Clear environment variables
    with patch.dict(os.environ, {}, clear=True):
        config = load_config()
        
        # Check that default values are used
        for key, value in DEFAULT_CONFIG.items():
            assert config[key] == value


def test_load_config_from_env():
    """Test that load_config loads values from environment variables."""
    # Set environment variables
    test_values = {
        "OLLAMA_BASE_URL": "http://test:11434",
        "OLLAMA_MODEL": "test-model",
        "MAX_CYCLES": "10",
        "PROJECT_ROOT": "test_project",
        "LOG_LEVEL": "DEBUG",
    }
    
    with patch.dict(os.environ, test_values):
        config = load_config()
        
        # Check that environment values are used
        assert config["OLLAMA_BASE_URL"] == "http://test:11434"
        assert config["OLLAMA_MODEL"] == "test-model"
        assert config["MAX_CYCLES"] == 10  # Should be converted to int
        assert config["PROJECT_ROOT"] == "test_project"
        assert config["LOG_LEVEL"] == "DEBUG"


def test_get_project_root():
    """Test that get_project_root returns a Path object."""
    with patch.dict(os.environ, {"PROJECT_ROOT": "test_project"}):
        project_root = get_project_root()
        
        # Check that project_root is a Path object
        assert project_root.name == "test_project"
        
        # Check that the directory exists
        assert project_root.exists()
        
        # Clean up
        project_root.rmdir()

