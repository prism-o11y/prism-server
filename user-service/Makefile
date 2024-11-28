.PHONY: start clean check_env

include assets/env/.env

NUM_CORES := $(shell python -c "import os; print(os.cpu_count())")
NUM_WORKERS := $(shell echo $$((($(NUM_CORES) / 2) + 1)))

ENV_FILE_PATH := assets/env/.env

start: check_env
	@echo "Starting the application with ${NUM_WORKERS} workers..."
	@gunicorn "src.main:entry()"\
	 -w $(NUM_WORKERS)\
	 -b ${SERVER_ADDR}\
	 -k src.config.server_config.HeadlessUvicornWorker\
	 --access-logfile -

clean:
	@echo "Cleaning up Python cache..."
	@find . \( -name '__pycache__' -o -name '*.pyc' -o -name '*.pyo' \) -delete

check_env:
	@echo "Checking for .env file..."
	@if [ ! -f assets/env/.env ]; then \
		echo ".env file not found! Please create it."; \
		exit 1; \
	else \
		echo ".env file found."; \
	fi
