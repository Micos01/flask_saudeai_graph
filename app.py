from flask import Flask, send_file, jsonify
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)

# URLs dos JSON Servers
MUNICIPIOS_URL = 'https://saude-ai-server.vercel.app/municipios'
DOENCAS_URL = 'https://saude-ai-server.vercel.app/doencas'

@app.route('/municipios/graficos', methods=['GET'])
def gerar_graficos_municipios():
    try:
        # Requisição para o endpoint de municípios
        response = requests.get(MUNICIPIOS_URL)
        if response.status_code != 200:
            return jsonify({'erro': 'Não foi possível buscar os dados de municípios'}), response.status_code

        # Carregar dados em um DataFrame
        dados = response.json()
        df = pd.DataFrame(dados)

        # Gerar figura com múltiplos gráficos
        fig, axs = plt.subplots(2, 2, figsize=(15, 10), dpi=300)
        fig.suptitle('Visualização de Indicadores por Município', fontsize=16, weight='bold')

        # Gráfico 1: População por Cidade
        axs[0, 0].bar(df['nome'], df['populacao'], color='skyblue', edgecolor='blue')
        axs[0, 0].set_title('População por Cidade', fontsize=12)
        axs[0, 0].set_ylabel('População')
        axs[0, 0].tick_params(axis='x', rotation=45)

        # Gráfico 2: IDHM por Cidade
        axs[0, 1].plot(df['nome'], df['idhm'], marker='o', color='green', linestyle='--')
        axs[0, 1].set_title('IDHM por Cidade', fontsize=12)
        axs[0, 1].set_ylabel('IDHM')
        axs[0, 1].tick_params(axis='x', rotation=45)

        # Gráfico 3: Gastos Públicos por Cidade
        axs[1, 0].barh(df['nome'], df['gastos_publicos'], color='orange', edgecolor='darkorange')
        axs[1, 0].set_title('Gastos Públicos por Cidade', fontsize=12)
        axs[1, 0].set_xlabel('Gastos Públicos (R$)')
        axs[1, 0].tick_params(axis='y', labelsize=8)

        # Gráfico 4: Mortalidade Infantil por Cidade
        axs[1, 1].scatter(df['nome'], df['mortalidade_infantil'], color='red')
        axs[1, 1].set_title('Mortalidade Infantil por Cidade', fontsize=12)
        axs[1, 1].set_ylabel('Mortalidade Infantil (por mil)')
        axs[1, 1].tick_params(axis='x', rotation=45)

        # Ajustar layout
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        # Salvar e retornar a imagem
        image_path = 'graficos_municipios.png'
        plt.savefig(image_path, format='png')
        plt.close(fig)
        return send_file(image_path, mimetype='image/png')

    except Exception as e:
        return jsonify({'erro': f'Erro ao gerar gráficos: {str(e)}'}), 500


@app.route('/doencas/graficos', methods=['GET'])
def gerar_graficos_doencas():
    try:
        # Requisição para o endpoint de doenças
        response = requests.get(DOENCAS_URL)
        if response.status_code != 200:
            return jsonify({'erro': 'Não foi possível buscar os dados de doenças'}), response.status_code

        # Carregar dados em um DataFrame
        dados = response.json()
        df = pd.json_normalize(dados, record_path='historico', meta=['nome'])

        # Gerar gráfico de barras para cada doença por ano
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
        anos = sorted(df['ano'].unique())
        doencas = df['nome'].unique()
        bar_width = 0.2  # Largura de cada barra
        positions = np.arange(len(doencas))

        for i, ano in enumerate(anos):
            valores = df[df['ano'] == ano].groupby('nome')['casos'].sum()
            offset = (i - len(anos) / 2) * bar_width
            ax.bar(positions + offset, valores, bar_width, label=f'Ano {ano}')

        # Configurar o gráfico
        ax.set_xticks(positions)
        ax.set_xticklabels(doencas, rotation=45)
        ax.set_title('Casos de Doenças por Ano', fontsize=14)
        ax.set_ylabel('Número de Casos')
        ax.legend(title='Ano')

        # Salvar e retornar a imagem
        image_path = 'graficos_doencas.svg'
        plt.tight_layout()
        plt.savefig(image_path, format='svg')
        plt.close(fig)
        return send_file(image_path, mimetype='image/png')

    except Exception as e:
        return jsonify({'erro': f'Erro ao gerar gráficos: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
