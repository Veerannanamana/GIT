#!/bin/bash
export FLASK_APP=app.py
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:$PORT app:app
