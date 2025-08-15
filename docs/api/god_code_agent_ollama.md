# GODCodeAgentOllama

The `GODCodeAgentOllama` class is the core code generation agent in the ApexAI-Core library. It uses the Ollama API to generate Python code based on natural language descriptions and can recursively build multiple modules.

## Class Definition

```python
class GODCodeAgentOllama:
    def __init__(self, project_root=None, max_cycles=None, verbose=True):
        """
        Initialize the GODCodeAgentOllama.
        
        Args:
            project_root (str, optional): Directory for storing generated modules.
                Defaults to 'apex_auto_project' or value from environment variable.
            max_cycles (int, optional): Maximum recursive cycles for code generation.
                Defaults to 7 or value from environment variable.
            verbose (bool, optional): Enable verbose output logging. Defaults to True.
        """
```

## Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `project_root` | str | Directory where generated code modules are stored |
| `max_cycles` | int | Maximum number of recursive cycles for code generation |
| `verbose` | bool | Whether to enable verbose logging |

## Methods

### `ollama_generate`

```python
def ollama_generate(self, mission, context=""):
    """
    Generate code using the Ollama API.
    
    Args:
        mission (str): The mission description for code generation
        context (str, optional): Additional context from previous iterations
        
    Returns:
        str: The generated code
    """
```

This method sends a request to the Ollama API to generate code based on the provided mission description and context. It handles API errors and returns a fallback message if the API call fails.

### `recursive_build`

```python
def recursive_build(self, mission, context=""):
    """
    Recursively build Python modules based on a mission description.
    
    Args:
        mission (str): The mission description for code generation
        context (str, optional): Additional context from previous iterations
        
    Returns:
        None
    """
```

This is the main method for code generation. It:

1. Generates code using the Ollama API
2. Writes the code to a file
3. Executes the code
4. If the execution fails, it tries to fix the issues
5. Repeats the process for a maximum number of cycles

### `write_and_execute`

```python
def write_and_execute(self, code, filename):
    """
    Write code to a file and execute it.
    
    Args:
        code (str): The code to write and execute
        filename (str): The filename to write the code to
        
    Returns:
        tuple: (success, output) where success is a boolean indicating whether
               the execution was successful and output is the execution output
    """
```

This method writes the generated code to a file and executes it. It handles different execution methods based on the code content (regular Python or FastAPI/Uvicorn).

### `operator_review`

```python
def operator_review(self, code, filename):
    """
    Review code for syntax errors.
    
    Args:
        code (str): The code to review
        filename (str): The filename for error reporting
        
    Returns:
        bool: True if the code passes review, False otherwise
    """
```

This method performs a static analysis of the code to check for syntax errors before execution.

### `should_run_with_uvicorn`

```python
def should_run_with_uvicorn(self, code, filename):
    """
    Determine if the code should be run with Uvicorn.
    
    Args:
        code (str): The code to analyze
        filename (str): The filename for error reporting
        
    Returns:
        bool: True if the code should be run with Uvicorn, False otherwise
    """
```

This method checks if the code contains FastAPI or Starlette imports, which would require running with Uvicorn instead of regular Python execution.

### `auto_install_module`

```python
def auto_install_module(self, error_output):
    """
    Automatically install missing modules based on error output.
    
    Args:
        error_output (str): The error output from code execution
        
    Returns:
        None
    """
```

This method parses error output for ModuleNotFoundError exceptions and automatically installs the missing modules using pip.

### `destroyer_prune`

```python
def destroyer_prune(self, filename):
    """
    Delete a file if it exists.
    
    Args:
        filename (str): The filename to delete
        
    Returns:
        None
    """
```

This method deletes a file if it exists, used for cleaning up temporary files.

### `_clean_generated_code`

```python
def _clean_generated_code(self, raw_code):
    """
    Clean generated code by extracting Python code blocks.
    
    Args:
        raw_code (str): The raw code from the Ollama API
        
    Returns:
        str: The cleaned code
    """
```

This method extracts Python code blocks from the raw output of the Ollama API, removing markdown formatting and non-code content.

### `_execute_regular_python`

```python
def _execute_regular_python(self, filename, args=None):
    """
    Execute a Python file with the Python interpreter.
    
    Args:
        filename (str): The filename to execute
        args (list, optional): Command line arguments to pass to the script
        
    Returns:
        tuple: (success, output) where success is a boolean indicating whether
               the execution was successful and output is the execution output
    """
```

This method executes a Python file using the standard Python interpreter and returns the execution output.

### `_execute_with_uvicorn`

```python
def _execute_with_uvicorn(self, filename):
    """
    Execute a FastAPI/Starlette application with Uvicorn.
    
    Args:
        filename (str): The filename to execute
        
    Returns:
        tuple: (success, output) where success is a boolean indicating whether
               the execution was successful and output is the execution output
    """
```

This method executes a FastAPI or Starlette application using Uvicorn and returns the execution output.

## Usage Examples

### Basic Code Generation

```python
from god_code_agent_ollama import GODCodeAgentOllama

# Create an agent
agent = GODCodeAgentOllama(project_root="my_project")

# Generate code
agent.recursive_build("Create a Python function to calculate factorial")
```

### Single Code Generation

```python
from god_code_agent_ollama import GODCodeAgentOllama

# Create an agent
agent = GODCodeAgentOllama()

# Generate code
code = agent.ollama_generate("Create a Python function to calculate factorial")

# Write and execute the code
success, output = agent.write_and_execute(code, "factorial.py")
if success:
    print("Execution successful!")
    print(output)
else:
    print("Execution failed!")
    print(output)
```

### Automatic Module Installation

```python
from god_code_agent_ollama import GODCodeAgentOllama

# Create an agent
agent = GODCodeAgentOllama()

# Generate code that uses external modules
code = agent.ollama_generate("Create a Python script to make HTTP requests")

# Write and execute the code
success, output = agent.write_and_execute(code, "http_requests.py")
if not success and "ModuleNotFoundError" in output:
    # Automatically install missing modules
    agent.auto_install_module(output)
    
    # Try again
    success, output = agent.write_and_execute(code, "http_requests.py")
```

## Environment Variables

The `GODCodeAgentOllama` class uses the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PROJECT_ROOT` | Directory for storing generated modules | `"apex_auto_project"` |
| `MAX_CYCLES` | Maximum recursive cycles for code generation | `7` |
| `OLLAMA_BASE_URL` | Base URL for the Ollama API | `"http://localhost:11434"` |
| `OLLAMA_MODEL` | Model to use for code generation | `"codellama:instruct"` |

