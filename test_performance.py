"""
Performance and benchmark tests for ApexAI-Core.

This module contains tests to measure and verify the performance characteristics
of the ApexAI-Core components. These tests are marked with the 'benchmark' marker
and can be skipped during regular testing with: pytest -k "not benchmark"
"""

import os
import sys
import time
import pytest
import tempfile
import shutil
from unittest.mock import patch, Mock

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multi_model_agent import MultiModelAgent
from god_code_agent_ollama import GODCodeAgentOllama


@pytest.mark.benchmark
class TestPerformance:
    """Performance tests for ApexAI-Core components."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('god_code_agent_ollama.requests.post')
    def test_ollama_generate_performance(self, mock_post):
        """Benchmark the performance of ollama_generate method."""
        # Setup mock response with delay to simulate API latency
        def delayed_response(*args, **kwargs):
            time.sleep(0.1)  # 100ms delay
            mock_resp = Mock()
            mock_resp.json.return_value = {'response': 'print("hello")'}
            mock_resp.raise_for_status.return_value = None
            return mock_resp
            
        mock_post.side_effect = delayed_response
        
        # Create agent
        agent = GODCodeAgentOllama(
            project_root=self.temp_dir,
            verbose=False
        )
        
        # Measure performance
        start_time = time.time()
        for _ in range(10):
            agent.ollama_generate("test mission")
        end_time = time.time()
        
        # Calculate average time per call
        avg_time = (end_time - start_time) / 10
        
        # Log performance metrics
        print(f"\nOllama generate average time: {avg_time:.4f} seconds")
        
        # Verify performance is within acceptable range
        # This is just a placeholder assertion since we're using mocks
        assert avg_time < 0.2, f"Performance too slow: {avg_time:.4f} seconds per call"

    def test_clean_generated_code_performance(self):
        """Benchmark the performance of _clean_generated_code method."""
        # Create agent
        agent = GODCodeAgentOllama(
            project_root=self.temp_dir,
            verbose=False
        )
        
        # Create a large code sample
        large_code = "```python\n" + "\n".join([f"print('Line {i}')" for i in range(1000)]) + "\n```"
        
        # Measure performance
        start_time = time.time()
        for _ in range(100):
            agent._clean_generated_code(large_code)
        end_time = time.time()
        
        # Calculate average time per call
        avg_time = (end_time - start_time) / 100
        
        # Log performance metrics
        print(f"\nClean generated code average time: {avg_time:.6f} seconds")
        
        # Verify performance is within acceptable range
        assert avg_time < 0.01, f"Performance too slow: {avg_time:.6f} seconds per call"

    def test_choose_model_performance(self):
        """Benchmark the performance of choose_model method."""
        # Create agent
        agent = MultiModelAgent(
            models={"code": "test-code-model", "general": "test-general-model"},
            verbose=False
        )
        
        # Create a large mission text
        large_mission = " ".join(["word" for _ in range(10000)])
        
        # Measure performance
        start_time = time.time()
        for _ in range(1000):
            agent.choose_model(large_mission)
        end_time = time.time()
        
        # Calculate average time per call
        avg_time = (end_time - start_time) / 1000
        
        # Log performance metrics
        print(f"\nChoose model average time: {avg_time:.6f} seconds")
        
        # Verify performance is within acceptable range
        assert avg_time < 0.001, f"Performance too slow: {avg_time:.6f} seconds per call"

    @patch('god_code_agent_ollama.subprocess.run')
    def test_file_operations_performance(self, mock_run):
        """Benchmark the performance of file operations."""
        # Setup mock
        mock_process = Mock()
        mock_process.stdout = "Mock output"
        mock_run.return_value = mock_process
        
        # Create agent
        agent = GODCodeAgentOllama(
            project_root=self.temp_dir,
            verbose=False
        )
        
        # Create a large code sample
        large_code = "\n".join([f"print('Line {i}')" for i in range(1000)])
        
        # Measure write performance
        start_time = time.time()
        for i in range(100):
            filename = os.path.join(self.temp_dir, f"test_{i}.py")
            agent.write_and_execute(large_code, filename)
        end_time = time.time()
        
        # Calculate average time per write operation
        avg_write_time = (end_time - start_time) / 100
        
        # Log performance metrics
        print(f"\nFile write and execute average time: {avg_write_time:.6f} seconds")
        
        # Verify performance is within acceptable range
        assert avg_write_time < 0.1, f"Performance too slow: {avg_write_time:.6f} seconds per operation"

    @patch('multi_model_agent.threading.Thread')
    def test_gui_responsiveness(self, mock_thread):
        """Test GUI responsiveness by measuring event handling time."""
        # Create a mock for Tkinter
        with patch('multi_model_agent.tk.Tk') as mock_tk:
            # Setup mock root
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            # Create agent
            agent = MultiModelAgent(verbose=False)
            
            # Mock StringVar
            with patch('multi_model_agent.tk.StringVar') as mock_stringvar:
                # Setup mock variable
                mock_var = Mock()
                mock_var.get.return_value = "Test mission"
                mock_stringvar.return_value = mock_var
                
                # Launch GUI but intercept before mainloop
                with patch.object(mock_root, 'mainloop'):
                    agent.launch_gui()
                    
                    # Find the run_action function
                    run_action = None
                    for name, attr in mock_root.mock_calls:
                        if isinstance(attr, Mock) and hasattr(attr, 'call_args'):
                            if attr.call_args and len(attr.call_args) > 0:
                                if "Run Mission" in str(attr.call_args):
                                    run_action = attr.call_args[1].get('command')
                                    break
                    
                    if run_action:
                        # Measure performance of run_action
                        start_time = time.time()
                        run_action()
                        end_time = time.time()
                        
                        # Calculate time
                        action_time = end_time - start_time
                        
                        # Log performance metrics
                        print(f"\nGUI run action time: {action_time:.6f} seconds")
                        
                        # Verify performance is within acceptable range
                        assert action_time < 0.1, f"GUI responsiveness too slow: {action_time:.6f} seconds"
                    else:
                        pytest.skip("Could not find run_action function in GUI")


@pytest.mark.benchmark
def test_memory_usage():
    """Test memory usage of the agents."""
    try:
        import psutil
        import os
        
        # Get current process
        process = psutil.Process(os.getpid())
        
        # Measure memory before creating agents
        memory_before = process.memory_info().rss / 1024 / 1024  # Convert to MB
        
        # Create agents
        temp_dir = tempfile.mkdtemp()
        god_agent = GODCodeAgentOllama(project_root=temp_dir, verbose=False)
        multi_agent = MultiModelAgent(project_root=temp_dir, verbose=False)
        
        # Measure memory after creating agents
        memory_after = process.memory_info().rss / 1024 / 1024  # Convert to MB
        
        # Calculate memory usage
        memory_usage = memory_after - memory_before
        
        # Log memory usage
        print(f"\nMemory usage for agents: {memory_usage:.2f} MB")
        
        # Verify memory usage is within acceptable range
        assert memory_usage < 50, f"Memory usage too high: {memory_usage:.2f} MB"
        
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)
        
    except ImportError:
        pytest.skip("psutil not installed, skipping memory usage test")


if __name__ == '__main__':
    pytest.main(['-v', __file__])

