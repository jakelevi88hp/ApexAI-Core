# ApexAI-Core

ApexAI-Core is an AI automation stack for business operations. It provides a framework for building AI-powered applications using local language models through Ollama.

## Features

- **Code Generation**: Generate Python code based on natural language descriptions
- **Recursive Refinement**: Automatically refine and improve generated code
- **Multiple Models**: Support for multiple language models with automatic selection
- **FastAPI Integration**: Automatic detection and execution of FastAPI applications
- **GUI Interface**: Simple graphical user interface for interacting with the agent
- **CLI Interface**: Command-line interface for automation and scripting
- **Dependency Management**: Automatic installation of missing dependencies
- **Asynchronous Support**: Async/await syntax for better performance
- **Dependency Injection**: Better testability and flexibility
- **Metrics and Monitoring**: Prometheus and OpenTelemetry integration
- **Caching**: In-memory and disk-based caching
- **Security**: Code sandboxing and input validation
- **Parallel Execution**: Thread pools, process pools, and async task management

## Installation

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.com/) - for running local language models

### Install from Source

```bash
# Clone the repository
git clone https://github.com/jakelevi88hp/ApexAI-Core.git
cd ApexAI-Core

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

### Install Required Models

Make sure Ollama is running, then pull the required models:

```bash
ollama pull codellama:instruct
ollama pull llama2
```

## Usage

### Command-Line Interface

```bash
# Show help
apexai --help

# Run a mission
apexai run "Create a Python function to calculate the factorial of a number"

# Run a mission with async execution
apexai run --async "Create a Python function to calculate the factorial of a number"

# Launch the GUI
apexai gui

# Generate code without executing
apexai generate "Create a Python function to calculate the factorial of a number" --output factorial.py

# List available models
apexai models

# Execute code in a sandbox
apexai sandbox my_script.py

# Show version information
apexai version
```

### Python API

```python
from apexai_core.agents import GODCodeAgentOllama, MultiModelAgent, AsyncAgent

# Create a GODCodeAgentOllama instance
agent = GODCodeAgentOllama(verbose=True)

# Generate and execute code
agent.recursive_build("Create a Python function to calculate the factorial of a number")

# Create a MultiModelAgent instance
multi_agent = MultiModelAgent(verbose=True)

# Run a mission with automatic model selection
multi_agent.run_mission("Create a Python function to calculate the factorial of a number")

# Launch the GUI
multi_agent.launch_gui()

# Create an AsyncAgent instance
async_agent = AsyncAgent(verbose=True)

# Run a mission asynchronously
import asyncio
asyncio.run(async_agent.recursive_build_async("Create a Python function to calculate the factorial of a number"))
```

### Advanced Features

#### Dependency Injection

```python
from apexai_core.di import container, get_service
from apexai_core.agents import GODCodeAgentOllama

# Register a custom implementation
container.register(GODCodeAgentOllama, lambda: MyCustomAgent())

# Get the service
agent = get_service(GODCodeAgentOllama)
```

#### Metrics and Monitoring

```python
from apexai_core.metrics import metrics, timed, counted, traced

# Use decorators for metrics
@timed("my_function_duration_seconds")
@counted("my_function_calls_total")
@traced("my_function")
def my_function():
    # Function code here
    pass

# Use metrics directly
metrics.increment_counter("my_counter", {"label": "value"})
metrics.observe_histogram("my_histogram", 0.5, {"label": "value"})
metrics.set_gauge("my_gauge", 42, {"label": "value"})
```

#### Caching

```python
from apexai_core.cache import memoized, disk_cached

# Use decorators for caching
@memoized
def expensive_function():
    # Function code here
    pass

@disk_cached(ttl=3600)  # Cache for 1 hour
def expensive_function_with_ttl():
    # Function code here
    pass
```

#### Security

```python
from apexai_core.security import CodeSandbox, InputValidator, secure_execution_wrapper

# Validate user input
valid, error = InputValidator.validate_mission("User input")
if not valid:
    print(f"Invalid input: {error}")

# Execute code in a sandbox
sandbox = CodeSandbox()
success, output = sandbox.execute_code("print('Hello, world!')")
```

#### Parallel Execution

```python
from apexai_core.parallel import task_manager, run_in_thread, run_in_process

# Use decorators for parallel execution
@run_in_thread
def thread_function():
    # Function code here
    pass

@run_in_process
def process_function():
    # Function code here
    pass

# Use task manager directly
task = task_manager.submit_thread_task("task_id", my_function)
```

## Configuration

ApexAI-Core can be configured using environment variables or a `.env` file:

```
# Ollama API Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=codellama:instruct

# Agent Configuration
MAX_CYCLES=7
PROJECT_ROOT=apex_auto_project
LOG_LEVEL=INFO
```

## Examples

### Generate a Simple Function

```python
from apexai_core.agents import GODCodeAgentOllama

agent = GODCodeAgentOllama()
agent.recursive_build("Create a Python function to calculate the factorial of a number")
```

### Generate a FastAPI Application

```python
from apexai_core.agents import GODCodeAgentOllama

agent = GODCodeAgentOllama()
agent.recursive_build("Create a FastAPI application with a '/status' endpoint and a '/execute' endpoint that takes code and returns execution result")
```

### Use the GUI

```python
from apexai_core.agents import MultiModelAgent

agent = MultiModelAgent()
agent.launch_gui()
```

### Use Asynchronous Execution

```python
from apexai_core.agents import AsyncAgent
import asyncio

async def main():
    agent = AsyncAgent()
    await agent.recursive_build_async("Create a Python function to calculate the factorial of a number")

asyncio.run(main())
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

