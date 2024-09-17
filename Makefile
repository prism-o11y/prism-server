.PHONY: set_env, check_env

include ./assets/env/.env

ENV_FILE_PATH := ./assets/env/.env

set_env: check_env
	@echo "Setting environment variables..."
	@bash scripts/set_env.sh

check_env:
	@echo "Checking for .env file..."
	@if [ ! -f ./assets/env/.env ]; then \
		echo ".env file not found! Please create it."; \
		exit 1; \
	else \
		echo ".env file found."; \
	fi
