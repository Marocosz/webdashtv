import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Carregar os dados do arquivo Excel
df = pd.read_excel('dados.xlsx')

# Converter a coluna 'DataHora' para o tipo datetime
df['DataHora'] = pd.to_datetime(df['DataHora'])

# Filtrar os dados do mês desejado
num_mes = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 
           6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}

mes_desejado = 3  # Alterar para o mês desejado
df_mes = df[df['DataHora'].dt.month == mes_desejado]

# Verificar se há dados para o mês especificado
if df_mes.empty:
    print(f"Não há dados para o mês {mes_desejado}.")
else:
    # Criar um arquivo PDF para salvar os gráficos
    with PdfPages('graficos.pdf') as pdf:
        
        # Criar o gráfico de pizza para os valores 'Teor'
        df_teor_filtrado = df_mes[df_mes['Teor'].isin(['Negativo', 'Positivo'])]
        contagem_teor_filtrado = df_teor_filtrado['Teor'].value_counts()
        
        # Função para formatar os rótulos com número absoluto e porcentagem
        def func(pct, allvals):
            absolute = int(pct / 100. * sum(allvals))
            return f"{absolute}\n({pct:.1f}%)"
        
        # Criar a figura e o eixo para o gráfico de pizza
        fig, ax = plt.subplots(figsize=(6, 6))
        
        # Definir cores personalizadas para o gráfico
        cores_pizza = ['#03C04A', '#F40000']  # verde para "Positivo" e Vermelho para "Negativo"
        
        # Criar o gráfico de pizza
        wedges, texts, autotexts = ax.pie(
            contagem_teor_filtrado.values,
            labels=contagem_teor_filtrado.index,
            autopct=lambda pct: func(pct, contagem_teor_filtrado.values),
            startangle=90,
            colors=cores_pizza,
            textprops={'fontsize': 12, 'fontweight': 'bold', 'color': 'black'},
            wedgeprops={'edgecolor': 'white', 'linewidth': 2}  # Adicionando a linha branca entre as fatias
        )
                
        # Alterar a cor e a formatação dos textos dentro do gráfico de pizza
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")
        
        # Adicionar título formatado ao gráfico de pizza
        ax.set_title(f"Distribuição dos valores 'Negativo' e 'Positivo' - {num_mes[mes_desejado]}",
                     fontname="Arial", fontsize=16, fontweight='bold', pad=20)
        
        # Ajustar o layout e salvar o gráfico no PDF
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        
        # Função para criar gráficos de barras formatados
        def criar_grafico_barra(dados, titulo, xlabel):
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Criar gráfico de barras com cor personalizada
            barras = dados.plot(kind='bar', color='#4169E1', ax=ax)
            
            # Adicionar rótulos de valores no topo das barras
            for p in barras.patches:
                ax.text(p.get_x() + p.get_width() / 2, p.get_height() + 0.2,
                        str(int(p.get_height())),
                        ha='center', fontsize=12, fontweight='bold', fontname="Arial", color='black')
            
            # Adicionar título e rótulos formatados
            ax.set_title(titulo, fontname="Arial", fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel(xlabel, fontname="Arial", fontsize=12)
            
            ax.set_xlabel("")  # Remove o texto "Tema" ou "Jornal" abaixo do gráfico
            
            # Rotacionar os nomes das categorias para melhor visualização
            ax.xaxis.set_tick_params(rotation=45)
            
            # Ajustar os rótulos das categorias no eixo X
            ax.set_xticks(range(len(dados.index)))
            ax.set_xticklabels(dados.index, ha='right', fontsize=10, fontname="Arial")
            
            # Remover linhas de grade e eixos desnecessários
            ax.yaxis.set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            
            # Ajustar layout e salvar o gráfico no PDF
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
        
        # Criar gráficos de barras para os temas e jornais mais mencionados
        criar_grafico_barra(df_mes['Tema'].value_counts(),
                            f"Temas mais mencionados - {num_mes[mes_desejado]}",
                            "Tema")
        
        criar_grafico_barra(df_mes['Jornal'].value_counts(),
                            f"Jornais que mais mencionaram - {num_mes[mes_desejado]}",
                            "Jornal")
        
        # Criar uma figura com os três gráficos juntos
        fig, axs = plt.subplots(1, 3, figsize=(18, 6))
        
        # Adicionar o gráfico de pizza ao primeiro eixo
        wedges, texts, autotexts = axs[0].pie(
            contagem_teor_filtrado.values, labels=contagem_teor_filtrado.index,
            autopct=lambda pct: func(pct, contagem_teor_filtrado.values), startangle=90,
            colors=cores_pizza, textprops={'fontsize': 10, 'fontweight': 'bold', 'color': 'black'},
            wedgeprops={'edgecolor': 'white', 'linewidth': 2}
        )
        
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")
        
        axs[0].set_title("Teor", fontname="Arial", fontsize=12, fontweight='bold')
        
        # Criar gráficos de barras para "Temas" e "Jornais"
        for ax, dados, titulo, xlabel in zip(
                axs[1:], [df_mes['Tema'].value_counts(), df_mes['Jornal'].value_counts()],
                ["Temas", "Jornais"], ["Tema", "Jornal"]):
            barras = dados.plot(kind='bar', color='#4169E1', ax=ax)
            
            for p in barras.patches:
                ax.text(p.get_x() + p.get_width() / 2, p.get_height() + 0.2,
                        str(int(p.get_height())),
                        ha='center', fontsize=10, fontweight='bold', fontname="Arial", color='black')
            
            ax.set_title(titulo, fontname="Arial", fontsize=12, fontweight='bold')
            ax.set_xlabel(xlabel, fontname="Arial", fontsize=10)
            ax.xaxis.set_tick_params(rotation=45)
            ax.set_xticklabels(dados.index, ha='right', fontsize=10, fontname="Arial")
            ax.yaxis.set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.set_xlabel("")  # Remove o texto "Tema" ou "Jornal" abaixo do gráfico
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    print("Os gráficos foram salvos em 'graficos.pdf'.")
