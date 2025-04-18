#!/bin/bash

# Check if running with Docker
if [ "$1" == "docker" ]; then
    echo "Starting with Docker..."
    docker compose up -d
    echo "API is running at http://localhost:5000"
    exit 0
fi

# Otherwise run locally
echo "Starting locally..."
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py 