#!/bin/bash

# Calculate NUM_CORES and NUM_WORKERS
NUM_CORES=$(python -c "import os; print(os.cpu_count())")
NUM_WORKERS=$(( (NUM_CORES / 2) + 1 ))

echo "Detected ${NUM_CORES} CPU cores."
echo "Starting the application with ${NUM_WORKERS} workers..."

# Start Gunicorn
gunicorn "src.main:entry()" \
    -w "${NUM_WORKERS}" \
    -b "${SERVER_ADDR}" \
    -k src.config.server_config.HeadlessUvicornWorker \
    --access-logfile -
