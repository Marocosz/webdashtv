from flask import Flask, render_template, request, send_file
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF

app = Flask(__name__)
EXCEL_FILE = "dados.xlsx"
PDF_FILE = "dashboard.pdf"

# Verifica se o arquivo Excel existe, se não, cria um novo
def verificar_arquivo():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=["Canal", "Jornal", "Tema", "DataHora", "Teor", "Texto"])
        df.to_excel(EXCEL_FILE, index=False)

@app.route('/')
def index():
    return render_template("Index.html")

@app.route('/process', methods=['POST'])
def process():
    verificar_arquivo()
    
    # Coletando dados do formulário
    canal = request.form['canal']
    jornal = request.form['jornal']
    tema = request.form['tema']
    datahora = request.form['datahora']
    teor = request.form['teor']
    texto = request.form['texto']
    
    # Criando um DataFrame com os novos dados
    novo_dado = pd.DataFrame([[canal, jornal, tema, datahora, teor, texto]],
                              columns=["Canal", "Jornal", "Tema", "DataHora", "Teor", "Texto"])
    
    # Carregar arquivo existente e adicionar nova linha
    df = pd.read_excel(EXCEL_FILE)
    df = pd.concat([df, novo_dado], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    
    return "Dados salvos com sucesso!"

@app.route('/download_excel')
def download_excel():
    return send_file(EXCEL_FILE, as_attachment=True)

@app.route('/gerar_dashboard_pdf')
def gerar_dashboard_pdf():
    verificar_arquivo()
    df = pd.read_excel(EXCEL_FILE)
    
    if df.empty:
        return "Nenhum dado disponível para gerar o dashboard."
    
    # Gerando gráfico de quantidade por teor
    plt.figure(figsize=(6,4))
    df["Teor"].value_counts().plot(kind="bar", color=["red", "gray", "green"])
    plt.title("Distribuição de Teor das Matérias")
    plt.xlabel("Teor")
    plt.ylabel("Quantidade")
    plt.xticks(rotation=0)
    plt.savefig("grafico.png")
    plt.close()
    
    # Criando o PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Dashboard de Matérias", ln=True, align="C")
    pdf.ln(10)
    pdf.image("grafico.png", x=30, w=150)
    pdf.ln(10)
    
    # Salvando o PDF
    pdf.output(PDF_FILE)
    
    return send_file(PDF_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
