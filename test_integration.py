"""
Integration tests for ApexAI-Core

Tests the integration between MultiModelAgent and GODCodeAgentOllama classes,
ensuring they work together correctly in various scenarios.
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, Mock

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multi_model_agent import MultiModelAgent
from god_code_agent_ollama import GODCodeAgentOllama


class TestApexAIIntegration(unittest.TestCase):
    """Integration tests for ApexAI-Core components."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Patch environment variables
        self.env_patcher = patch.dict('os.environ', {
            'PROJECT_ROOT': self.temp_dir,
            'MAX_CYCLES': '3',
            'OLLAMA_BASE_URL': 'http://localhost:11434',
            'OLLAMA_MODEL': 'codellama:instruct'
        })
        self.env_patcher.start()

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.env_patcher.stop()

    @patch('god_code_agent_ollama.requests.post')
    def test_model_selection_affects_api_call(self, mock_post):
        """Test that model selection in MultiModelAgent affects the API call in GODCodeAgentOllama."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'print("hello")'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Create agent with custom models
        agent = MultiModelAgent(
            models={"code": "test-code-model", "general": "test-general-model"},
            verbose=False
        )
        
        # Run a code-related mission
        mission = "Write a Python function to calculate factorial"
        agent.run_mission(mission)
        
        # Verify that the code model was selected
        self.assertEqual(os.environ.get("OLLAMA_MODEL"), "test-code-model")
        
        # Verify the API call used the correct model
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['model'], "test-code-model")
        
        # Run a general mission
        mission = "Tell me about the history of AI"
        agent.run_mission(mission)
        
        # Verify that the general model was selected
        self.assertEqual(os.environ.get("OLLAMA_MODEL"), "test-general-model")
        
        # Verify the API call used the correct model
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['model'], "test-general-model")

    @patch('god_code_agent_ollama.requests.post')
    @patch('multi_model_agent.subprocess.run')
    def test_self_update_affects_both_agents(self, mock_run, mock_post):
        """Test that self_update in MultiModelAgent affects both agents."""
        # Setup mock response for API
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'print("hello")'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Setup mock for subprocess.run (git pull)
        mock_process = Mock()
        mock_process.stdout = "Updating 1234abc..5678def\nFast-forward\n file changed"
        mock_run.return_value = mock_process
        
        # Create agent
        agent = MultiModelAgent(verbose=False)
        
        # Perform self-update
        result = agent.self_update()
        self.assertTrue(result)
        
        # Run a mission after update
        mission = "Write a Python function"
        agent.run_mission(mission)
        
        # Verify that the API call was made correctly
        mock_post.assert_called()

    @patch('god_code_agent_ollama.requests.post')
    def test_error_propagation(self, mock_post):
        """Test that errors in GODCodeAgentOllama propagate to MultiModelAgent."""
        # Setup mock to raise exception
        mock_post.side_effect = Exception("API Error")
        
        # Create agent
        agent = MultiModelAgent(verbose=False)
        
        # Run a mission that should fail
        with self.assertRaises(Exception):
            agent.run_mission("Write a Python function")

    @patch('god_code_agent_ollama.requests.post')
    def test_generate_improvement_integration(self, mock_post):
        """Test generate_improvement integration between both classes."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'def improved_function():\n    pass'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Create agent
        agent = MultiModelAgent(verbose=False)
        
        # Generate improvement
        improvement = agent.generate_improvement("Add error handling")
        
        # Verify the result
        self.assertEqual(improvement, 'def improved_function():\n    pass')
        
        # Verify the API call
        _, kwargs = mock_post.call_args
        self.assertIn("Improve the agent code: Add error handling", kwargs['json']['prompt'])

    @patch('god_code_agent_ollama.requests.post')
    def test_context_passing(self, mock_post):
        """Test that context is properly passed between agents."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'print("hello with context")'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Create agent
        agent = MultiModelAgent(verbose=False)
        
        # Run mission with context
        context = "Previous code: def old_function(): pass"
        agent.run_mission("Write a Python function", context)
        
        # Verify the API call included the context
        _, kwargs = mock_post.call_args
        self.assertIn(context, kwargs['json']['prompt'])


class TestEnvironmentConfiguration(unittest.TestCase):
    """Tests for environment configuration and initialization."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Save original environment
        self.original_environ = os.environ.copy()
        
        # Create temp directory
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after each test method."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_environ)
        
        # Remove temp directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_dotenv_loading(self):
        """Test that .env file is loaded correctly."""
        # Create a .env file in the temp directory
        env_path = os.path.join(self.temp_dir, '.env')
        with open(env_path, 'w') as f:
            f.write("""
            # Test .env file
            OLLAMA_BASE_URL=http://test-server:11434
            OLLAMA_MODEL=test-model
            MAX_CYCLES=5
            PROJECT_ROOT=/custom/path
            """)
        
        # Patch os.path.exists to return True for .env file
        with patch('os.path.exists', return_value=True):
            # Patch open to return our custom .env file
            with patch('builtins.open', mock_open(read_data=open(env_path).read())):
                # Import dotenv and load it
                from dotenv import load_dotenv
                load_dotenv()
                
                # Create agents
                god_agent = GODCodeAgentOllama(verbose=False)
                multi_agent = MultiModelAgent(verbose=False)
                
                # Verify environment variables were loaded
                self.assertEqual(os.environ.get('OLLAMA_BASE_URL'), 'http://test-server:11434')
                self.assertEqual(os.environ.get('OLLAMA_MODEL'), 'test-model')
                self.assertEqual(os.environ.get('MAX_CYCLES'), '5')
                self.assertEqual(os.environ.get('PROJECT_ROOT'), '/custom/path')
                
                # Verify agent configuration
                self.assertEqual(god_agent.max_cycles, 5)
                self.assertEqual(multi_agent.agent.max_cycles, 5)


if __name__ == '__main__':
    unittest.main()

