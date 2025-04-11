#!/bin/bash

# Dá permissões de execução (localmente antes de fazer push):
# chmod +x start.sh

# Inicia o script de commits automáticos em background
python commit_auto.py &

# Inicia o servidor com Gunicorn
gunicorn main:app
