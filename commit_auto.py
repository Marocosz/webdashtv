import time
import os
import base64
import requests
from datetime import datetime
import hashlib

GITHUB_USERNAME = "Marocosz"
GITHUB_REPO = "webdashtv"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
FILE_PATH = "dados.xlsx"
BRANCH = "main"

API_URL = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{FILE_PATH}"
ultimo_hash = None
ultima_execucao = None  # Para garantir que só rode uma vez por dia

def log(msg):
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{hora}] {msg}")

def hash_do_arquivo(content):
    return hashlib.sha256(content).hexdigest()

def upload_excel():
    global ultimo_hash
    if not GITHUB_TOKEN:
        log("❌ ERRO: GITHUB_TOKEN não está definido nas variáveis de ambiente.")
        return

    try:
        with open(FILE_PATH, "rb") as f:
            content = f.read()

        hash_atual = hash_do_arquivo(content)
        if hash_atual == ultimo_hash:
            log("ℹ️ Nenhuma alteração detectada no conteúdo. Pulando envio.")
            return

        encoded = base64.b64encode(content).decode("utf-8")
        r_get = requests.get(API_URL, headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        })
        sha = r_get.json().get("sha") if r_get.status_code == 200 else None

        payload = {
            "message": f"Atualização automática: {datetime.now().isoformat()}",
            "content": encoded,
            "branch": BRANCH
        }
        if sha:
            payload["sha"] = sha

        r_put = requests.put(API_URL, headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }, json=payload)

        if r_put.status_code in [200, 201]:
            log("✅ Excel enviado com sucesso para o GitHub!")
            ultimo_hash = hash_atual
        else:
            log(f"❌ Erro no envio: {r_put.status_code} - {r_put.text}")

    except Exception as e:
        log(f"❌ Erro inesperado: {e}")

log("🟢 Iniciando agendamento diário às 03:00...")
while True:
    agora = datetime.now()
    if agora.hour == 3 and agora.minute == 0:
        hoje = agora.date()
        if ultima_execucao != hoje:
            log("⏰ São 03:00! Iniciando upload...")
            upload_excel()
            ultima_execucao = hoje
        else:
            log("ℹ️ Upload já realizado hoje. Aguardando próximo dia...")
    time.sleep(60)  # Checa uma vez por minuto
