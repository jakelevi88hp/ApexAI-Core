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

# Launch the GUI
apexai gui

# Generate code without executing
apexai generate "Create a Python function to calculate the factorial of a number" --output factorial.py

# Show version information
apexai version
```

### Python API

```python
from apexai_core.agents import GODCodeAgentOllama, MultiModelAgent

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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

