#!/bin/bash
cd /home/debian/projects/kokoriko-backend
source venv/bin/activate
exec uvicorn app.main:app --host 127.0.0.1 --port 4223 --workers 4
