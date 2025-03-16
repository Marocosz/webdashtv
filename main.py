# Importando as bibliotecas necessárias
from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF

# Inicializando o aplicativo Flask
app = Flask(__name__, template_folder=os.path.dirname(__file__))

# Definindo os nomes dos arquivos que serão utilizados
EXCEL_FILE = "dados.xlsx"
PDF_FILE = "dashboard.pdf"

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
@app.route('/download_excel')
def download_excel():
    # Retorna o arquivo Excel como anexo para o usuário baixar
    return send_file(EXCEL_FILE, as_attachment=True)

@app.route('/gerar_texto_mensagem', methods=['POST'])
def gerar_texto_mensagem():
    verificar_arquivo()
    df = pd.read_excel(EXCEL_FILE)

    if df.empty:
        return jsonify({"message": "Nenhum dado disponível para gerar o texto."})
    
    # Filtra os dados do dia atual
    data_atual = datetime.now().strftime('%Y-%m-%d')
    df['DataHora'] = pd.to_datetime(df['DataHora'])
    df_dia = df[df['DataHora'].dt.strftime('%Y-%m-%d') == data_atual]

    if df_dia.empty:
        return jsonify({"message": "Nenhum dado para o dia de hoje."})
    
    # Gerando o texto
    texto_mensagem = ""
    for index, row in df_dia.iterrows():
        hora = row['DataHora'].strftime('%H:%M')
        teor = row['Teor']
        texto = row['Texto']
        
        # Formatação do texto
        texto_mensagem += f"⏰{hora}\n"
        texto_mensagem += f"{'🔴' if teor == 'Negativo' else '⚪' if teor == 'Neutro' else '🟢'}{teor}\n"
        texto_mensagem += f"ℹ️{texto}\n\n"
    
    return jsonify({"texto": texto_mensagem})

# Rota para gerar e baixar o dashboard em PDF
@app.route('/gerar_dashboard_pdf')
def gerar_dashboard_pdf():
    # Verifica se o arquivo Excel existe
    verificar_arquivo()
    
    # Carrega os dados do arquivo Excel
    df = pd.read_excel(EXCEL_FILE)
    
    # Se não houver dados, retorna uma mensagem informando que não é possível gerar o dashboard
    if df.empty:
        return "Nenhum dado disponível para gerar o dashboard."
    
    # Gerando o gráfico de distribuição de teor das matérias
    plt.figure(figsize=(6, 4))  # Define o tamanho da figura
    # Conta a quantidade de matérias por teor e plota um gráfico de barras
    df["Teor"].value_counts().plot(kind="bar", color=["red", "gray", "green"])
    plt.title("Distribuição de Teor das Matérias")  # Título do gráfico
    plt.xlabel("Teor")  # Rótulo do eixo X
    plt.ylabel("Quantidade")  # Rótulo do eixo Y
    plt.xticks(rotation=0)  # Alinha as etiquetas do eixo X
    plt.savefig("grafico.png")  # Salva o gráfico como imagem
    plt.close()  # Fecha a figura gerada para evitar sobrecarga de memória
    
    # Criando o PDF para o dashboard
    pdf = FPDF()  # Inicializando o objeto PDF
    pdf.set_auto_page_break(auto=True, margin=15)  # Ativando quebra de página automática
    pdf.add_page()  # Adiciona uma página ao PDF
    pdf.set_font("Arial", "B", 16)  # Define a fonte do texto
    pdf.cell(200, 10, "Dashboard de Matérias", ln=True, align="C")  # Título centralizado na página
    pdf.ln(10)  # Linha em branco
    pdf.image("grafico.png", x=30, w=150)  # Insere a imagem do gráfico no PDF
    pdf.ln(10)  # Linha em branco após o gráfico
    
    # Salva o PDF gerado no arquivo
    pdf.output(PDF_FILE)
    
    # Retorna o arquivo PDF para o usuário baixar
    return send_file(PDF_FILE, as_attachment=True)

# Inicia o servidor Flask no modo de depuração
if __name__ == '__main__':
    app.run(debug=True)
