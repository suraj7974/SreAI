FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY sre_agent/ ./sre_agent/
COPY .env* ./

# Create incidents directory
RUN mkdir -p /app/incidents

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "uvicorn", "sre_agent.api:app", "--host", "0.0.0.0", "--port", "8000"]
