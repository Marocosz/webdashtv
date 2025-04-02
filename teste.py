from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

DATABASE_URL = "postgresql://postgres:hbBkNPCLxIRGROfLRSLPoHVvCeiqWdwN@metro.proxy.rlwy.net:42270/railway"

# Criar a engine do SQLAlchemy
engine = create_engine(DATABASE_URL)


conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Criar tabela dados se ela não existir
cur.execute("""
    CREATE TABLE IF NOT EXISTS dados (
        id SERIAL PRIMARY KEY,
        canal TEXT,
        jornal TEXT,
        tema TEXT,
        data_hora TIMESTAMP,
        teor TEXT,
        texto TEXT
    );
""")

# Verificar se a tabela existe
cur.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public';
""")

tabelas = cur.fetchall()
print(tabelas)

cur.execute("SELECT * FROM dados;")
print(cur.fetchall())

query = "SELECT * FROM dados;"
df = pd.read_sql(query, conn)

cur.close()
conn.close()

print(df.head())
