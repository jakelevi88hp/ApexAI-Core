# API Reference

This section provides detailed documentation for all the classes and methods in the ApexAI-Core library.

## Core Components

- [GODCodeAgentOllama](god_code_agent_ollama.md): A code generation agent that can recursively build Python modules based on natural language descriptions.
- [MultiModelAgent](multi_model_agent.md): A wrapper for GODCodeAgentOllama that supports multiple models and provides a GUI interface.

## Module Structure

The ApexAI-Core library is organized into the following modules:

```
ApexAI-Core/
├── god_code_agent_ollama.py  # Core code generation agent
└── multi_model_agent.py      # Multi-model wrapper with GUI
```

## Common Workflows

### Code Generation

The primary workflow for code generation involves:

1. Creating a MultiModelAgent instance
2. Running a mission with a natural language description
3. Retrieving the generated code from the project directory

```python
from multi_model_agent import MultiModelAgent

agent = MultiModelAgent(project_root="my_project")
agent.run_mission("Create a Python script to parse CSV files")

# Generated code will be in the my_project directory
```

### Using the GUI

The GUI provides a user-friendly interface for:

1. Entering mission descriptions
2. Running missions
3. Viewing output logs
4. Self-updating the codebase

```python
from multi_model_agent import MultiModelAgent

agent = MultiModelAgent()
agent.launch_gui()
```

### Model Selection

The MultiModelAgent automatically selects the appropriate model based on the mission content:

```python
from multi_model_agent import MultiModelAgent

agent = MultiModelAgent(
    models={
        "code": "codellama:instruct",
        "general": "llama2"
    }
)

# Will use the code model
agent.run_mission("Write a Python function to calculate factorial")

# Will use the general model
agent.run_mission("Explain the concept of artificial intelligence")
```

