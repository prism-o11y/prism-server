.PHONY: start, clean, check_env

include assets/env/.env

NUM_CORES := $(shell python -c "import os; print(os.cpu_count())")
NUM_WORKERS := $(shell echo $$((2 * $(NUM_CORES) + 1)))

ENV_FILE_PATH := assets/env/.env

start: check_env
	@gunicorn src.main:entry -b ${SERVER_ADDR} -w $(NUM_WORKERS) -k uvicorn.workers.UvicornWorker --access-logfile -

clean:
	@find . \( -name '__pycache__' -o -name '*.pyc' -o -name '*.pyo' \) -delete

check_env:
	@echo "Checking .env file..."
	@if [ ! -f assets/env/.env ]; then \
		echo ".env file not found!"; \
		exit 1; \
	else \
		echo ".env file found..."; \
	fi