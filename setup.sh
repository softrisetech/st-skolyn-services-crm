#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
  echo "Copying .env.example to .env..."
  cp .env.example .env
else
  echo ".env file already exists. Skipping copy."
fi

# Load .env file into the script
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
else
  echo ".env file not found. Exiting..."
  exit 1
fi

#Give permissions to directories
# chmod -R 777 ./bootstrap/cache

#Remove existing containers
docker compose down

#Build containers
docker compose build

#Start containers
docker compose up -d

# Run migration command
docker exec -it skoyln_services_crm sh -c "python manage.py migrate && python manage.py permission_seed"
