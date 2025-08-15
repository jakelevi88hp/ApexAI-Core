# Simple Code Generation

This example demonstrates how to generate a simple Python function using the ApexAI-Core library.

## Generating a Factorial Function

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent(verbose=True)

# Generate a factorial function
agent.run_mission("Create a Python function to calculate the factorial of a number")
```

### Expected Output

The agent will generate a file in the project directory (default: `apex_auto_project/module_1.py`) with content similar to:

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

## Generating a Fibonacci Function

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent(verbose=True)

# Generate a Fibonacci function
agent.run_mission("Create a Python function to calculate the nth Fibonacci number")
```

### Expected Output

The agent will generate a file in the project directory with content similar to:

```python
def fibonacci(n):
    """
    Calculate the nth Fibonacci number.
    
    Args:
        n (int): The position in the Fibonacci sequence
        
    Returns:
        int: The nth Fibonacci number
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# Test the function
print(fibonacci(10))  # Should print 55
```

## Generating a Prime Number Checker

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent(verbose=True)

# Generate a prime number checker
agent.run_mission("Create a Python function to check if a number is prime")
```

### Expected Output

The agent will generate a file in the project directory with content similar to:

```python
def is_prime(n):
    """
    Check if a number is prime.
    
    Args:
        n (int): The number to check
        
    Returns:
        bool: True if the number is prime, False otherwise
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

# Test the function
for i in range(20):
    print(f"{i} is {'prime' if is_prime(i) else 'not prime'}")
```

## Generating a String Reversal Function

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent(verbose=True)

# Generate a string reversal function
agent.run_mission("Create a Python function to reverse a string")
```

### Expected Output

The agent will generate a file in the project directory with content similar to:

```python
def reverse_string(s):
    """
    Reverse a string.
    
    Args:
        s (str): The string to reverse
        
    Returns:
        str: The reversed string
    """
    return s[::-1]

# Test the function
print(reverse_string("Hello, World!"))  # Should print "!dlroW ,olleH"
```

## Generating a Temperature Conversion Function

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent(verbose=True)

# Generate a temperature conversion function
agent.run_mission("Create Python functions to convert between Celsius and Fahrenheit")
```

### Expected Output

The agent will generate a file in the project directory with content similar to:

```python
def celsius_to_fahrenheit(celsius):
    """
    Convert Celsius to Fahrenheit.
    
    Args:
        celsius (float): Temperature in Celsius
        
    Returns:
        float: Temperature in Fahrenheit
    """
    return (celsius * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit):
    """
    Convert Fahrenheit to Celsius.
    
    Args:
        fahrenheit (float): Temperature in Fahrenheit
        
    Returns:
        float: Temperature in Celsius
    """
    return (fahrenheit - 32) * 5/9

# Test the functions
celsius = 25
fahrenheit = celsius_to_fahrenheit(celsius)
print(f"{celsius}°C = {fahrenheit}°F")

fahrenheit = 98.6
celsius = fahrenheit_to_celsius(fahrenheit)
print(f"{fahrenheit}°F = {celsius}°C")
```

## Using Direct Code Generation

You can also generate code directly without writing it to a file or executing it:

```python
from god_code_agent_ollama import GODCodeAgentOllama

# Create an agent
agent = GODCodeAgentOllama(verbose=True)

# Generate code directly
code = agent.ollama_generate("Create a Python function to calculate the area of a circle")
print(code)
```

### Expected Output

The agent will generate code similar to:

```python
def calculate_circle_area(radius):
    """
    Calculate the area of a circle.
    
    Args:
        radius (float): The radius of the circle
        
    Returns:
        float: The area of the circle
    """
    import math
    return math.pi * radius ** 2

# Test the function
print(calculate_circle_area(5))  # Should print approximately 78.54
```

