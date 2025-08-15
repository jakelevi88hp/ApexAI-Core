"""
Tests for the CLI module.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from apexai_core.cli import parse_args, main


def test_parse_args_version():
    """Test that parse_args correctly parses the version command."""
    args = parse_args(["version"])
    assert args.command == "version"


def test_parse_args_run():
    """Test that parse_args correctly parses the run command."""
    args = parse_args(["run", "Test mission"])
    assert args.command == "run"
    assert args.mission == "Test mission"
    assert args.context == ""
    assert args.model_type == "auto"


def test_parse_args_gui():
    """Test that parse_args correctly parses the gui command."""
    args = parse_args(["gui"])
    assert args.command == "gui"


def test_parse_args_generate():
    """Test that parse_args correctly parses the generate command."""
    args = parse_args(["generate", "Test mission"])
    assert args.command == "generate"
    assert args.mission == "Test mission"
    assert args.output == "generated_code.py"


@patch("apexai_core.cli.GODCodeAgentOllama")
def test_main_version(mock_agent):
    """Test that main correctly handles the version command."""
    with patch.object(sys, "argv", ["apexai", "version"]):
        with patch("apexai_core.cli.print") as mock_print:
            exit_code = main()
            assert exit_code == 0
            mock_print.assert_called_once()
            assert "version" in mock_print.call_args[0][0]


@patch("apexai_core.cli.GODCodeAgentOllama")
def test_main_run(mock_agent):
    """Test that main correctly handles the run command."""
    # Mock the GODCodeAgentOllama instance
    mock_instance = MagicMock()
    mock_agent.return_value = mock_instance
    
    # Run the command
    with patch.object(sys, "argv", ["apexai", "run", "Test mission"]):
        exit_code = main()
        
        # Check that the command was successful
        assert exit_code == 0
        
        # Check that the agent was created with the expected arguments
        mock_agent.assert_called_once()
        
        # Check that recursive_build was called with the expected arguments
        mock_instance.recursive_build.assert_called_once_with("Test mission", "")


@patch("apexai_core.cli.MultiModelAgent")
def test_main_gui(mock_agent):
    """Test that main correctly handles the gui command."""
    # Mock the MultiModelAgent instance
    mock_instance = MagicMock()
    mock_agent.return_value = mock_instance
    
    # Run the command
    with patch.object(sys, "argv", ["apexai", "gui"]):
        exit_code = main()
        
        # Check that the command was successful
        assert exit_code == 0
        
        # Check that the agent was created with the expected arguments
        mock_agent.assert_called_once()
        
        # Check that launch_gui was called
        mock_instance.launch_gui.assert_called_once()

