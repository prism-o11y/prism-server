#!/bin/bash

ENV_FILE=${1:-"assets/env/.env"}

if [ ! -f "$ENV_FILE" ]; then
  echo ".env file not found!"
  exit 1
fi

export_env() {
  while IFS='=' read -r key value || [ -n "$key" ]; do
    if [[ ! $key =~ ^# ]] && [[ -n "$key" ]]; then
      key=$(echo "$key" | xargs)
      value=$(echo "$value" | xargs)
      
      export "$key=$value"
      echo "Exported: $key"
    fi
  done < "$ENV_FILE"
}

export_env
