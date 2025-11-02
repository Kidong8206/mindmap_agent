#!/bin/bash
# Script to run the Mindmap Agent application

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

cd mindmap_agent/app
echo "Starting Mindmap Agent on http://localhost:8000"
echo "Access the web interface at: http://localhost:8000/app"
echo "API documentation at: http://localhost:8000/docs"
echo ""
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
