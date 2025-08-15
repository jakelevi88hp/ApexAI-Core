FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for Ollama
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Pull the required model
RUN ollama pull codellama:instruct

# Expose port for FastAPI
EXPOSE 8000

# Command to run the application
CMD ["python", "god_code_agent_ollama.py"]

