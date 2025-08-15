FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Install the package
RUN pip install --no-cache-dir -e .

# Create a non-root user
RUN useradd -m apexai
USER apexai

# Create project directory
RUN mkdir -p /home/apexai/apex_auto_project
ENV PROJECT_ROOT=/home/apexai/apex_auto_project

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_BASE_URL=http://ollama:11434
ENV OLLAMA_MODEL=codellama:instruct
ENV MAX_CYCLES=7

# Expose ports for FastAPI apps
EXPOSE 8000

# Command to run the CLI
ENTRYPOINT ["apexai"]
CMD ["--help"]

