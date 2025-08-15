# FastAPI Application

This example demonstrates how to generate a FastAPI application using the ApexAI-Core library.

## Generating a Simple FastAPI Application

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent(verbose=True)

# Generate a simple FastAPI application
agent.run_mission("Create a FastAPI application with a root endpoint that returns a greeting")
```

### Expected Output

The agent will generate a file in the project directory (default: `apex_auto_project/module_1.py`) with content similar to:

```python
from fastapi import FastAPI

app = FastAPI(title="Greeting API", description="A simple API that returns a greeting")

@app.get("/")
async def root():
    """
    Root endpoint that returns a greeting.
    
    Returns:
        dict: A greeting message
    """
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

The agent will also attempt to run the application using Uvicorn, which will start a web server at `http://0.0.0.0:8000`.

## Generating a Todo API

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent(verbose=True)

# Generate a Todo API
agent.run_mission("Create a FastAPI application for a Todo list with CRUD operations")
```

### Expected Output

The agent will generate a file in the project directory with content similar to:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI(title="Todo API", description="API for managing a Todo list")

# Define Todo model
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class Todo(TodoCreate):
    id: str

# In-memory database
todos = {}

@app.post("/todos/", response_model=Todo, status_code=201)
async def create_todo(todo: TodoCreate):
    """
    Create a new Todo item.
    
    Args:
        todo (TodoCreate): The Todo item to create
        
    Returns:
        Todo: The created Todo item
    """
    todo_id = str(uuid.uuid4())
    todos[todo_id] = Todo(id=todo_id, **todo.dict())
    return todos[todo_id]

@app.get("/todos/", response_model=List[Todo])
async def read_todos():
    """
    Get all Todo items.
    
    Returns:
        List[Todo]: A list of all Todo items
    """
    return list(todos.values())

@app.get("/todos/{todo_id}", response_model=Todo)
async def read_todo(todo_id: str):
    """
    Get a specific Todo item by ID.
    
    Args:
        todo_id (str): The ID of the Todo item
        
    Returns:
        Todo: The Todo item
        
    Raises:
        HTTPException: If the Todo item is not found
    """
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todos[todo_id]

@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: str, todo: TodoCreate):
    """
    Update a Todo item.
    
    Args:
        todo_id (str): The ID of the Todo item
        todo (TodoCreate): The updated Todo item
        
    Returns:
        Todo: The updated Todo item
        
    Raises:
        HTTPException: If the Todo item is not found
    """
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    todos[todo_id] = Todo(id=todo_id, **todo.dict())
    return todos[todo_id]

@app.delete("/todos/{todo_id}", status_code=204)
async def delete_todo(todo_id: str):
    """
    Delete a Todo item.
    
    Args:
        todo_id (str): The ID of the Todo item
        
    Raises:
        HTTPException: If the Todo item is not found
    """
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    del todos[todo_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Generating a Weather API

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent(verbose=True)

# Generate a Weather API
agent.run_mission("Create a FastAPI application for a Weather API that returns weather data for a given city")
```

### Expected Output

The agent will generate a file in the project directory with content similar to:

```python
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Optional
import random

app = FastAPI(title="Weather API", description="API for retrieving weather data")

# Define Weather model
class WeatherData(BaseModel):
    city: str
    temperature: float
    humidity: float
    wind_speed: float
    description: str

# Mock database of weather data
weather_db = {
    "new york": WeatherData(
        city="New York",
        temperature=22.5,
        humidity=65.0,
        wind_speed=10.2,
        description="Partly cloudy"
    ),
    "london": WeatherData(
        city="London",
        temperature=18.3,
        humidity=72.0,
        wind_speed=8.5,
        description="Rainy"
    ),
    "tokyo": WeatherData(
        city="Tokyo",
        temperature=28.1,
        humidity=55.0,
        wind_speed=5.8,
        description="Sunny"
    ),
    "sydney": WeatherData(
        city="Sydney",
        temperature=25.7,
        humidity=60.0,
        wind_speed=12.3,
        description="Clear"
    ),
    "paris": WeatherData(
        city="Paris",
        temperature=20.4,
        humidity=68.0,
        wind_speed=7.9,
        description="Cloudy"
    )
}

@app.get("/weather/{city}", response_model=WeatherData)
async def get_weather(city: str):
    """
    Get weather data for a specific city.
    
    Args:
        city (str): The name of the city
        
    Returns:
        WeatherData: Weather data for the city
        
    Raises:
        HTTPException: If the city is not found
    """
    city_lower = city.lower()
    if city_lower not in weather_db:
        raise HTTPException(status_code=404, detail=f"Weather data for {city} not found")
    return weather_db[city_lower]

@app.get("/weather/", response_model=Dict[str, WeatherData])
async def get_all_weather():
    """
    Get weather data for all cities.
    
    Returns:
        Dict[str, WeatherData]: Weather data for all cities
    """
    return weather_db

@app.get("/weather/random", response_model=WeatherData)
async def get_random_weather():
    """
    Get weather data for a random city.
    
    Returns:
        WeatherData: Weather data for a random city
    """
    city = random.choice(list(weather_db.keys()))
    return weather_db[city]

@app.get("/weather/search", response_model=Dict[str, WeatherData])
async def search_weather(
    min_temp: Optional[float] = Query(None, description="Minimum temperature"),
    max_temp: Optional[float] = Query(None, description="Maximum temperature"),
    description: Optional[str] = Query(None, description="Weather description")
):
    """
    Search for cities with specific weather conditions.
    
    Args:
        min_temp (float, optional): Minimum temperature
        max_temp (float, optional): Maximum temperature
        description (str, optional): Weather description
        
    Returns:
        Dict[str, WeatherData]: Weather data for cities matching the criteria
    """
    results = {}
    
    for city, data in weather_db.items():
        if min_temp is not None and data.temperature < min_temp:
            continue
        if max_temp is not None and data.temperature > max_temp:
            continue
        if description is not None and description.lower() not in data.description.lower():
            continue
        results[city] = data
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Testing the Generated API

Once the FastAPI application is generated and running, you can test it using:

1. **Web Browser**: Navigate to `http://localhost:8000/docs` to access the Swagger UI, which provides an interactive interface for testing the API.

2. **curl**: Use curl to make HTTP requests to the API:

   ```bash
   # Get all todos
   curl -X GET "http://localhost:8000/todos/"
   
   # Create a new todo
   curl -X POST "http://localhost:8000/todos/" \
     -H "Content-Type: application/json" \
     -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'
   ```

3. **Python Requests**: Use the requests library to make HTTP requests from Python:

   ```python
   import requests
   
   # Get all todos
   response = requests.get("http://localhost:8000/todos/")
   todos = response.json()
   print(todos)
   
   # Create a new todo
   new_todo = {
       "title": "Buy groceries",
       "description": "Milk, eggs, bread"
   }
   response = requests.post("http://localhost:8000/todos/", json=new_todo)
   created_todo = response.json()
   print(created_todo)
   ```

## Adding Authentication to the API

You can also generate an API with authentication:

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent(verbose=True)

# Generate an API with authentication
agent.run_mission("Create a FastAPI application with JWT authentication for a Todo list API")
```

This will generate a more complex application with user authentication using JWT tokens.

