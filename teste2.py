import psycopg2
import pandas as pd

conn = psycopg2.connect(
    dbname="meu_clipping_db",
    user="postgres",
    password="M8r03!hc",
    host="localhost",
    port="5432"
)

df = pd.read_sql("SELECT * FROM clipping;", conn)
print(df)
conn.close()
