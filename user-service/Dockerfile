# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    bash && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Copy the entrypoint script
COPY scripts/entrypoint.sh /entrypoint.sh

# Convert line endings to Unix format using sed
RUN sed -i 's/\r$//' /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Switch to a non-root user after setting up permissions
RUN addgroup --system appgroup && adduser --system appuser --ingroup appgroup

# Change ownership of the app directory and entrypoint script
RUN chown -R appuser:appgroup /app /entrypoint.sh

# Switch to the non-root user
USER appuser

# Expose the port Gunicorn will run on
EXPOSE 8000

# Define environment variables
ENV SERVER_ADDR=0.0.0.0:8000

# Set the entrypoint script as the container's entrypoint
ENTRYPOINT ["/entrypoint.sh"]
