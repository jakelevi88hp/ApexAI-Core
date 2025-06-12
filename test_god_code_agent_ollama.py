"""
Unit tests for GODCodeAgentOllama

Tests cover the key functionalities including code generation, execution,
review, and utility functions while mocking external dependencies.
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import os
import tempfile
import shutil
import sys
import subprocess

# Add the parent directory to the path to import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from god_code_agent_ollama import GODCodeAgentOllama


class TestGODCodeAgentOllama(unittest.TestCase):
    """Test suite for GODCodeAgentOllama class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.agent = GODCodeAgentOllama(
            project_root=self.temp_dir,
            max_cycles=3,
            verbose=False
        )

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_creates_project_directory(self):
        """Test that initialization creates the project directory."""
        new_temp_dir = tempfile.mkdtemp()
        shutil.rmtree(new_temp_dir)  # Remove so we can test creation
        
        agent = GODCodeAgentOllama(project_root=new_temp_dir, verbose=False)
        self.assertTrue(os.path.exists(new_temp_dir))
        
        shutil.rmtree(new_temp_dir, ignore_errors=True)

    def test_init_with_environment_variables(self):
        """Test initialization with environment variables."""
        with patch.dict(os.environ, {
            'PROJECT_ROOT': '/tmp/test_project',
            'MAX_CYCLES': '5'
        }):
            agent = GODCodeAgentOllama(verbose=False)
            self.assertEqual(agent.max_cycles, 5)

    def test_clean_generated_code(self):
        """Test the _clean_generated_code method."""
        raw_code = "```python\nprint('hello')\n```\n..."
        cleaned = self.agent._clean_generated_code(raw_code)
        expected = "print('hello')"
        self.assertEqual(cleaned, expected)

    def test_clean_generated_code_fallback(self):
        """Test _clean_generated_code with invalid input that gets filtered out."""
        raw_code = "```\nThis script does something\n```"  # This should get filtered out
        cleaned = self.agent._clean_generated_code(raw_code)
        # The cleaning function filters out invalid lines, so this should fall back to default
        self.assertEqual(cleaned, "print('Hello world from GODCodeAgent')")

    def test_operator_review_passes(self):
        """Test operator_review with code that should pass."""
        code = "def hello():\n    print('Hello world')"
        result = self.agent.operator_review(code, "test.py")
        self.assertTrue(result)

    def test_operator_review_fails(self):
        """Test operator_review with code that should fail."""
        code = "invalid code here"
        result = self.agent.operator_review(code, "test.py")
        self.assertFalse(result)

    def test_should_run_with_uvicorn_true(self):
        """Test should_run_with_uvicorn with FastAPI code."""
        code = "from fastapi import FastAPI\napp = FastAPI()"
        result = self.agent.should_run_with_uvicorn(code, "test.py")
        self.assertTrue(result)

    def test_should_run_with_uvicorn_false(self):
        """Test should_run_with_uvicorn with regular Python code."""
        code = "print('Hello world')"
        result = self.agent.should_run_with_uvicorn(code, "test.py")
        self.assertFalse(result)

    def test_destroyer_prune(self):
        """Test destroyer_prune removes files."""
        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, "w") as f:
            f.write("test content")
        
        self.assertTrue(os.path.exists(test_file))
        self.agent.destroyer_prune(test_file)
        self.assertFalse(os.path.exists(test_file))

    @patch('god_code_agent_ollama.subprocess.run')
    def test_auto_install_module_success(self, mock_run):
        """Test auto_install_module with successful installation."""
        mock_run.return_value = Mock()
        error_output = "ModuleNotFoundError: No module named 'requests'"
        
        self.agent.auto_install_module(error_output)
        mock_run.assert_called_with(
            [sys.executable, "-m", "pip", "install", "requests"],
            check=True,
            capture_output=True,
            text=True
        )

    @patch('god_code_agent_ollama.subprocess.run')
    def test_auto_install_module_failure(self, mock_run):
        """Test auto_install_module with failed installation."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "pip", stderr="Installation failed")
        error_output = "ModuleNotFoundError: No module named 'nonexistent'"
        
        # Should not raise exception, just log error
        self.agent.auto_install_module(error_output)

    @patch('god_code_agent_ollama.requests.post')
    def test_ollama_generate_success(self, mock_post):
        """Test ollama_generate with successful API response."""
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'print("hello world")'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.agent.ollama_generate("test mission")
        self.assertEqual(result, 'print("hello world")')

    @patch('god_code_agent_ollama.requests.post')
    def test_ollama_generate_api_error(self, mock_post):
        """Test ollama_generate with API error."""
        mock_post.side_effect = Exception("API Error")
        
        result = self.agent.ollama_generate("test mission")
        self.assertIn("Unexpected Error", result)

    @patch('god_code_agent_ollama.requests.post')
    def test_ollama_generate_invalid_response(self, mock_post):
        """Test ollama_generate with invalid API response."""
        mock_response = Mock()
        mock_response.json.return_value = {'invalid': 'response'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.agent.ollama_generate("test mission")
        self.assertIn("Invalid Response", result)

    @patch('god_code_agent_ollama.subprocess.run')
    def test_execute_regular_python_success(self, mock_run):
        """Test _execute_regular_python with successful execution."""
        mock_process = Mock()
        mock_process.stdout = "Hello World"
        mock_run.return_value = mock_process
        
        test_file = os.path.join(self.temp_dir, "test.py")
        success, output = self.agent._execute_regular_python(test_file)
        
        self.assertTrue(success)
        self.assertEqual(output, "Hello World")

    @patch('god_code_agent_ollama.subprocess.run')
    def test_execute_regular_python_failure(self, mock_run):
        """Test _execute_regular_python with execution failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "python", stderr="Syntax Error")
        
        test_file = os.path.join(self.temp_dir, "test.py")
        with self.assertRaises(subprocess.CalledProcessError):
            self.agent._execute_regular_python(test_file)

    def test_write_and_execute_file_write_error(self):
        """Test write_and_execute with file write error."""
        # Try to write to a directory that doesn't exist
        invalid_path = "/nonexistent/directory/test.py"
        success, output = self.agent.write_and_execute("print('test')", invalid_path)
        
        self.assertFalse(success)
        self.assertIn("File write error", output)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('god_code_agent_ollama.requests.post')
    def test_recursive_build_max_cycles(self, mock_post):
        """Test recursive_build respects max_cycles limit."""
        # Mock API to return simple code that passes review
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'print("hello")'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        agent = GODCodeAgentOllama(
            project_root=self.temp_dir,
            max_cycles=2,
            verbose=False
        )
        
        # This should stop after 2 cycles
        agent.recursive_build("test mission")
        
        # Should have created 2 module files
        expected_files = ["module_1.py", "module_2.py"]
        for filename in expected_files:
            self.assertTrue(os.path.exists(os.path.join(self.temp_dir, filename)))


if __name__ == '__main__':
    unittest.main()