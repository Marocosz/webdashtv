# Importando as bibliotecas necessárias
from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF

# Inicializando o aplicativo Flask
app = Flask(__name__, template_folder=os.path.dirname(__file__))

# Dicionário com os canais e seus respectivos jornais
jornais = {
    "Globo": ["Inter TV Rural", "Bom Dia Rio", "Bom Dia Brasil", "RJ TV 1", "RJ TV 2"],
    "Record": ["Balanço Geral", "RJ No Ar TV Record", "RJ Record"]
}


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
@app.route('/baixar_excel')
def download_excel():
    return send_file(EXCEL_FILE, as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", download_name="dados.xlsx")

# Função para verificar a existência do arquivo (exemplo de implementação)
def verificar_arquivo():
    # Verifica se o arquivo existe e pode ser lido
    pass  # Implementar a lógica de verificação

@app.route('/gerar_texto_mensagem', methods=['POST'])
def gerar_texto_mensagem():
    # Obtém os dados enviados pelo frontend (data escolhida)
    data_recebida = request.json.get('data')  # Obtém a data do corpo da requisição
    
    if not data_recebida:
        return jsonify({"message": "Data não fornecida."})

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

    # Geração do texto
    texto_mensagem = f"*CLIPPING | {data_escolhida.strftime('%d-%m-%y')}*\n\n\n\n"
    
    # Agrupa as notícias por jornal
    jornais = df_dia['Jornal'].unique()
    for jornal in jornais:
        texto_mensagem += f"*📺{jornal}*\n\n"
        
        df_jornal = df_dia[df_dia['Jornal'] == jornal]
        for _, row in df_jornal.iterrows():
            hora = row['DataHora'].strftime('%H:%M')
            teor = row['Teor']
            texto = row['Texto']
            
            # Define o ícone baseado no teor da notícia
            icone_teor = "🔴" if teor.lower() == "negativa" else "⚪" if teor.lower() == "neutra" else "🟢"
            
            texto_mensagem += f"⏰*{hora}*\n"
            texto_mensagem += f"*{icone_teor}{teor}*\n"
            texto_mensagem += f"ℹ️{texto}\n\n"
            
        texto_mensagem += f"-----------------------------------\n\n"

    # Retorna o texto gerado para o frontend
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

@app.route('/get_jornais', methods=['POST'])
def get_jornais():
    canal = request.json.get("canal")
    return jsonify(jornais.get(canal, []))

# Inicia o servidor Flask no modo de depuração
if __name__ == '__main__':
    app.run(debug=True)