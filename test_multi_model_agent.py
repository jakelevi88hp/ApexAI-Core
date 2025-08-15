"""
Unit tests for MultiModelAgent

Tests cover the key functionalities including model selection, mission execution,
self-update, and GUI components while mocking external dependencies.
"""

import os
import sys
import unittest
import logging
import tkinter as tk
import threading
import subprocess
from unittest.mock import patch, Mock, MagicMock, call

# Add the parent directory to the path to import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multi_model_agent import MultiModelAgent


class TestMultiModelAgent(unittest.TestCase):
    """Test suite for MultiModelAgent class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Disable logging during tests
        logging.disable(logging.CRITICAL)
        
        # Create a mock for GODCodeAgentOllama
        self.mock_god_agent_patcher = patch('multi_model_agent.GODCodeAgentOllama')
        self.mock_god_agent = self.mock_god_agent_patcher.start()
        
        # Initialize the agent with test models
        self.agent = MultiModelAgent(
            models={"code": "test-code-model", "general": "test-general-model"},
            verbose=False
        )
        
    def tearDown(self):
        """Clean up after each test method."""
        # Re-enable logging
        logging.disable(logging.NOTSET)
        
        # Stop the patcher
        self.mock_god_agent_patcher.stop()

    def test_init_default_values(self):
        """Test initialization with default values."""
        agent = MultiModelAgent()
        self.assertEqual(agent.models["code"], "codellama:instruct")
        self.assertEqual(agent.models["general"], "llama2")
        self.mock_god_agent.assert_called_once()

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        custom_models = {"code": "custom-code", "general": "custom-general"}
        agent = MultiModelAgent(
            models=custom_models,
            project_root="/custom/path",
            max_cycles=5,
            verbose=True
        )
        self.assertEqual(agent.models, custom_models)
        self.mock_god_agent.assert_called_once_with("/custom/path", 5, True)
        self.assertTrue(agent.verbose)

    def test_init_exception_handling(self):
        """Test initialization with exception."""
        self.mock_god_agent.side_effect = Exception("Test error")
        with self.assertRaises(Exception):
            MultiModelAgent()

    def test_choose_model_code_keywords(self):
        """Test model selection with code-related keywords."""
        code_missions = [
            "Write a Python script to parse CSV files",
            "Create a function to calculate fibonacci numbers",
            "Build an API for user authentication",
            "Implement a class for data processing",
            "Design an algorithm for sorting arrays"
        ]
        
        for mission in code_missions:
            model = self.agent.choose_model(mission)
            self.assertEqual(model, "test-code-model")

    def test_choose_model_general_keywords(self):
        """Test model selection with general keywords."""
        general_missions = [
            "Tell me a story about dragons",
            "What is the capital of France?",
            "Explain quantum physics",
            "Write a poem about nature",
            "Summarize the plot of Hamlet"
        ]
        
        for mission in general_missions:
            model = self.agent.choose_model(mission)
            self.assertEqual(model, "test-general-model")

    def test_choose_model_mixed_content(self):
        """Test model selection with mixed content."""
        # Should select code model if any code keywords are present
        mixed_mission = "Write a poem about Python programming language and include a code example"
        model = self.agent.choose_model(mixed_mission)
        self.assertEqual(model, "test-code-model")

    def test_choose_model_exception_handling(self):
        """Test model selection with exception."""
        # Create a new agent with a mocked choose_model that raises an exception
        agent = MultiModelAgent(
            models={"code": "test-code-model", "general": "test-general-model"},
            verbose=False
        )
        
        # Mock the any() function to raise an exception
        with patch('multi_model_agent.any', side_effect=Exception("Test error")):
            model = agent.choose_model("Test mission")
            # Should fall back to general model
            self.assertEqual(model, "test-general-model")

    @patch.dict('os.environ', {}, clear=True)
    def test_run_mission(self):
        """Test run_mission method."""
        # Setup
        mission = "Write a Python script to parse CSV files"
        context = "Previous context"
        
        # Execute
        self.agent.run_mission(mission, context)
        
        # Verify
        self.assertEqual(os.environ.get("OLLAMA_MODEL"), "test-code-model")
        self.agent.agent.recursive_build.assert_called_once_with(mission, context)

    def test_run_mission_empty(self):
        """Test run_mission with empty mission."""
        self.agent.run_mission("")
        # Should not call recursive_build
        self.agent.agent.recursive_build.assert_not_called()

    def test_run_mission_exception(self):
        """Test run_mission with exception."""
        self.agent.agent.recursive_build.side_effect = Exception("Test error")
        with self.assertRaises(Exception):
            self.agent.run_mission("Test mission")

    @patch('multi_model_agent.subprocess.run')
    def test_self_update_success_up_to_date(self, mock_run):
        """Test self_update when already up to date."""
        mock_process = Mock()
        mock_process.stdout = "Already up to date."
        mock_run.return_value = mock_process
        
        result = self.agent.self_update()
        self.assertTrue(result)
        mock_run.assert_called_once()

    @patch('multi_model_agent.subprocess.run')
    def test_self_update_success_updated(self, mock_run):
        """Test self_update when update is successful."""
        mock_process = Mock()
        mock_process.stdout = "Updating 1234abc..5678def\nFast-forward\n file changed"
        mock_run.return_value = mock_process
        
        result = self.agent.self_update()
        self.assertTrue(result)
        mock_run.assert_called_once()

    @patch('multi_model_agent.subprocess.run')
    def test_self_update_failure_called_process_error(self, mock_run):
        """Test self_update with CalledProcessError."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git pull", stderr="fatal: not a git repository")
        
        result = self.agent.self_update()
        self.assertFalse(result)
        mock_run.assert_called_once()

    @patch('multi_model_agent.subprocess.run')
    def test_self_update_failure_timeout(self, mock_run):
        """Test self_update with TimeoutExpired."""
        mock_run.side_effect = subprocess.TimeoutExpired("git pull", 30)
        
        result = self.agent.self_update()
        self.assertFalse(result)
        mock_run.assert_called_once()

    @patch('multi_model_agent.subprocess.run')
    def test_self_update_failure_exception(self, mock_run):
        """Test self_update with generic exception."""
        mock_run.side_effect = Exception("Test error")
        
        result = self.agent.self_update()
        self.assertFalse(result)
        mock_run.assert_called_once()

    def test_generate_improvement(self):
        """Test generate_improvement method."""
        mission = "Add error handling"
        expected_output = "def improved_function():\n    try:\n        pass\n    except Exception as e:\n        print(f'Error: {e}')"
        
        self.agent.agent.ollama_generate.return_value = expected_output
        
        result = self.agent.generate_improvement(mission)
        self.assertEqual(result, expected_output)
        self.agent.agent.ollama_generate.assert_called_once_with(f"Improve the agent code: {mission}")

    def test_generate_improvement_exception(self):
        """Test generate_improvement with exception."""
        self.agent.agent.ollama_generate.side_effect = Exception("Test error")
        
        result = self.agent.generate_improvement("Test mission")
        self.assertTrue(result.startswith("# Error generating improvement"))


class TestMultiModelAgentGUI(unittest.TestCase):
    """Test suite for MultiModelAgent GUI components."""

    @patch('multi_model_agent.tk.Tk')
    @patch('multi_model_agent.ttk.Frame')
    @patch('multi_model_agent.ttk.LabelFrame')
    @patch('multi_model_agent.ttk.Entry')
    @patch('multi_model_agent.scrolledtext.ScrolledText')
    @patch('multi_model_agent.ttk.Button')
    @patch('multi_model_agent.ttk.Label')
    def test_launch_gui_initialization(self, mock_label, mock_button, mock_scrolledtext, 
                                      mock_entry, mock_labelframe, mock_frame, mock_tk):
        """Test GUI initialization."""
        # Setup mocks
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        # Create agent
        agent = MultiModelAgent(verbose=False)
        
        # Mock threading to avoid actual thread creation
        with patch('multi_model_agent.threading.Thread'):
            # Launch GUI
            agent.launch_gui()
        
        # Verify GUI initialization
        mock_tk.assert_called_once()
        mock_root.title.assert_called_once_with("Apex MultiModelAgent")
        mock_root.geometry.assert_called_once_with("600x400")
        mock_root.mainloop.assert_called_once()

    @patch('multi_model_agent.tk.Tk')
    @patch('multi_model_agent.messagebox')
    def test_gui_run_action_empty_mission(self, mock_messagebox, mock_tk):
        """Test GUI run action with empty mission."""
        # Setup mocks
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        # Create a StringVar mock that returns empty string
        mock_stringvar = Mock()
        mock_stringvar.get.return_value = ""
        
        # Patch tk.StringVar to return our mock
        with patch('multi_model_agent.tk.StringVar', return_value=mock_stringvar):
            # Create agent
            agent = MultiModelAgent(verbose=False)
            
            # Launch GUI but intercept before mainloop
            with patch.object(mock_root, 'mainloop'):
                agent.launch_gui()
                
                # Get the run_action function from the GUI
                # This is tricky because it's a nested function
                # We need to find the Button creation with "Run Mission" text
                for call_args in mock_root.mock_calls:
                    if isinstance(call_args, call) and len(call_args.args) > 0:
                        if "Run Mission" in str(call_args):
                            # Extract the command function
                            run_action = call_args.kwargs.get('command')
                            if run_action:
                                # Call the function
                                run_action()
                                # Verify error message was shown
                                mock_messagebox.showerror.assert_called_once()
                                return
        
        self.fail("Could not find Run Mission button command")

    @patch('multi_model_agent.tk.Tk')
    def test_gui_exception_handling(self, mock_tk):
        """Test GUI exception handling."""
        # Setup mock to raise exception
        mock_tk.side_effect = Exception("Test error")
        
        # Create agent
        agent = MultiModelAgent(verbose=False)
        
        # Mock sys.exit to avoid actual exit
        with patch('multi_model_agent.sys.exit') as mock_exit:
            with patch('multi_model_agent.messagebox.showerror') as mock_error:
                # Launch GUI which should raise exception
                agent.launch_gui()
                
                # Verify error handling
                mock_error.assert_called_once()
                mock_exit.assert_called_once_with(1)


if __name__ == '__main__':
    unittest.main()
