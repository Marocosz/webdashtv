import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# --- 1. Configuração do Ambiente e do Banco de Dados ---

print("A iniciar o script de importação...")

# Carrega as variáveis de ambiente do ficheiro .env
load_dotenv()

# Obtém a URL de conexão do banco de dados do seu ficheiro .env
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("ERRO: A variável de ambiente DATABASE_URL não foi encontrada. Verifique se o seu ficheiro .env está no mesmo diretório e configurado corretamente.")

# Converte o prefixo 'postgres://' para 'postgresql://' se necessário
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Cria a base para o modelo declarativo do SQLAlchemy
Base = declarative_base()

# --- 2. Definição do Modelo (Deve ser idêntico ao do seu app.py) ---

class Noticia(Base):
    """
    Representa a tabela 'noticia' no banco de dados.
    """
    __tablename__ = 'noticia'
    id = Column(Integer, primary_key=True)
    canal = Column(String(100), nullable=False)
    jornal = Column(String(100), nullable=False)
    tema = Column(String(200), nullable=False)
    data_hora = Column(DateTime, nullable=False)
    teor = Column(String(50), nullable=False)
    texto = Column(Text, nullable=False)

    def __repr__(self):
        return f'<Noticia {self.id}: {self.jornal}>'

# --- 3. Script de Importação ---

def importar_dados_do_excel():
    """
    Lê um ficheiro Excel e importa os seus dados para o banco de dados PostgreSQL.
    """
    excel_file_path = 'dados.xlsx' # Nome do seu ficheiro Excel

    # Verifica se o ficheiro Excel existe no mesmo diretório
    if not os.path.exists(excel_file_path):
        print(f"ERRO: O ficheiro '{excel_file_path}' não foi encontrado.")
        print("Por favor, coloque este script no mesmo diretório que o seu ficheiro Excel.")
        return

    # Lê os dados do Excel para um DataFrame do Pandas
    try:
        df = pd.read_excel(excel_file_path)
        print(f"Sucesso: {len(df)} registos encontrados no ficheiro Excel.")
    except Exception as e:
        print(f"ERRO: Não foi possível ler o ficheiro Excel. Detalhes: {e}")
        return
        
    # Renomeia as colunas do Excel para corresponderem ao modelo do banco de dados (letras minúsculas)
    try:
        df.rename(columns={
            "Canal": "canal",
            "Jornal": "jornal",
            "Tema": "tema",
            "DataHora": "data_hora",
            "Teor": "teor",
            "Texto": "texto"
        }, inplace=True)
    except Exception as e:
        print(f"AVISO: Não foi possível renomear as colunas. A verificar se já estão no formato correto... Erro: {e}")

    # Conecta-se ao banco de dados
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        print("Sucesso: Conexão com o banco de dados estabelecida.")
    except Exception as e:
        print(f"ERRO: Falha ao conectar ao banco de dados. Verifique a sua DATABASE_URL. Detalhes: {e}")
        return

    # Garante que a tabela 'noticia' existe no banco de dados
    Base.metadata.create_all(engine)
    
    registos_adicionados = 0
    registos_ignorados = 0

    print("\nA iniciar o processo de importação... (Isto pode demorar alguns minutos)")
    # Itera sobre cada linha do DataFrame
    for index, row in df.iterrows():
        try:
            # Converte a coluna de data/hora
            data_hora_obj = pd.to_datetime(row['data_hora']).to_pydatetime()
            
            # (Opcional) Verifica se o registo já existe para evitar duplicados
            registo_existente = session.query(Noticia).filter_by(
                texto=row['texto'], 
                data_hora=data_hora_obj
            ).first()

            if registo_existente:
                registos_ignorados += 1
                continue # Pula para o próximo registo se já existir

            # Cria um novo objeto Noticia com os dados da linha
            nova_noticia = Noticia(
                canal=row['canal'],
                jornal=row['jornal'],
                tema=row['tema'],
                data_hora=data_hora_obj,
                teor=row['teor'],
                texto=row['texto']
            )
            session.add(nova_noticia)
            registos_adicionados += 1

        except Exception as e:
            print(f"\nERRO ao processar a linha {index + 2} do Excel:")
            print(row.to_dict())
            print(f"Detalhes do erro: {e}\n")
            session.rollback()
            return

    # Salva (commit) todas as alterações no banco de dados de uma só vez
    try:
        session.commit()
        print("\n--- ✅ IMPORTAÇÃO CONCLUÍDA ✅ ---")
        print(f"Total de registos adicionados: {registos_adicionados}")
        print(f"Total de registos já existentes (ignorados): {registos_ignorados}")
    except Exception as e:
        print(f"ERRO FINAL: Falha ao salvar os dados no banco. Nenhuma alteração foi feita. Detalhes: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    importar_dados_do_excel()
