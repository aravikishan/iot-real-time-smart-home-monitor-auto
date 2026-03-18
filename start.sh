#!/bin/bash
set -e
echo "Starting IoT Real-Time Smart Home Monitor..."
uvicorn app:app --host 0.0.0.0 --port 9022 --workers 1
