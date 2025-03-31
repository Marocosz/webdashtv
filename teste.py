import pandas as pd

# Definir as colunas
columns = ["Canal", "Jornal", "Tema", "DataHora", "Teor", "Texto"]

# Criar um DataFrame vazio
df = pd.DataFrame(columns=columns)

# Salvar como um arquivo Excel
df.to_excel("dados.xlsx", index=False)

print("Arquivo 'dados.xlsx' criado com sucesso!")