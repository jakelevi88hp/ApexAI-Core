# ApexAI-Core Documentation

Welcome to the ApexAI-Core documentation. This documentation provides detailed information about the ApexAI-Core library, its components, and how to use them.

## Overview

ApexAI-Core is a powerful AI automation stack for business operations. It provides a framework for building AI-powered applications using local language models through Ollama. The core components include:

- **GODCodeAgentOllama**: A code generation agent that can recursively build Python modules based on natural language descriptions.
- **MultiModelAgent**: A wrapper for GODCodeAgentOllama that supports multiple models and provides a GUI interface.

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/jakelevi88hp/ApexAI-Core.git
cd ApexAI-Core

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.com/) installed and running
- Required language models pulled (e.g., `ollama pull codellama:instruct`)

### Basic Usage

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent()

# Run a mission
agent.run_mission("Create a Python function to calculate the Fibonacci sequence")

# Launch the GUI
agent.launch_gui()
```

## Documentation Structure

- [API Reference](api/index.md): Detailed documentation of all classes and methods
- [Tutorials](tutorials/index.md): Step-by-step guides for common tasks
- [Examples](examples/index.md): Example code and use cases

## Contributing

Please see the [Contributing Guide](../CONTRIBUTING.md) for information on how to contribute to the project.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

