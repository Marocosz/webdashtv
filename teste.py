import pandas as pd
import matplotlib.pyplot as plt

# Carregar os dados do Excel
df = pd.read_excel('dados.xlsx')

# Converter a coluna 'DataHora' para o tipo datetime (se ainda não estiver)
df['DataHora'] = pd.to_datetime(df['DataHora'])

# Filtrar os dados de um mês específico, por exemplo, mês 1 (Janeiro)
mes_desejado = 3  # Alterar para o mês desejado (1 para Janeiro, 2 para Fevereiro, etc.)
df_mes = df[df['DataHora'].dt.month == mes_desejado]

# Verificar se há dados para o mês especificado
if df_mes.empty:
    print(f"Não há dados para o mês {mes_desejado}.")
else:
    # Filtrar os dados de 'Teor' para o mês específico
    df_teor_filtrado = df_mes[df_mes['Teor'].isin(['Negativo', 'Positivo'])]
    contagem_teor_filtrado = df_teor_filtrado['Teor'].value_counts()

    # Função para formatar os rótulos com o valor absoluto e a porcentagem
    def func(pct, allvals):
        absolute = int(pct / 100.*sum(allvals))
        return f"{absolute} ({pct:.1f}%)"

    # Criar o gráfico de pizza
    plt.figure(figsize=(6,6))
    plt.pie(contagem_teor_filtrado.values, labels=contagem_teor_filtrado.index, autopct=lambda pct: func(pct, contagem_teor_filtrado.values), startangle=90, colors=['#ff9999','#66b3ff'])
    plt.title(f"Distribuição dos valores 'Negativo' e 'Positivo' para o mês {mes_desejado}")
    plt.tight_layout()
    plt.show()

    # Filtrar os dados de 'Tema' para o mês específico
    contagem_temas = df_mes['Tema'].value_counts()

    # Gerar um número dinâmico de cores baseado no número de barras
    num_barras = len(contagem_temas)
    cores = plt.cm.Paired(range(num_barras))  # Usando uma paleta de cores

    # Criar o gráfico de barras para 'Tema'
    plt.figure(figsize=(8,6))
    contagem_temas.plot(kind='bar', color=cores)

    # Adicionar título e rótulos aos eixos
    plt.title(f"Quantidade de vezes que cada tema foi mencionado no mês {mes_desejado}")
    plt.xlabel('Tema')
    plt.ylabel('Quantidade')
    plt.tight_layout()

    # Exibir o gráfico
    plt.show()

    # Filtrar os dados de 'Jornal' para o mês específico
    contagem_jornais = df_mes['Jornal'].value_counts()

    # Criar o gráfico de barras para 'Jornal'
    plt.figure(figsize=(8,6))
    contagem_jornais.plot(kind='bar', color=cores)

    # Adicionar título e rótulos aos eixos
    plt.title(f"Quantidade de vezes que cada jornal foi mencionado no mês {mes_desejado}")
    plt.xlabel('Jornal')
    plt.ylabel('Quantidade')
    plt.tight_layout()

    # Exibir o gráfico
    plt.show()
