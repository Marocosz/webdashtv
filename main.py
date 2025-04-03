# Importando as bibliotecas necessárias
from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from flask_cors import CORS
import subprocess
import atexit

os.system("apt-get update && apt-get install -y fonts-liberation ttf-mscorefonts-installer")
# Inicializando o aplicativo Flask
app = Flask(__name__, template_folder='templates')

CORS(app)  # Habilita CORS para evitar bloqueios

# Dicionário com os canais e seus respectivos jornais
jornais = {
    "Globo": ["Inter TV Rural", "Bom Dia Inter", "Bom Dia Rio", "Bom Dia Brasil", "RJ TV 1", "RJ TV 2"],
    "Record": ["Balanço Geral", "RJ No Ar TV Record", "RJ Record"]
}


# Definindo os nomes dos arquivos que serão utilizados
EXCEL_FILE = "dados.xlsx"
PDF_FILE = "dashboard.pdf"

# Configuração do repositório
GITHUB_USERNAME = "Marocosz"
GITHUB_REPO = "webdashtv"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

subprocess.run(['git', 'config', 'user.name', 'Marocosz'], check=True)
subprocess.run(['git', 'config', 'user.email', 'ditanixplayer@gmail.com'], check=True)

print('--------------------------------------------------------------')
print("Diretório atual:", os.getcwd())

# Caminho do repositório dentro do Render
REPO_DIR = os.getcwd()

def git_commit_and_push():
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

        
# Função que verifica se o arquivo Excel já existe, se não, cria um novo com a estrutura básica
def verificar_arquivo():
    # Se o arquivo não existir, cria um novo DataFrame e salva como Excel
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=["Canal", "Jornal", "Tema", "DataHora", "Teor", "Texto"])
        df.to_excel(EXCEL_FILE, index=False)

# Rota para a página inicial, onde o usuário pode preencher o formulário
@app.route('/')
def index():
    
    return render_template("index.html")  # Renderiza o arquivo HTML (Index.html) para o usuário

# Rota para processar os dados enviados pelo formulário
@app.route('/process', methods=['POST'])
def process():
    # Verifica se o arquivo Excel existe ou cria um novo
    verificar_arquivo()
    
    # Coletando os dados enviados pelo formulário na requisição POST
    canal = request.form['canal']
    jornal = request.form['jornal']
    tema = request.form['tema']
    datahora = request.form['datahora']
    teor = request.form['teor']
    texto = request.form['texto']
    
    # Criando um novo DataFrame com os dados recebidos
    novo_dado = pd.DataFrame([[canal, jornal, tema, datahora, teor, texto]],
                              columns=["Canal", "Jornal", "Tema", "DataHora", "Teor", "Texto"])
    
    # Carregando o arquivo Excel existente e concatenando o novo dado
    df = pd.read_excel(EXCEL_FILE)
    df = pd.concat([df, novo_dado], ignore_index=True)  # Ignora o índice para adicionar como nova linha
    df.to_excel(EXCEL_FILE, index=False)  # Salva o DataFrame atualizado no arquivo Excel
    
    # Retorna uma resposta JSON confirmando que os dados foram adicionados

    return jsonify({"message": "Dados adicionados com sucesso!"})

# Rota para fazer o download do arquivo Excel
@app.route('/baixar_excel')
def download_excel():
    return send_file(EXCEL_FILE, as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", download_name="dados.xlsx")


@app.route('/gerar_texto_mensagem', methods=['POST'])
def gerar_texto_mensagem():
    # Obtém os dados enviados pelo frontend (data escolhida e período)
    data_recebida = request.json.get('data')  # Obtém a data do corpo da requisição
    periodo_recebido = request.json.get('periodo')  # Obtém o período do corpo da requisição

    # Definindo os jornais por período
    jornais_manha = ["Bom Dia Brasil", "Bom Dia Rio", "Bom Dia Inter", "Inter TV Rural", "RJ No Ar TV Record"]
    jornais_tarde = ["RJ TV 1", "Balanço Geral"]
    jornais_noite = ["RJ TV 2", "RJ Record"]

    if not data_recebida:
        return jsonify({"message": "Data não fornecida."})

    if not periodo_recebido:
        return jsonify({"message": "Período não fornecido."})

    # Verifica se o período é válido
    if periodo_recebido not in ['Manha', 'Tarde', 'Noite']:
        return jsonify({"message": "Período inválido. Escolha entre 'Manhã', 'Tarde' ou 'Noite'."})

    # Verifica se a data fornecida está no formato correto
    try:
        data_escolhida = datetime.strptime(data_recebida, '%Y-%m-%d').date()  # Formato: 'YYYY-MM-DD'
    except ValueError:
        return jsonify({"message": "Data inválida. Use o formato YYYY-MM-DD."})

    # Chama a função para verificar a existência de arquivos necessários
    verificar_arquivo()

    # Lê os dados do arquivo Excel
    df = pd.read_excel(EXCEL_FILE)

    # Verifica se o DataFrame está vazio
    if df.empty:
        return jsonify({"message": "Nenhum dado disponível para gerar o texto."})

    # Converte a coluna 'DataHora' para datetime (se ainda não estiver)
    df['DataHora'] = pd.to_datetime(df['DataHora'])

    # Filtra os dados para pegar apenas os registros da data escolhida
    df_dia = df[df['DataHora'].dt.date == data_escolhida]

    # Verifica se há dados para a data escolhida
    if df_dia.empty:
        return jsonify({"message": f"Nenhum dado para a data {data_escolhida.strftime('%d-%m-%Y')}."})

    # Determina os jornais de acordo com o período escolhido
    if periodo_recebido == 'Manha':
        jornais_periodo = jornais_manha
    elif periodo_recebido == 'Tarde':
        jornais_periodo = jornais_tarde
    else:  # periodo_recebido == 'Noite'
        jornais_periodo = jornais_noite

    # Geração do texto com o título modificando de acordo com o período
    texto_mensagem = f"*CLIPPING | {data_escolhida.strftime('%d-%m-%y')} - {periodo_recebido}*\n\n\n\n"
    
    # Agrupa as notícias por jornal e filtra apenas os jornais do período
    for jornal in jornais_periodo:
        if jornal in df_dia['Jornal'].values:
            texto_mensagem += f"*📺{jornal}*\n\n"
            
            df_jornal = df_dia[df_dia['Jornal'] == jornal]
            for _, row in df_jornal.iterrows():
                hora = row['DataHora'].strftime('%H:%M')
                teor = row['Teor']
                texto = row['Texto']
                
                # Define o ícone baseado no teor da notícia
                icone_teor = "🔴" if teor.lower() == "negativo" else "⚪" if teor.lower() == "neutro" else "🟢"
                
                texto_mensagem += f"⏰*{hora}*\n"
                texto_mensagem += f"*{icone_teor}{teor}*\n"
                texto_mensagem += f"ℹ️{texto}\n\n"
            
            texto_mensagem += f"-----------------------------------\n\n"
    
    texto_mensagem += f"https://clipping.intecmidia.com.br/index.php/apps/files/files/596?dir=/1-RECORTES%20DO%20DIA\n"

    # Retorna o texto gerado para o frontend
    return jsonify({"texto": texto_mensagem})

# Rota para gerar e baixar o dashboard em PDF
@app.route('/gerar_dashboard_pdf', methods=['GET', 'POST'])
def gerar_dashboard_pdf():
    # Verifica se o arquivo Excel existe
    verificar_arquivo()
    
    # Carregar os dados do arquivo Excel
    df = pd.read_excel('dados.xlsx')

    # Converter a coluna 'DataHora' para o tipo datetime
    df['DataHora'] = pd.to_datetime(df['DataHora'])

    # Filtrar os dados do mês desejado
    num_mes = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 
            6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}


    mes_desejado = request.json.get('mes')  # Alterar para o mês desejado
    mes_desejado = int(mes_desejado)
    df_mes = df[df['DataHora'].dt.month == mes_desejado]
    
    print(df_mes)

    # Verificar se há dados para o mês especificado
    if df_mes.empty:
        print(f"Não há dados para o mês {mes_desejado}.")
        return jsonify({"erro": f"Não há dados disponíveis para o mês {mes_desejado}."}), 400
    else:
        # Criar um arquivo PDF para salvar os gráficos
        with PdfPages('graficos.pdf') as pdf:
            
            # Criar o gráfico de pizza para os valores 'Teor'
            df_teor_filtrado = df_mes[df_mes['Teor'].isin(['Negativo', 'Positivo'])]
            contagem_teor_filtrado = df_teor_filtrado['Teor'].value_counts()
            
            # Função para formatar os rótulos com número absoluto e porcentagem
            def func(pct, allvals):
                absolute = int(pct / 100. * sum(allvals))
                return f"{absolute}\n({pct:.1f}%)"
            
            # Criar a figura e o eixo para o gráfico de pizza
            fig, ax = plt.subplots(figsize=(6, 6))
            
            # Definir cores personalizadas para o gráfico
            cores_pizza = ['#03C04A', '#F40000']  # verde para "Positivo" e Vermelho para "Negativo"
            
            # Criar o gráfico de pizza
            wedges, texts, autotexts = ax.pie(
                contagem_teor_filtrado.values,
                labels=contagem_teor_filtrado.index,
                autopct=lambda pct: func(pct, contagem_teor_filtrado.values),
                startangle=90,
                colors=cores_pizza,
                textprops={'fontsize': 12, 'fontweight': 'bold', 'color': 'black'},
                wedgeprops={'edgecolor': 'white', 'linewidth': 2}  # Adicionando a linha branca entre as fatias
            )
                    
            # Alterar a cor e a formatação dos textos dentro do gráfico de pizza
            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontweight("bold")
            
            # Adicionar título formatado ao gráfico de pizza
            ax.set_title(f"Distribuição dos valores 'Negativo' e 'Positivo' - {num_mes[mes_desejado]}",
                        fontname="Arial", fontsize=16, fontweight='bold', pad=20)
            
            # Ajustar o layout e salvar o gráfico no PDF
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            
            # Função para criar gráficos de barras formatados
            def criar_grafico_barra(dados, titulo, xlabel):
                fig, ax = plt.subplots(figsize=(8, 6))
                
                # Criar gráfico de barras com cor personalizada
                barras = dados.plot(kind='bar', color='#4169E1', ax=ax)
                
                # Adicionar rótulos de valores no topo das barras
                for p in barras.patches:
                    ax.text(p.get_x() + p.get_width() / 2, p.get_height() + 0.2,
                            str(int(p.get_height())),
                            ha='center', fontsize=12, fontweight='bold', fontname="Arial", color='black')
                
                # Adicionar título e rótulos formatados
                ax.set_title(titulo, fontname="Arial", fontsize=16, fontweight='bold', pad=20)
                ax.set_xlabel(xlabel, fontname="Arial", fontsize=12)
                
                ax.set_xlabel("")  # Remove o texto "Tema" ou "Jornal" abaixo do gráfico
                
                # Rotacionar os nomes das categorias para melhor visualização
                ax.xaxis.set_tick_params(rotation=45)
                
                # Ajustar os rótulos das categorias no eixo X
                ax.set_xticks(range(len(dados.index)))
                ax.set_xticklabels(dados.index, ha='right', fontsize=10, fontname="Arial")
                
                # Remover linhas de grade e eixos desnecessários
                ax.yaxis.set_visible(False)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                
                # Ajustar layout e salvar o gráfico no PDF
                plt.tight_layout()
                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)
            
            # Criar gráficos de barras para os temas e jornais mais mencionados
            criar_grafico_barra(df_mes['Tema'].value_counts(),
                                f"Temas mais mencionados - {num_mes[mes_desejado]}",
                                "Tema")
            
            criar_grafico_barra(df_mes['Jornal'].value_counts(),
                                f"Jornais que mais mencionaram - {num_mes[mes_desejado]}",
                                "Jornal")
            
            # Criar uma figura com os três gráficos juntos
            fig, axs = plt.subplots(1, 3, figsize=(18, 6))
            
            # Adicionar o gráfico de pizza ao primeiro eixo
            wedges, texts, autotexts = axs[0].pie(
                contagem_teor_filtrado.values, labels=contagem_teor_filtrado.index,
                autopct=lambda pct: func(pct, contagem_teor_filtrado.values), startangle=90,
                colors=cores_pizza, textprops={'fontsize': 10, 'fontweight': 'bold', 'color': 'black'},
                wedgeprops={'edgecolor': 'white', 'linewidth': 2}
            )
            
            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontweight("bold")
            
            axs[0].set_title("Teor", fontname="Arial", fontsize=12, fontweight='bold')
            
            # Criar gráficos de barras para "Temas" e "Jornais"
            for ax, dados, titulo, xlabel in zip(
                    axs[1:], [df_mes['Tema'].value_counts(), df_mes['Jornal'].value_counts()],
                    ["Temas", "Jornais"], ["Tema", "Jornal"]):
                barras = dados.plot(kind='bar', color='#4169E1', ax=ax)
                
                for p in barras.patches:
                    ax.text(p.get_x() + p.get_width() / 2, p.get_height() + 0.2,
                            str(int(p.get_height())),
                            ha='center', fontsize=10, fontweight='bold', fontname="Arial", color='black')
                
                ax.set_title(titulo, fontname="Arial", fontsize=12, fontweight='bold')
                ax.set_xlabel(xlabel, fontname="Arial", fontsize=10)
                ax.xaxis.set_tick_params(rotation=45)
                ax.set_xticklabels(dados.index, ha='right', fontsize=10, fontname="Arial")
                ax.yaxis.set_visible(False)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.set_xlabel("")  # Remove o texto "Tema" ou "Jornal" abaixo do gráfico
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
        
        print("Os gráficos foram salvos em 'graficos.pdf'.")
    
    # Verificar se o arquivo foi gerado corretamente antes de retornar
    if os.path.exists('graficos.pdf'):
        return send_file('graficos.pdf', as_attachment=True, mimetype="application/pdf", download_name="relatorio.pdf")
    else:
        return "Erro ao gerar o arquivo PDF.", 500

@app.route('/get_jornais', methods=['POST'])
def get_jornais():
    canal = request.json.get("canal")
    return jsonify(jornais.get(canal, []))

@app.route('/delete_last_rows', methods=['POST'])
def delete_last_rows():
    try:
        data = request.json
        num_linhas = int(data.get("num_linhas", 0))

        if not os.path.exists(EXCEL_FILE):
            return jsonify({"message": "Arquivo Excel não encontrado."}), 404

        # Carregar os dados
        df = pd.read_excel(EXCEL_FILE)

        # Verificar se há linhas suficientes para excluir
        if num_linhas > len(df):
            return jsonify({"message": f"Erro: O arquivo tem apenas {len(df)} linhas disponíveis."}), 400

        # Excluir as últimas linhas
        df = df.iloc[:-num_linhas]

        # Salvar o novo arquivo
        df.to_excel(EXCEL_FILE, index=False)

        return jsonify({"message": f"{num_linhas} linhas excluídas com sucesso!"})

    except Exception as e:
        return jsonify({"message": f"Erro ao excluir linhas: {str(e)}"}), 500
    

# Inicia o servidor Flask no modo de depuração
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)