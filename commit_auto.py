import time
import subprocess
import os
import sys

GITHUB_USERNAME = "Marocosz"
GITHUB_REPO = "webdashtv"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_DIR = os.getcwd()

print(f"📁 Diretório atual: {REPO_DIR}")
print(GITHUB_TOKEN)

# Verifica se o token está disponível
if not GITHUB_TOKEN:
    print("❌ ERRO: GITHUB_TOKEN não está definido nas variáveis de ambiente.")
    sys.exit(1)

print("✅ Script de commit automático iniciado.")
print(f"📁 Diretório atual: {REPO_DIR}")

while True:
    time.sleep(300)  # Executa a cada ~5 minutos

    try:
        os.chdir(REPO_DIR)

        # Verifica se é um repositório Git
        if not os.path.exists(os.path.join(REPO_DIR, ".git")):
            print("⚠️ Diretório não é um repositório Git. Inicializando...")
            subprocess.run(["git", "init"], check=True)

        # Configura nome e e-mail globalmente
        subprocess.run(["git", "config", "--global", "user.name", GITHUB_USERNAME], check=True)
        subprocess.run(["git", "config", "--global", "user.email", f"{GITHUB_USERNAME}@users.noreply.github.com"], check=True)

        # Verifica se já existe remote
        repo_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{GITHUB_REPO}.git"
        remote_check = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True)

        if "origin" not in remote_check.stdout:
            print("🔗 Adicionando repositório remoto...")
            subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
        else:
            print("🔄 Atualizando URL do repositório remoto...")
            subprocess.run(["git", "remote", "set-url", "origin", repo_url], check=True)

        # Busca branches
        subprocess.run(["git", "fetch", "origin"], check=True)

        # Verifica a branch atual
        branch_output = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
        current_branch = branch_output.stdout.strip()

        if current_branch == "HEAD":
            print("📌 Repositório está em detached HEAD. Criando/mudando para 'main'...")
            subprocess.run(["git", "checkout", "-B", "main"], check=True)
        elif current_branch != "main":
            print(f"📌 Atualmente na branch '{current_branch}', mudando para 'main'...")
            subprocess.run(["git", "checkout", "main"], check=True)

        # Puxa últimas mudanças (ignora histórico diferente)
        subprocess.run(["git", "pull", "origin", "main", "--allow-unrelated-histories"], check=True)

        # Adiciona somente se houver mudanças
        subprocess.run(["git", "add", "dados.xlsx"], check=True)
        diff_check = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if diff_check.returncode == 0:
            print("🟡 Nenhuma mudança detectada no arquivo. Aguardando próximo ciclo...")
            continue

        # Commit e push
        subprocess.run(["git", "commit", "-m", "Atualização automática do arquivo Excel"], check=True)
        subprocess.run(["git", "push", "--set-upstream", "origin", "main", "--force"], check=True)

        print("✅ Arquivo atualizado e push realizado com sucesso!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar comando Git: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
