#!/bin/bash
pip install -r src/requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port $PORT