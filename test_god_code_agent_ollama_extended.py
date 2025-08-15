"""
Extended unit tests for GODCodeAgentOllama

This module provides additional test coverage for the GODCodeAgentOllama class,
focusing on edge cases, error handling, and complex scenarios.
"""

import unittest
import os
import sys
import tempfile
import shutil
import json
import subprocess
from unittest.mock import patch, Mock, mock_open, MagicMock

# Add the parent directory to the path to import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from god_code_agent_ollama import GODCodeAgentOllama


class TestGODCodeAgentOllamaExtended(unittest.TestCase):
    """Extended test suite for GODCodeAgentOllama class."""

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

    def test_init_with_environment_variables_partial(self):
        """Test initialization with partial environment variables."""
        with patch.dict(os.environ, {
            'PROJECT_ROOT': '/tmp/test_project',
            # MAX_CYCLES not set
        }):
            agent = GODCodeAgentOllama(verbose=False)
            self.assertEqual(agent.project_root, '/tmp/test_project')
            # Should use default max_cycles
            self.assertEqual(agent.max_cycles, 7)

    def test_init_with_invalid_environment_variables(self):
        """Test initialization with invalid environment variables."""
        with patch.dict(os.environ, {
            'MAX_CYCLES': 'not_a_number'
        }):
            # Should use default max_cycles when environment variable is invalid
            agent = GODCodeAgentOllama(verbose=False)
            self.assertEqual(agent.max_cycles, 7)

    def test_clean_generated_code_complex(self):
        """Test _clean_generated_code with complex input."""
        raw_code = """
Here's a Python script to solve your problem:

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
print(fibonacci(10))
```

You can run this script with Python 3.x.

Here's another example in JavaScript:

```javascript
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}
console.log(fibonacci(10));
```
        """
        cleaned = self.agent._clean_generated_code(raw_code)
        expected = "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\n# Test the function\nprint(fibonacci(10))"
        self.assertEqual(cleaned, expected)

    def test_clean_generated_code_multiple_code_blocks(self):
        """Test _clean_generated_code with multiple code blocks."""
        raw_code = """
First, let's create a function:

```python
def hello():
    print("Hello world")
```

Now, let's create another function:

```python
def goodbye():
    print("Goodbye world")
```
        """
        cleaned = self.agent._clean_generated_code(raw_code)
        # Should extract the first code block only
        expected = "def hello():\n    print(\"Hello world\")"
        self.assertEqual(cleaned, expected)

    def test_clean_generated_code_no_code_blocks(self):
        """Test _clean_generated_code with no code blocks."""
        raw_code = "This is just text without any code blocks."
        cleaned = self.agent._clean_generated_code(raw_code)
        # Should fall back to default
        expected = "print('Hello world from GODCodeAgent')"
        self.assertEqual(cleaned, expected)

    def test_clean_generated_code_empty_code_blocks(self):
        """Test _clean_generated_code with empty code blocks."""
        raw_code = "```python\n```"
        cleaned = self.agent._clean_generated_code(raw_code)
        # Should fall back to default
        expected = "print('Hello world from GODCodeAgent')"
        self.assertEqual(cleaned, expected)

    def test_operator_review_syntax_error(self):
        """Test operator_review with syntax error."""
        code = "def invalid_function():\nprint('Missing indentation')"
        result = self.agent.operator_review(code, "test.py")
        self.assertFalse(result)

    def test_operator_review_indentation_error(self):
        """Test operator_review with indentation error."""
        code = "def valid_function():\n    print('Correct indentation')\n  print('Wrong indentation')"
        result = self.agent.operator_review(code, "test.py")
        self.assertFalse(result)

    def test_operator_review_import_error(self):
        """Test operator_review with import error."""
        code = "import non_existent_module"
        # Import errors are not caught by static analysis, so this should pass
        result = self.agent.operator_review(code, "test.py")
        self.assertTrue(result)

    def test_should_run_with_uvicorn_starlette(self):
        """Test should_run_with_uvicorn with Starlette code."""
        code = "from starlette.applications import Starlette\napp = Starlette()"
        result = self.agent.should_run_with_uvicorn(code, "test.py")
        self.assertTrue(result)

    def test_should_run_with_uvicorn_commented_import(self):
        """Test should_run_with_uvicorn with commented FastAPI import."""
        code = "# from fastapi import FastAPI\n# app = FastAPI()\nprint('Hello world')"
        result = self.agent.should_run_with_uvicorn(code, "test.py")
        self.assertFalse(result)

    def test_destroyer_prune_nonexistent_file(self):
        """Test destroyer_prune with nonexistent file."""
        non_existent_file = os.path.join(self.temp_dir, "non_existent.py")
        # Should not raise an exception
        self.agent.destroyer_prune(non_existent_file)
        self.assertFalse(os.path.exists(non_existent_file))

    def test_destroyer_prune_directory(self):
        """Test destroyer_prune with directory."""
        test_dir = os.path.join(self.temp_dir, "test_dir")
        os.makedirs(test_dir)
        self.assertTrue(os.path.exists(test_dir))
        
        # Should not raise an exception
        self.agent.destroyer_prune(test_dir)
        self.assertFalse(os.path.exists(test_dir))

    @patch('god_code_agent_ollama.subprocess.run')
    def test_auto_install_module_multiple_modules(self, mock_run):
        """Test auto_install_module with multiple missing modules."""
        mock_run.return_value = Mock()
        error_output = "ModuleNotFoundError: No module named 'requests'\nModuleNotFoundError: No module named 'pandas'"
        
        self.agent.auto_install_module(error_output)
        # Should install both modules
        mock_run.assert_any_call(
            [sys.executable, "-m", "pip", "install", "requests"],
            check=True,
            capture_output=True,
            text=True
        )
        mock_run.assert_any_call(
            [sys.executable, "-m", "pip", "install", "pandas"],
            check=True,
            capture_output=True,
            text=True
        )

    @patch('god_code_agent_ollama.subprocess.run')
    def test_auto_install_module_no_modules(self, mock_run):
        """Test auto_install_module with no missing modules."""
        error_output = "SyntaxError: invalid syntax"
        
        self.agent.auto_install_module(error_output)
        # Should not call pip install
        mock_run.assert_not_called()

    @patch('god_code_agent_ollama.requests.post')
    def test_ollama_generate_with_context(self, mock_post):
        """Test ollama_generate with context."""
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'print("hello with context")'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.agent.ollama_generate("test mission", "previous context")
        self.assertEqual(result, 'print("hello with context")')
        
        # Verify that context was included in the request
        _, kwargs = mock_post.call_args
        self.assertIn("previous context", kwargs['json']['prompt'])

    @patch('god_code_agent_ollama.requests.post')
    def test_ollama_generate_with_custom_model(self, mock_post):
        """Test ollama_generate with custom model."""
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'print("hello from custom model")'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Set custom model in environment
        with patch.dict(os.environ, {'OLLAMA_MODEL': 'custom-model'}):
            result = self.agent.ollama_generate("test mission")
            self.assertEqual(result, 'print("hello from custom model")')
            
            # Verify that custom model was used
            _, kwargs = mock_post.call_args
            self.assertEqual(kwargs['json']['model'], 'custom-model')

    @patch('god_code_agent_ollama.requests.post')
    def test_ollama_generate_with_custom_base_url(self, mock_post):
        """Test ollama_generate with custom base URL."""
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'print("hello from custom URL")'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Set custom base URL in environment
        with patch.dict(os.environ, {'OLLAMA_BASE_URL': 'http://custom-ollama:11434'}):
            result = self.agent.ollama_generate("test mission")
            self.assertEqual(result, 'print("hello from custom URL")')
            
            # Verify that custom base URL was used
            args, _ = mock_post.call_args
            self.assertEqual(args[0], 'http://custom-ollama:11434/api/generate')

    @patch('god_code_agent_ollama.subprocess.run')
    def test_execute_regular_python_with_args(self, mock_run):
        """Test _execute_regular_python with command line arguments."""
        mock_process = Mock()
        mock_process.stdout = "Hello World"
        mock_run.return_value = mock_process
        
        test_file = os.path.join(self.temp_dir, "test.py")
        success, output = self.agent._execute_regular_python(test_file, ["arg1", "arg2"])
        
        self.assertTrue(success)
        self.assertEqual(output, "Hello World")
        
        # Verify that arguments were passed
        args, _ = mock_run.call_args
        self.assertEqual(args[0], [sys.executable, test_file, "arg1", "arg2"])

    @patch('god_code_agent_ollama.subprocess.run')
    def test_execute_with_uvicorn(self, mock_run):
        """Test _execute_with_uvicorn method."""
        # Create a mock for Popen
        mock_popen = Mock()
        mock_popen.pid = 12345
        mock_popen.poll.return_value = None  # Process is running
        
        # Create a mock for subprocess.run that returns a mock process
        mock_run.return_value = Mock(stdout="Uvicorn running on http://127.0.0.1:8000")
        
        # Patch subprocess.Popen to return our mock
        with patch('god_code_agent_ollama.subprocess.Popen', return_value=mock_popen):
            # Patch time.sleep to avoid actual sleep
            with patch('god_code_agent_ollama.time.sleep'):
                test_file = os.path.join(self.temp_dir, "test_api.py")
                success, output = self.agent._execute_with_uvicorn(test_file)
                
                self.assertTrue(success)
                self.assertIn("Uvicorn running", output)
                
                # Verify that uvicorn was called correctly
                args, _ = mock_run.call_args
                self.assertEqual(args[0], ["uvicorn", "test_api:app", "--reload"])

    def test_write_and_execute_file_with_uvicorn(self):
        """Test write_and_execute with FastAPI code."""
        code = "from fastapi import FastAPI\napp = FastAPI()\n\n@app.get('/')\ndef root():\n    return {'message': 'Hello World'}"
        filename = os.path.join(self.temp_dir, "test_api.py")
        
        # Patch _execute_with_uvicorn to avoid actual execution
        with patch.object(self.agent, '_execute_with_uvicorn', return_value=(True, "Uvicorn running")):
            success, output = self.agent.write_and_execute(code, filename)
            
            self.assertTrue(success)
            self.assertIn("Uvicorn running", output)
            
            # Verify that file was written correctly
            with open(filename, 'r') as f:
                written_code = f.read()
                self.assertEqual(written_code, code)

    def test_recursive_build_with_context(self):
        """Test recursive_build with context."""
        # Patch ollama_generate to return simple code
        with patch.object(self.agent, 'ollama_generate', return_value='print("hello")'):
            # Patch write_and_execute to simulate successful execution
            with patch.object(self.agent, 'write_and_execute', return_value=(True, "Hello")):
                self.agent.recursive_build("test mission", "previous context")
                
                # Verify that context was passed to ollama_generate
                self.agent.ollama_generate.assert_called_with("test mission", "previous context")

    def test_recursive_build_failure(self):
        """Test recursive_build with execution failure."""
        # Patch ollama_generate to return simple code
        with patch.object(self.agent, 'ollama_generate', return_value='print("hello")'):
            # Patch write_and_execute to simulate failed execution
            with patch.object(self.agent, 'write_and_execute', return_value=(False, "Error")):
                # Patch operator_review to pass
                with patch.object(self.agent, 'operator_review', return_value=True):
                    self.agent.recursive_build("test mission")
                    
                    # Should still create the file despite execution failure
                    expected_file = os.path.join(self.temp_dir, "module_1.py")
                    self.assertTrue(os.path.exists(expected_file))


class TestGODCodeAgentOllamaIntegrationExtended(unittest.TestCase):
    """Extended integration tests for GODCodeAgentOllama."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('god_code_agent_ollama.requests.post')
    def test_recursive_build_with_dependencies(self, mock_post):
        """Test recursive_build with code that has dependencies."""
        # First response includes import of non-existent module
        first_response = 'import nonexistent_module\n\nprint("Hello World")'
        # Second response after error is fixed code
        second_response = 'print("Fixed Hello World")'
        
        # Setup mock to return different responses
        mock_response1 = Mock()
        mock_response1.json.return_value = {'response': first_response}
        mock_response1.raise_for_status.return_value = None
        
        mock_response2 = Mock()
        mock_response2.json.return_value = {'response': second_response}
        mock_response2.raise_for_status.return_value = None
        
        mock_post.side_effect = [mock_response1, mock_response2]
        
        # Mock subprocess.run for _execute_regular_python
        with patch('god_code_agent_ollama.subprocess.run') as mock_run:
            # First execution fails with ModuleNotFoundError
            mock_run.side_effect = [
                subprocess.CalledProcessError(1, "python", stderr="ModuleNotFoundError: No module named 'nonexistent_module'"),
                Mock(stdout="Fixed Hello World")  # Second execution succeeds
            ]
            
            # Mock auto_install_module to simulate installation
            with patch.object(GODCodeAgentOllama, 'auto_install_module') as mock_install:
                agent = GODCodeAgentOllama(
                    project_root=self.temp_dir,
                    max_cycles=2,
                    verbose=False
                )
                
                # Run the recursive build
                agent.recursive_build("test mission")
                
                # Verify auto_install_module was called
                mock_install.assert_called_once()
                
                # Should have created module files
                expected_files = ["module_1.py", "module_2.py"]
                for filename in expected_files:
                    self.assertTrue(os.path.exists(os.path.join(self.temp_dir, filename)))

    @patch('god_code_agent_ollama.requests.post')
    def test_recursive_build_with_review_failure(self, mock_post):
        """Test recursive_build with code that fails review."""
        # First response has syntax error
        first_response = 'def invalid_function():\nprint("Missing indentation")'
        # Second response is fixed code
        second_response = 'def valid_function():\n    print("Correct indentation")'
        
        # Setup mock to return different responses
        mock_response1 = Mock()
        mock_response1.json.return_value = {'response': first_response}
        mock_response1.raise_for_status.return_value = None
        
        mock_response2 = Mock()
        mock_response2.json.return_value = {'response': second_response}
        mock_response2.raise_for_status.return_value = None
        
        mock_post.side_effect = [mock_response1, mock_response2]
        
        # Mock subprocess.run for _execute_regular_python to succeed on second try
        with patch('god_code_agent_ollama.subprocess.run') as mock_run:
            mock_run.return_value = Mock(stdout="Correct indentation")
            
            agent = GODCodeAgentOllama(
                project_root=self.temp_dir,
                max_cycles=2,
                verbose=False
            )
            
            # Run the recursive build
            agent.recursive_build("test mission")
            
            # Should have created module files
            expected_files = ["module_1.py", "module_2.py"]
            for filename in expected_files:
                self.assertTrue(os.path.exists(os.path.join(self.temp_dir, filename)))
            
            # Verify the content of the second file
            with open(os.path.join(self.temp_dir, "module_2.py"), 'r') as f:
                content = f.read()
                self.assertEqual(content, second_response)


if __name__ == '__main__':
    unittest.main()

