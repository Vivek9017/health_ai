# Use official Python image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y curl

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pull llama3 model
RUN ollama pull llama3

# Expose port
EXPOSE 10000

# Start Ollama service + Flask app
CMD ollama serve & gunicorn app:app --bind 0.0.0.0:10000