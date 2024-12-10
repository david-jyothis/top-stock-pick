FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set Python path to include the src directory
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV QUESTDB_HOST=questdb
ENV QUESTDB_PORT=8812

# Command to run the application
CMD ["python", "src/api_server.py"]