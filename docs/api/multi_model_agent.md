# MultiModelAgent

The `MultiModelAgent` class is a wrapper for the `GODCodeAgentOllama` that provides model selection based on mission content and a graphical user interface (GUI) for user interaction.

## Class Definition

```python
class MultiModelAgent:
    def __init__(self, 
                 models=None, 
                 project_root=None, 
                 max_cycles=None, 
                 verbose=True):
        """
        Initialize the MultiModelAgent.
        
        Args:
            models (dict, optional): Dictionary mapping model types to model names.
                Defaults to {"code": "codellama:instruct", "general": "llama2"}.
            project_root (str, optional): Directory for storing generated modules.
                Passed to GODCodeAgentOllama.
            max_cycles (int, optional): Maximum recursive cycles for code generation.
                Passed to GODCodeAgentOllama.
            verbose (bool, optional): Enable verbose output logging. Defaults to True.
        """
```

## Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `models` | dict | Dictionary mapping model types to model names |
| `agent` | GODCodeAgentOllama | The underlying code generation agent |
| `verbose` | bool | Whether to enable verbose logging |

## Methods

### `choose_model`

```python
def choose_model(self, mission):
    """
    Choose a model based on mission content using keyword detection.
    
    Args:
        mission (str): The mission text to analyze
        
    Returns:
        str: The name of the selected model
    """
```

This method analyzes the mission text to determine whether it's a code-related task or a general task, and selects the appropriate model accordingly.

### `run_mission`

```python
def run_mission(self, mission, context=""):
    """
    Run a mission using the automatically chosen model.
    
    Args:
        mission (str): The task description for code generation
        context (str, optional): Additional context from previous iterations
        
    Returns:
        None
    """
```

This method:
1. Selects the appropriate model based on the mission content
2. Sets the model in the environment
3. Runs the mission using the underlying GODCodeAgentOllama

### `self_update`

```python
def self_update(self):
    """
    Pull the latest code from the current git repository.
    
    Returns:
        bool: True if update was successful, False otherwise
    """
```

This method updates the codebase by pulling the latest changes from the git repository.

### `generate_improvement`

```python
def generate_improvement(self, mission):
    """
    Generate code improvements using the active model.
    
    Args:
        mission (str): Description of the improvement to make
        
    Returns:
        str: Generated improvement code
    """
```

This method generates code improvements based on a mission description, using the underlying GODCodeAgentOllama.

### `launch_gui`

```python
def launch_gui(self):
    """
    Launch a Tkinter GUI with controls for mission execution and self-update.
    
    Returns:
        None
    """
```

This method launches a graphical user interface (GUI) for interacting with the agent. The GUI provides:
- A text entry for entering mission descriptions
- Buttons for running missions and self-updating
- A log display for viewing output
- A status bar for displaying the current status

## GUI Components

The GUI created by the `launch_gui` method includes the following components:

### Mission Input Section

- **Label**: "Enter mission description:"
- **Entry**: Text field for entering the mission description
- **Run Mission Button**: Button to execute the entered mission

### Log Output Section

- **ScrolledText**: Text area for displaying log messages
- **Custom Log Handler**: Redirects log messages to the text area

### Button Section

- **Run Mission Button**: Executes the entered mission
- **Self Update Button**: Updates the codebase from the git repository
- **Exit Button**: Closes the GUI

### Status Bar

- Displays the current status of the application (e.g., "Ready", "Running mission...")

## Custom Log Handler

The GUI includes a custom log handler that redirects log messages to the GUI:

```python
class TextHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        log_text.configure(state='normal')
        log_text.insert(tk.END, msg + '\n')
        log_text.see(tk.END)
        log_text.configure(state='disabled')
```

## Threading

The GUI uses threading to prevent freezing during long-running operations:

```python
import threading
thread = threading.Thread(target=lambda: self.run_mission(mission))
thread.daemon = True
thread.start()
```

## Usage Examples

### Basic Usage

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent()

# Run a mission
agent.run_mission("Create a Python function to calculate factorial")
```

### Custom Models

```python
from multi_model_agent import MultiModelAgent

# Create an agent with custom models
agent = MultiModelAgent(
    models={
        "code": "codellama:instruct",
        "general": "llama2",
        "creative": "mistral:instruct"
    }
)

# Run a mission
agent.run_mission("Create a Python function to calculate factorial")
```

### Launch GUI

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent()

# Launch the GUI
agent.launch_gui()
```

### Generate Improvements

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent()

# Generate improvements
improvement = agent.generate_improvement("Add error handling to the factorial function")
print(improvement)
```

### Self Update

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent()

# Update the codebase
if agent.self_update():
    print("Update successful!")
else:
    print("Update failed!")
```

## Model Selection Logic

The `choose_model` method uses the following logic to select a model:

1. Convert the mission text to lowercase
2. Check for code-related keywords:
   - "code", "script", "api", "function", "class", "data", "csv", "json", "algorithm", "program"
3. If any of these keywords are found, select the "code" model
4. Otherwise, select the "general" model

This allows the agent to automatically use the most appropriate model for the task at hand.

## Error Handling

The `MultiModelAgent` class includes comprehensive error handling:

- Initialization errors are logged and re-raised
- Model selection errors fall back to the general model
- Mission execution errors are logged and re-raised
- Self-update errors are logged and return False
- GUI errors are logged and displayed to the user

## Logging

The `MultiModelAgent` class uses the Python logging module for logging:

- Logs are written to both the console and a log file
- The log file is located at `multi_model_agent.log` in the same directory as the script
- The log level can be configured (defaults to INFO)
- When using the GUI, logs are also displayed in the log output section

