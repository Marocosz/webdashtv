#!/bin/bash

echo "🟢 Iniciando commit_auto.py em background..."
python commit_auto.py &

echo "🚀 Iniciando servidor Gunicorn..."
gunicorn main:app

wait
