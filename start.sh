#!/bin/bash

# Inicia o script de commits automáticos em background
python commit_auto.py &

# Inicia o servidor com Gunicorn
gunicorn main:app