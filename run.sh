#!/bin/bash
# Script to run the Mindmap Agent application

cd mindmap_agent/app
echo "Starting Mindmap Agent on http://localhost:8000"
echo "Access the web interface at: http://localhost:8000/app"
echo "API documentation at: http://localhost:8000/docs"
echo ""
uvicorn main:app --reload --host 0.0.0.0 --port 8000
