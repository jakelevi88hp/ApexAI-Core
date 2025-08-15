# FastAPI Integration

This tutorial will guide you through generating and running FastAPI applications with ApexAI-Core.

## Understanding FastAPI Detection

The GODCodeAgentOllama class includes a method called `should_run_with_uvicorn` that detects when code contains FastAPI or Starlette imports. When such imports are detected, the agent will run the code using Uvicorn instead of the regular Python interpreter.

## Generating a Simple FastAPI Application

Let's start by generating a simple FastAPI application:

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent()

# Generate a simple FastAPI application
agent.run_mission("Create a FastAPI application with a root endpoint that returns a greeting")
```

This will generate a file in the project directory with content similar to:

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

The agent will detect the FastAPI import and run the application using Uvicorn, which will start a web server at `http://0.0.0.0:8000`.

## Accessing the API Documentation

FastAPI automatically generates API documentation using Swagger UI and ReDoc:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

These interfaces provide interactive documentation for your API, allowing you to:
- View all available endpoints
- See request and response schemas
- Test endpoints directly from the browser

## Generating a More Complex API

Let's generate a more complex API with multiple endpoints and data models:

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent()

# Generate a more complex API
agent.run_mission("Create a FastAPI application for a book management system with CRUD operations")
```

This will generate a more complex application with:
- Data models for books, authors, etc.
- CRUD operations (Create, Read, Update, Delete)
- Validation using Pydantic models
- Error handling

## Running the API in Development Mode

When the agent runs a FastAPI application, it uses Uvicorn with the `--reload` flag, which enables hot reloading. This means that any changes you make to the code will be automatically detected and the server will restart.

If you want to run the application manually, you can use:

```bash
cd apex_auto_project
uvicorn module_1:app --reload
```

Replace `module_1` with the name of the generated module.

## Deploying the API

To deploy the generated API to a production environment, you can:

1. **Use Uvicorn directly**:
   ```bash
   uvicorn module_1:app --host 0.0.0.0 --port 8000
   ```

2. **Use Gunicorn with Uvicorn workers** (recommended for production):
   ```bash
   pip install gunicorn
   gunicorn module_1:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Use Docker**:
   ```dockerfile
   FROM python:3.9

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY module_1.py .

   CMD ["uvicorn", "module_1:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

   Build and run the Docker container:
   ```bash
   docker build -t my-fastapi-app .
   docker run -p 8000:8000 my-fastapi-app
   ```

## Adding Authentication

You can generate an API with authentication:

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent()

# Generate an API with authentication
agent.run_mission("Create a FastAPI application with JWT authentication for a book management system")
```

This will generate an application with:
- User registration and login endpoints
- JWT token generation and validation
- Protected endpoints that require authentication

## Adding Database Integration

You can generate an API with database integration:

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent()

# Generate an API with database integration
agent.run_mission("Create a FastAPI application with SQLAlchemy integration for a book management system")
```

This will generate an application with:
- SQLAlchemy models
- Database connection setup
- CRUD operations using the database

## Testing the API

You can generate tests for your API:

```python
from multi_model_agent import MultiModelAgent

# Create an agent
agent = MultiModelAgent()

# Generate tests for the API
agent.run_mission("Create pytest tests for a FastAPI book management system")
```

This will generate test files with:
- Test client setup
- Test cases for each endpoint
- Mocking of dependencies

## Troubleshooting

### Missing Dependencies

If you encounter missing dependencies when running the generated API, you can install them manually:

```bash
pip install fastapi uvicorn
```

For more complex APIs, you might need additional dependencies:

```bash
pip install fastapi uvicorn sqlalchemy pydantic python-jose[cryptography] passlib[bcrypt]
```

### Port Already in Use

If you encounter a "Port already in use" error, you can:

1. Find the process using the port:
   ```bash
   lsof -i :8000
   ```

2. Kill the process:
   ```bash
   kill <PID>
   ```

3. Or use a different port:
   ```bash
   uvicorn module_1:app --port 8001
   ```

### CORS Issues

If you're accessing the API from a web application and encounter CORS issues, you can add CORS middleware:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
```

## Next Steps

Now that you've learned how to generate and run FastAPI applications, you can:

- [Generate complex multi-module applications](recursive_generation.md)
- [Handle errors and improve code generation](error_handling.md)
- [Explore FastAPI application examples](../examples/fastapi_application.md)

