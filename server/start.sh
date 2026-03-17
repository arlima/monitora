#!/bin/sh
PORT=$(python3 -c "import yaml; print(yaml.safe_load(open('/etc/monitora/monitora.yml'))['PORT'])")
gunicorn --bind 0.0.0.0:$PORT --workers 2 server:app &
python3 /app/bot.py
