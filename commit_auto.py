import time
import subprocess
import os

GITHUB_USERNAME = "Marocosz"
GITHUB_REPO = "webdashtv"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_DIR = os.getcwd()

while True:
    time.sleep(800)  # A cada 13 min
    try:
        os.chdir(REPO_DIR)

        # Verifica se é um repositório Git
        if not os.path.exists(os.path.join(REPO_DIR, ".git")):
            print("⚠️ Diretório não é um repositório Git. Inicializando...")
            subprocess.run(["git", "init"], check=True)

        # Configura usuário e e-mail do Git (caso não tenha sido configurado)
        subprocess.run(["git", "config", "--global", "user.name", GITHUB_USERNAME], check=True)
        subprocess.run(["git", "config", "--global", "user.email", f"{GITHUB_USERNAME}@users.noreply.github.com"], check=True)

        # Verifica se o remote origin já existe
        remote_check = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True)
        repo_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{GITHUB_REPO}.git"

        if "origin" not in remote_check.stdout:
            print("🔗 Adicionando repositório remoto...")
            subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
        else:
            print("🔄 Atualizando URL do repositório remoto...")
            subprocess.run(["git", "remote", "set-url", "origin", repo_url], check=True)

        # Busca as branches remotas para evitar conflitos
        subprocess.run(["git", "fetch", "origin"], check=True)

        # Verifica a branch atual
        branch_output = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
        current_branch = branch_output.stdout.strip()

        if current_branch == "HEAD":
            print("📌 O repositório está em detached HEAD. Tentando mudar para a branch 'main'...")
            subprocess.run(["git", "checkout", "-B", "main"], check=True)
        elif current_branch != "main":
            print(f"📌 Atualmente na branch '{current_branch}', mudando para 'main'...")
            subprocess.run(["git", "checkout", "main"], check=True)

        # Puxar as últimas mudanças para evitar conflitos
        subprocess.run(["git", "pull", "origin", "main", "--allow-unrelated-histories"], check=True)

        # Adicionar mudanças no Excel
        subprocess.run(["git", "add", "dados.xlsx"], check=True)

        # Criar commit com mensagem automática
        subprocess.run(["git", "commit", "-m", "Atualização automática do arquivo Excel"], check=True)

        # Enviar mudanças ao GitHub
        subprocess.run(["git", "push", "--set-upstream", "origin", "main", "--force"], check=True)

        print("✅ Arquivo atualizado e push realizado com sucesso!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar comando Git: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

