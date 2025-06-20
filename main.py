# Importando as bibliotecas necessárias
import os
import io
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# --- Carregando Variáveis de Ambiente ---
load_dotenv()

# --- Configuração do App Flask e do Banco de Dados ---
app = Flask(__name__, template_folder='templates')
CORS(app)

database_uri = os.environ.get('DATABASE_URL', 'sqlite:///local_dev.db')
if database_uri.startswith("postgres://"):
    database_uri = database_uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Dicionário de Jornais (Lógica Local) ---
jornais = {
    "Globo": ["Inter TV Rural", "Bom Dia Inter", "Bom Dia Rio", "Bom Dia Brasil", "RJ TV 1", "RJ TV 2"],
    "Record": ["Balanço Geral", "RJ No Ar TV Record", "RJ Record"]
}

# --- Modelo de Dados (ORM) ---
class Noticia(db.Model):
    __tablename__ = 'noticia'
    id = db.Column(db.Integer, primary_key=True)
    canal = db.Column(db.String(100), nullable=False)
    jornal = db.Column(db.String(100), nullable=False)
    tema = db.Column(db.String(200), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    teor = db.Column(db.String(50), nullable=False)
    texto = db.Column(db.Text, nullable=False)

    # Adiciona um método para serializar o objeto para JSON
    def to_dict(self):
        return {
            'id': self.id,
            'canal': self.canal,
            'jornal': self.jornal,
            'tema': self.tema,
            'data_hora': self.data_hora.strftime('%Y-%m-%dT%H:%M'),
            'teor': self.teor,
            'texto': self.texto
        }

    def __repr__(self):
        return f'<Noticia {self.id}: {self.jornal} - {self.tema}>'

# --- Rotas da API ---

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/get_jornais', methods=['POST'])
def get_jornais():
    canal = request.json.get("canal")
    lista_jornais = jornais.get(canal, [])
    return jsonify(lista_jornais)

@app.route('/process', methods=['POST'])
def process():
    try:
        data_hora_obj = datetime.strptime(request.form['datahora'], '%Y-%m-%dT%H:%M')
        nova_noticia = Noticia(
            canal=request.form['canal'],
            jornal=request.form['jornal'],
            tema=request.form['tema'],
            data_hora=data_hora_obj,
            teor=request.form['teor'],
            texto=request.form['texto']
        )
        db.session.add(nova_noticia)
        db.session.commit()
        return jsonify({"message": "Dados adicionados com sucesso!"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao processar dados: {e}")
        return jsonify({"message": "Erro ao salvar os dados."}), 500
        
# --- NOVAS ROTAS PARA EDIÇÃO E EXCLUSÃO ---

@app.route('/get_recent_data', methods=['GET'])
def get_recent_data():
    """Busca os 20 registros mais recentes do banco de dados."""
    try:
        # Ordena por data_hora descendente e pega os 20 primeiros
        registros = Noticia.query.order_by(Noticia.data_hora.desc()).limit(20).all()
        return jsonify([r.to_dict() for r in registros])
    except Exception as e:
        print(f"Erro ao buscar dados recentes: {e}")
        return jsonify({"error": "Não foi possível buscar os dados."}), 500

@app.route('/update_data/<int:id>', methods=['PUT'])
def update_data(id):
    """Atualiza um registro existente no banco de dados."""
    try:
        noticia = Noticia.query.get_or_404(id)
        data = request.json

        # Atualiza os campos da notícia com os novos dados
        noticia.canal = data.get('canal', noticia.canal)
        noticia.jornal = data.get('jornal', noticia.jornal)
        noticia.tema = data.get('tema', noticia.tema)
        if 'data_hora' in data:
            noticia.data_hora = datetime.strptime(data['data_hora'], '%Y-%m-%dT%H:%M')
        noticia.teor = data.get('teor', noticia.teor)
        noticia.texto = data.get('texto', noticia.texto)

        db.session.commit()
        return jsonify({"message": f"Registro {id} atualizado com sucesso!"})
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar registro {id}: {e}")
        return jsonify({"error": "Não foi possível atualizar o registro."}), 500

@app.route('/delete_data/<int:id>', methods=['DELETE'])
def delete_data(id):
    """Deleta um registro específico do banco de dados."""
    try:
        noticia = Noticia.query.get_or_404(id)
        db.session.delete(noticia)
        db.session.commit()
        return jsonify({"message": f"Registro {id} deletado com sucesso!"})
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao deletar registro {id}: {e}")
        return jsonify({"error": "Não foi possível deletar o registro."}), 500


# --- Rotas Antigas e de Relatórios (sem alterações) ---

@app.route('/baixar_excel')
def download_excel():
    try:
        df = pd.read_sql_table('noticia', db.engine)
        output = io.BytesIO()
        df.to_excel(output, index=False, sheet_name='Dados')
        output.seek(0)
        return send_file(output, as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", download_name="dados_completos.xlsx")
    except Exception as e:
        print(f"Erro ao gerar Excel: {e}")
        return jsonify({"message": "Erro ao gerar o arquivo Excel."}), 500

@app.route('/gerar_texto_mensagem', methods=['POST'])
def gerar_texto_mensagem():
    data_recebida = request.json.get('data')
    periodo_recebido = request.json.get('periodo')
    if not data_recebida or not periodo_recebido:
        return jsonify({"message": "Data ou período não fornecido."}), 400

    try:
        data_escolhida = datetime.strptime(data_recebida, '%Y-%m-%d').date()
        registros = Noticia.query.filter(db.func.date(Noticia.data_hora) == data_escolhida).all()

        if not registros:
            return jsonify({"message": f"Nenhum dado para a data {data_escolhida.strftime('%d-%m-%Y')}."})

        df_dia = pd.DataFrame([r.to_dict() for r in registros])

        jornais_manha = ["Bom Dia Brasil", "Bom Dia Rio", "Bom Dia Inter", "Inter TV Rural", "RJ No Ar TV Record"]
        jornais_tarde = ["RJ TV 1", "Balanço Geral"]
        jornais_noite = ["RJ TV 2", "RJ Record"]
        jornais_periodo = jornais_manha if periodo_recebido == 'Manha' else jornais_tarde if periodo_recebido == 'Tarde' else jornais_noite

        texto_mensagem = f"*CLIPPING | {data_escolhida.strftime('%d-%m-%y')} - {periodo_recebido}*\n\n\n\n"
        for jornal_nome in jornais_periodo:
            df_jornal = df_dia[df_dia['jornal'] == jornal_nome]
            if not df_jornal.empty:
                texto_mensagem += f"*📺{jornal_nome}*\n\n"
                for _, row in df_jornal.iterrows():
                    icone_teor = "🔴" if row['teor'].lower() == "negativo" else "⚪" if row['teor'].lower() == "neutro" else "🟢"
                    # Converte a string de data_hora de volta para objeto datetime para formatar
                    hora_formatada = datetime.strptime(row['data_hora'], '%Y-%m-%dT%H:%M').strftime('%H:%M')
                    texto_mensagem += f"⏰*{hora_formatada}*\n"
                    texto_mensagem += f"*{icone_teor}{row['teor']}*\n"
                    texto_mensagem += f"ℹ️{row['texto']}\n\n"
                texto_mensagem += "-----------------------------------\n\n"
        
        texto_mensagem += "https://clipping.intecmidia.com.br/index.php/apps/files/files/596?dir=/1-RECORTES%20DO%20DIA\n"
        return jsonify({"texto": texto_mensagem})

    except Exception as e:
        print(f"Erro ao gerar texto: {e}")
        return jsonify({"message": "Ocorreu um erro ao gerar o texto."}), 500

@app.route('/gerar_dashboard_pdf', methods=['POST'])
def gerar_dashboard_pdf():
    mes_desejado = request.json.get('mes')
    if not mes_desejado:
        return jsonify({"erro": "Mês não fornecido."}), 400

    try:
        mes_desejado = int(mes_desejado)
        registros_mes = Noticia.query.filter(db.extract('month', Noticia.data_hora) == mes_desejado).all()

        if not registros_mes:
            return jsonify({"erro": f"Não há dados disponíveis para o mês {mes_desejado}."}), 404
        
        df_mes = pd.DataFrame([r.to_dict() for r in registros_mes])
        num_mes = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}

        pdf_buffer = io.BytesIO()
        with PdfPages(pdf_buffer) as pdf:
            df_teor_filtrado = df_mes[df_mes['teor'].isin(['Negativo', 'Positivo'])]
            if not df_teor_filtrado.empty:
                contagem_teor_filtrado = df_teor_filtrado['teor'].value_counts()
                
                # CORREÇÃO: Mapeia as cores aos valores para garantir a ordem correta
                color_map = {'Positivo': '#03C04A', 'Negativo': '#F40000'}
                cores_pizza = [color_map.get(teor, '#cccccc') for teor in contagem_teor_filtrado.index]

                def func(pct, allvals):
                    absolute = int(pct / 100. * sum(allvals))
                    return f"{absolute}\n({pct:.1f}%)"

                fig, ax = plt.subplots(figsize=(6, 6))
                wedges, texts, autotexts = ax.pie(
                    contagem_teor_filtrado.values, labels=contagem_teor_filtrado.index,
                    autopct=lambda pct: func(pct, contagem_teor_filtrado.values),
                    startangle=90, colors=cores_pizza, # Usa a lista de cores corrigida
                    textprops={'fontsize': 12, 'fontweight': 'bold', 'color': 'black'},
                    wedgeprops={'edgecolor': 'white', 'linewidth': 2}
                )
                for autotext in autotexts:
                    autotext.set_color("white")
                ax.set_title(f"Distribuição de Teor - {num_mes[mes_desejado]}", fontsize=16, fontweight='bold', pad=20)
                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)

            def criar_grafico_barra(dados, titulo, ax):
                if dados.empty: return
                barras = dados.plot(kind='bar', color='#4169E1', ax=ax)
                for p in barras.patches:
                    ax.text(p.get_x() + p.get_width() / 2, p.get_height() + 0.2,
                            str(int(p.get_height())),
                            ha='center', fontsize=10, fontweight='bold', color='black')
                ax.set_title(titulo, fontsize=12, fontweight='bold')
                ax.set_xlabel("")
                ax.tick_params(axis='x', rotation=45)
                ax.set_xticklabels(dados.index, ha='right')
                ax.yaxis.set_visible(False)
                for spine in ['top', 'right', 'left', 'bottom']:
                    ax.spines[spine].set_visible(False)

            fig_tema, ax_tema = plt.subplots(figsize=(8, 6))
            criar_grafico_barra(df_mes['tema'].value_counts(), f"Temas Mais Mencionados - {num_mes[mes_desejado]}", ax_tema)
            plt.tight_layout()
            pdf.savefig(fig_tema)
            plt.close(fig_tema)

            fig_jornal, ax_jornal = plt.subplots(figsize=(8, 6))
            criar_grafico_barra(df_mes['jornal'].value_counts(), f"Jornais que Mais Mencionaram - {num_mes[mes_desejado]}", ax_jornal)
            plt.tight_layout()
            pdf.savefig(fig_jornal)
            plt.close(fig_jornal)

        pdf_buffer.seek(0)
        return send_file(pdf_buffer, as_attachment=True, mimetype="application/pdf", download_name=f"relatorio_{num_mes[mes_desejado]}.pdf")

    except Exception as e:
        return jsonify({"erro": f"Ocorreu um erro interno ao gerar o PDF: {e}"}), 500

@app.route('/baixar-excel-mensal', methods=['POST'])
def baixar_excel_mensal():
    # CORREÇÃO: Recebe o novo formato 'mes_ano'
    mes_ano_str = request.json.get('mes_ano')
    if not mes_ano_str:
        return jsonify({"erro": "Mês e ano não fornecidos"}), 400

    try:
        # Converte a string 'AAAA-MM' para um objeto datetime
        data_selecionada = datetime.strptime(mes_ano_str, '%Y-%m')
        
        # Filtra os registros pelo mês e ano extraídos
        registros = Noticia.query.filter(
            db.extract('month', Noticia.data_hora) == data_selecionada.month,
            db.extract('year', Noticia.data_hora) == data_selecionada.year
        ).all()

        if not registros:
            return jsonify({"erro": "Nenhum dado encontrado para o mês selecionado."}), 404
        
        df_filtrado = pd.DataFrame([r.to_dict() for r in registros])
        
        output = io.BytesIO()
        df_filtrado.to_excel(output, index=False, sheet_name=data_selecionada.strftime('%B %Y'))
        output.seek(0)
        
        return send_file(
            output, 
            as_attachment=True, 
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            download_name=f'dados_{data_selecionada.strftime("%Y-%m")}.xlsx'
        )
    except Exception as e:
        print(f"Erro ao baixar excel mensal: {e}")
        return jsonify({"erro": f"Erro no processamento: {str(e)}"}), 500

# Roda o servidor Flask
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
