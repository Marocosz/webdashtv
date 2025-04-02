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


query = "SELECT * FROM dados;"
df = pd.read_sql(query, engine)



print(df.head())
engine.dispose()