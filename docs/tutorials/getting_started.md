# Getting Started with ApexAI-Core

This tutorial will guide you through setting up ApexAI-Core and running your first code generation mission.

## Prerequisites

Before you begin, make sure you have the following installed:

- Python 3.8 or higher
- [Ollama](https://ollama.com/) - for running local language models
- Git - for cloning the repository

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/jakelevi88hp/ApexAI-Core.git
cd ApexAI-Core
```

### Step 2: Create a Virtual Environment (Optional but Recommended)

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install the Package in Development Mode

```bash
pip install -e .
```

### Step 5: Pull Required Models with Ollama

Make sure Ollama is running, then pull the required models:

```bash
ollama pull codellama:instruct
ollama pull llama2
```

## Configuration

ApexAI-Core can be configured using environment variables or by passing parameters to the constructor.

### Environment Variables

Create a `.env` file in the root directory of the project with the following content:

```
# Ollama API Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=codellama:instruct

# Agent Configuration
MAX_CYCLES=7
PROJECT_ROOT=apex_auto_project
```

### Constructor Parameters

Alternatively, you can pass parameters to the constructor:

```python
from multi_model_agent import MultiModelAgent

agent = MultiModelAgent(
    models={"code": "codellama:instruct", "general": "llama2"},
    project_root="my_project",
    max_cycles=5,
    verbose=True
)
```

## Your First Code Generation Mission

Let's run a simple code generation mission to create a Python function that calculates the factorial of a number.

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent()

# Run a mission
agent.run_mission("Create a Python function to calculate the factorial of a number")
```

This will:
1. Select the appropriate model (in this case, the code model)
2. Generate code using the Ollama API
3. Write the code to a file in the project directory
4. Execute the code to verify it works

## Examining the Generated Code

The generated code will be stored in the project directory specified by the `project_root` parameter or the `PROJECT_ROOT` environment variable. By default, this is `apex_auto_project`.

```bash
# List the generated files
ls -la apex_auto_project

# View the content of the first module
cat apex_auto_project/module_1.py
```

The generated code should contain a function to calculate the factorial of a number, similar to:

```python
def factorial(n):
    """
    Calculate the factorial of a number.
    
    Args:
        n (int): The number to calculate the factorial of
        
    Returns:
        int: The factorial of n
    """
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

# Test the function
print(factorial(5))  # Should print 120
```

## Next Steps

Now that you've successfully run your first code generation mission, you can:

- [Learn how to use the GUI](using_the_gui.md)
- [Configure and use custom models](custom_models.md)
- [Generate and run FastAPI applications](fastapi_integration.md)

## Troubleshooting

### Ollama Connection Issues

If you encounter connection issues with Ollama, make sure:

1. Ollama is running (`ollama serve`)
2. The Ollama API is accessible at the URL specified in the `OLLAMA_BASE_URL` environment variable
3. The required models are pulled (`ollama pull codellama:instruct`)

### Missing Dependencies

If you encounter missing dependencies, you can install them manually:

```bash
pip install <package_name>
```

Alternatively, the agent will attempt to automatically install missing dependencies when it encounters a `ModuleNotFoundError`.

### Permission Issues

If you encounter permission issues when writing to the project directory, make sure you have write permissions for the directory specified by the `project_root` parameter or the `PROJECT_ROOT` environment variable.

