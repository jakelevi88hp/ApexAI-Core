# Custom Models

This tutorial will guide you through configuring and using custom models with the MultiModelAgent class.

## Understanding Model Selection

The MultiModelAgent class automatically selects the appropriate model based on the mission content:

- **Code Model**: Used for code-related tasks (e.g., "Write a Python function...")
- **General Model**: Used for general tasks (e.g., "Explain the concept of...")

The model selection is performed by the `choose_model` method, which analyzes the mission text for code-related keywords.

## Default Models

By default, the MultiModelAgent uses the following models:

```python
models = {
    "code": "codellama:instruct",
    "general": "llama2",
}
```

These models must be available in your Ollama installation. You can pull them using:

```bash
ollama pull codellama:instruct
ollama pull llama2
```

## Configuring Custom Models

You can configure custom models by passing a dictionary to the MultiModelAgent constructor:

```python
from multi_model_agent import MultiModelAgent

# Create an agent with custom models
agent = MultiModelAgent(
    models={
        "code": "codellama:7b",
        "general": "mistral:7b",
    }
)
```

Make sure the models you specify are available in your Ollama installation. You can pull them using:

```bash
ollama pull codellama:7b
ollama pull mistral:7b
```

## Adding Additional Model Types

You can add additional model types beyond the default "code" and "general" types:

```python
from multi_model_agent import MultiModelAgent

# Create an agent with additional model types
agent = MultiModelAgent(
    models={
        "code": "codellama:7b",
        "general": "mistral:7b",
        "creative": "llama2:13b",
        "math": "phind-codellama:34b",
    }
)
```

However, to use these additional model types, you'll need to modify the `choose_model` method to select them based on appropriate criteria.

## Customizing Model Selection Logic

To customize the model selection logic, you can subclass the MultiModelAgent class and override the `choose_model` method:

```python
from multi_model_agent import MultiModelAgent

class CustomModelAgent(MultiModelAgent):
    def choose_model(self, mission):
        """
        Choose a model based on mission content using custom logic.
        
        Args:
            mission (str): The mission text to analyze
            
        Returns:
            str: The name of the selected model
        """
        mission_lower = mission.lower()
        
        # Check for code-related keywords
        code_keywords = ("code", "script", "api", "function", "class", 
                         "data", "csv", "json", "algorithm", "program")
        if any(word in mission_lower for word in code_keywords):
            return self.models.get("code", self.models["general"])
        
        # Check for creative-related keywords
        creative_keywords = ("story", "poem", "creative", "write", "imagine")
        if any(word in mission_lower for word in creative_keywords):
            return self.models.get("creative", self.models["general"])
        
        # Check for math-related keywords
        math_keywords = ("math", "calculate", "equation", "formula", "solve")
        if any(word in mission_lower for word in math_keywords):
            return self.models.get("math", self.models["general"])
        
        # Default to general model
        return self.models["general"]
```

You can then use your custom agent class:

```python
# Create a custom agent
agent = CustomModelAgent(
    models={
        "code": "codellama:7b",
        "general": "mistral:7b",
        "creative": "llama2:13b",
        "math": "phind-codellama:34b",
    }
)

# Run missions with different model types
agent.run_mission("Write a Python function to calculate factorial")  # Uses code model
agent.run_mission("Write a poem about artificial intelligence")      # Uses creative model
agent.run_mission("Solve the quadratic equation x^2 + 5x + 6 = 0")   # Uses math model
agent.run_mission("Explain the concept of quantum computing")        # Uses general model
```

## Using Environment Variables

You can also set the model using environment variables:

```bash
# Set the model in the environment
export OLLAMA_MODEL=codellama:7b

# Run your Python script
python my_script.py
```

In your script:

```python
from multi_model_agent import MultiModelAgent

# Create an agent (will use OLLAMA_MODEL from environment)
agent = MultiModelAgent()

# Run a mission
agent.run_mission("Create a Python function to calculate factorial")
```

## Dynamically Changing Models

You can dynamically change the model during runtime:

```python
from multi_model_agent import MultiModelAgent
import os

# Create an agent
agent = MultiModelAgent()

# Run a mission with the default model
agent.run_mission("Create a Python function to calculate factorial")

# Change the model
os.environ["OLLAMA_MODEL"] = "mistral:7b"

# Run another mission with the new model
agent.run_mission("Explain the concept of quantum computing")
```

## Model Performance Considerations

Different models have different performance characteristics:

- Larger models (e.g., 13B, 34B) generally produce better results but require more memory and are slower
- Smaller models (e.g., 7B) are faster and require less memory but may produce lower quality results
- Specialized models (e.g., CodeLlama) perform better on specific tasks (e.g., code generation)

Choose models based on your hardware capabilities and quality requirements.

## Troubleshooting

### Model Not Found

If you encounter a "Model not found" error, make sure:

1. The model is pulled in Ollama: `ollama pull <model_name>`
2. The model name is spelled correctly
3. Ollama is running: `ollama serve`

### Out of Memory

If you encounter an out of memory error:

1. Try using a smaller model (e.g., 7B instead of 13B)
2. Close other applications to free up memory
3. If using GPU, make sure you have enough VRAM

### Slow Performance

If the model is running slowly:

1. Try using a smaller model
2. Make sure you have sufficient CPU/GPU resources
3. Check if other processes are consuming resources

## Next Steps

Now that you've learned how to configure and use custom models, you can:

- [Generate and run FastAPI applications](fastapi_integration.md)
- [Handle errors and improve code generation](error_handling.md)
- [Generate complex multi-module applications](recursive_generation.md)

