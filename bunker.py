import pandas as pd
import streamlit as st
import numpy as np

# Configuração básica do layout
st.set_page_config(layout="wide")
st.header("INTERGAMES BUNKER 2025")
st.subheader("Leaderboard")

caminho_arquivo = 'Bnkr Intergames Leaderboard V2.xlsx'

# 1. LISTA DE NOMES DAS ABAS ATUALIZADA EM MAIÚSCULAS
# Estes nomes devem corresponder EXATAMENTE aos nomes das abas no arquivo Excel.
nomes_das_tabelas = [
    'SCALED FEM', 
    'SCALED MASC', 
    'INTER FEM', 
    'INTER MASC', 
    'MASTER FEM', 
    'MASTER MASC', 
    'RX FEM', 
    'RX MASC'
]

# FUNÇÃO DE CARREGAMENTO E PROCESSAMENTO
@st.cache_data
def carregar_tabelas(caminho, abas):
    """
    Lê o Excel com cache, remove linhas vazias, FILTRA a linha 'Total Geral', 
    ordena, adiciona Posição e aplica o filtro de colunas.
    """
    dicionario_bruto = pd.read_excel(
        caminho, 
        sheet_name=abas, 
        header=3  # Linha 4 do Excel
    ) 
    
    dicionario_filtrado = {}
    
    for nome_aba, df_bruto in dicionario_bruto.items():
        
        # 1. LIMPEZA INICIAL: Remove linhas onde todos os valores são NaN
        df_limpo = df_bruto.dropna(how='all').copy()

        # 2. REMOÇÃO ROBUSTA DA LINHA 'Total Geral'
        try:
            # O filtro mantém apenas as linhas onde a coluna 'Equipe/Atleta' NÃO é 'Total Geral'
            df_comp = df_limpo[df_limpo['Equipe/Atleta'] != 'Total Geral'].copy()
        except KeyError:
            # Em caso de erro no nome da coluna, usa o df limpo
            df_comp = df_limpo.copy()
            st.warning(f"Aviso: Não foi possível filtrar a linha 'Total Geral' na aba {nome_aba}.")
        
        # 3. ORDENAÇÃO POR 'Total Geral'
        try:
            # Garante que a coluna 'Total Geral' é numérica para a ordenação
            df_comp['Total Geral'] = pd.to_numeric(df_comp['Total Geral'], errors='coerce')

            df_ordenado = df_comp.sort_values(
                by='Total Geral', 
                ascending=False,
                na_position='last', 
                ignore_index=True 
            ).copy()
        
        except KeyError:
            df_ordenado = df_comp.copy()
            st.warning(f"Aviso: Coluna 'Total Geral' não encontrada na aba {nome_aba}. Ordenação e Posição não aplicadas.")

        # 4. CRIAÇÃO DA COLUNA DE POSIÇÃO (Rank)
        num_atletas = df_ordenado.shape[0]
        # Insere a coluna 'Posição' na primeira coluna (índice 0)
        df_ordenado.insert(0, 'Posição', np.arange(1, num_atletas + 1))
        
        # 5. FILTRAR AS COLUNAS (Posição + 6 originais = 7 colunas)
        df_filtrado = df_ordenado.iloc[:, 0:8].copy()
        
        dicionario_filtrado[nome_aba] = df_filtrado
        
    return dicionario_filtrado

# CHAMA a função para obter o dicionário de DataFrames
dicionario_dataframes = carregar_tabelas(caminho_arquivo, nomes_das_tabelas)


# ----------------------------------------------------
# INTERFACE STREAMLIT
# ----------------------------------------------------

# Cria a lista de opções (os nomes das abas em MAIÚSCULAS)
opcoes_lb = list(dicionario_dataframes.keys())

if opcoes_lb:
    
    # Segmented Control usa os nomes em MAIÚSCULAS
    selection = st.segmented_control("Categoria", opcoes_lb) 

    if selection:
        
        tabela_escolhida = dicionario_dataframes[selection]
        
        st.subheader(f"Classificação: {selection}")
        
        # CÁLCULO DA ALTURA DINÂMICA
        num_linhas = tabela_escolhida.shape[0]
        altura_dinamica = (num_linhas * 35) + 38
        
        st.dataframe(
            tabela_escolhida, 
            use_container_width=True, 
            hide_index=True, 
            height=altura_dinamica
        )
        
    else:
        st.info("Selecione uma categoria acima para visualizar a Leaderboard.")

# Se o dicionário estiver vazio, mostra o erro.
else:
    st.error("Nenhuma Leaderboard foi carregada. Verifique se os nomes das abas em MAIÚSCULAS estão corretos no Excel.")