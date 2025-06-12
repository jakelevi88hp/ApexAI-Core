# GODCodeAgentOllama

A Python-based code generation and execution framework that uses the Ollama API to recursively generate, execute, and refine Python scripts for specified tasks.

## Features

- **Recursive Code Generation**: Automatically generates Python code based on natural language descriptions
- **Automatic Execution**: Executes generated code and provides feedback for improvements
- **FastAPI Support**: Automatically detects and runs FastAPI applications using uvicorn
- **Auto-dependency Installation**: Automatically installs missing Python modules
- **Configurable**: Supports configuration via environment variables
- **Comprehensive Logging**: Uses structured logging with configurable levels
- **Error Handling**: Robust error handling for API calls and code execution
- **Extensible**: Modular design for easy extension and customization

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jakelevi88hp/ApexAI-Core.git
cd ApexAI-Core
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure Ollama is running locally on port 11434 (or configure a different endpoint)

## Configuration

The agent can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API base URL |
| `OLLAMA_MODEL` | `codellama:instruct` | Ollama model to use for code generation |
| `PROJECT_ROOT` | `apex_auto_project` | Directory for storing generated modules |
| `MAX_CYCLES` | `7` | Maximum number of recursive cycles |

Example:
```bash
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="codellama:instruct"
export PROJECT_ROOT="my_project"
export MAX_CYCLES="5"
```

## Usage

### Basic Usage

```python
from god_code_agent_ollama import GODCodeAgentOllama

# Initialize the agent
agent = GODCodeAgentOllama(max_cycles=4, verbose=True)

# Define your mission
mission = "Build a FastAPI server with a '/status' endpoint and a '/execute' endpoint that takes code and returns execution result."

# Run the recursive build
agent.recursive_build(mission)
```

### Advanced Configuration

```python
from god_code_agent_ollama import GODCodeAgentOllama

# Custom configuration
agent = GODCodeAgentOllama(
    project_root="my_custom_project",
    max_cycles=3,
    verbose=True
)

# Complex mission with context
mission = "Create a REST API with user authentication and data persistence"
context = "Use SQLite for database and JWT for authentication"

agent.recursive_build(mission, context)
```

### API Usage

You can also use individual methods for specific tasks:

```python
from god_code_agent_ollama import GODCodeAgentOllama

agent = GODCodeAgentOllama()

# Generate code only
code = agent.ollama_generate("Create a simple calculator function")

# Review code
is_valid = agent.operator_review(code, "calculator.py")

# Execute code
success, output = agent.write_and_execute(code, "calculator.py")
```

## Architecture

The framework consists of several key components:

### Core Components

1. **Code Generator** (`ollama_generate`): Interfaces with Ollama API to generate Python code
2. **Code Executor** (`write_and_execute`): Executes generated code with proper error handling
3. **Code Reviewer** (`operator_review`): Reviews generated code for basic quality criteria
4. **Dependency Manager** (`auto_install_module`): Automatically installs missing dependencies
5. **Recursive Builder** (`recursive_build`): Orchestrates the recursive improvement process

### Workflow

1. **Generation Phase**: Generate Python code based on the mission description
2. **Execution Phase**: Write code to file and execute it
3. **Review Phase**: Evaluate the code and execution results
4. **Iteration Phase**: If successful, enhance the code in the next cycle
5. **Cleanup Phase**: Remove failed code files

## Error Handling

The framework includes comprehensive error handling:

- **API Errors**: Graceful handling of Ollama API failures with fallback responses
- **Execution Errors**: Automatic module installation for missing dependencies
- **File System Errors**: Proper error messages for file I/O operations
- **Timeout Handling**: Configurable timeouts for long-running operations

## Testing

Run the test suite to ensure everything is working correctly:

```bash
python -m unittest test_god_code_agent_ollama.py -v
```

The test suite includes:
- Unit tests for all major components
- Integration tests for complete workflows
- Mocked external dependencies for reliable testing

## Logging

The framework uses Python's built-in logging module with structured logging:

```python
import logging

# Configure logging level
logging.getLogger('god_code_agent_ollama').setLevel(logging.DEBUG)
```

Log levels:
- `DEBUG`: Detailed information for debugging
- `INFO`: General information about the execution
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for failed operations

## Examples

### Example 1: Simple Web Server

```python
from god_code_agent_ollama import GODCodeAgentOllama

agent = GODCodeAgentOllama(max_cycles=3)
mission = "Create a simple HTTP server that serves 'Hello World' on port 8000"
agent.recursive_build(mission)
```

### Example 2: Data Processing Script

```python
from god_code_agent_ollama import GODCodeAgentOllama

agent = GODCodeAgentOllama(max_cycles=4)
mission = "Create a script that reads a CSV file, processes the data, and generates a summary report"
context = "Use pandas for data manipulation and create visualizations"
agent.recursive_build(mission, context)
```

### Example 3: API Client

```python
from god_code_agent_ollama import GODCodeAgentOllama

agent = GODCodeAgentOllama(max_cycles=5)
mission = "Build a REST API client that can fetch weather data and cache the results"
agent.recursive_build(mission)
```

## Limitations

- Requires a running Ollama instance with code generation models
- Generated code quality depends on the underlying LLM model
- Limited to Python code generation
- Execution environment must have necessary permissions for file operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with appropriate tests
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the BSD 3-Clause License. See the LICENSE file for details.

## Troubleshooting

### Common Issues

1. **Ollama Connection Error**: Ensure Ollama is running and accessible at the configured URL
2. **Module Installation Failures**: Check pip permissions and internet connectivity
3. **File Permission Errors**: Ensure the application has write permissions to the project directory
4. **Timeout Issues**: Adjust timeout values for slow operations or large code generation tasks

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from god_code_agent_ollama import GODCodeAgentOllama
agent = GODCodeAgentOllama(verbose=True)
```

## Support

For support, please open an issue on the GitHub repository or contact the maintainers.