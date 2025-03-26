import pandas as pd
import streamlit as st
import calendar
from datetime import datetime

if 'df_desp' not in st.session_state:
    st.error('Dados não carregados. Favor entrar no Dashboard primeiro')
    st.stop() 

if 'df_rec' not in st.session_state:
    st.error('Dados não carregados. Favor entrar no Dashboard primeiro')
    st.stop() 


tab1, tab2, tab3 = st.tabs(["Fluxo do Mes", "Fluxo Total", "Fluxo Projetado"])


desp = st.session_state.df_desp
rec = st.session_state.df_rec
ano_selecionado = st.session_state.ano_selecionado
numero_mes_selecionado = st.session_state.mes_selecionado[0]

def filtro_mes(mes,df):
    return df['data'].dt.month == mes

def filtro_ano(ano,df):
    return df['data'].dt.year == ano

def filtro_inicio(mes,df):
    return df['data'].dt.month >= mes


def formatar_diferenca(valor):
    if valor > 0:
        return f"{valor:,.2f}"  # Seta para cima
    elif valor < 0:
        return f"{(valor):,.2f}"  # Seta para baixo e valor absoluto
    return f"{valor:,.2f}"  # Caso seja zero, mantém normal


def formatar_moeda(valor):
    return f"{valor}".replace(",", "X").replace(".", ",").replace("X", ".")  


def tratar_valor_liquido(valor):
        """
        Função para tratar um único valor da coluna 'VALOR LÍQUIDO'.

        Args:
            valor (str): O valor a ser tratado.

        Returns:
            float or NaN: O valor convertido para float ou NaN se não for possível converter.
        """
        if not isinstance(valor, str):
            return float('nan')  # Retorna NaN se não for uma string
        
        valor = valor.strip()  # Remove espaços em branco no início e no fim
        if not valor:
            return float('nan')  # Retorna NaN se a string estiver vazia

        valor = valor.replace(".", "") # Remove pontos de milhar
        valor = valor.replace(",", ".")  # Substitui vírgula por ponto

        try:
            return round(float(valor), 2)
        except ValueError:
            return float('nan') 


stone = pd.read_csv("dados/stone.csv", sep=';',decimal=',', usecols=['CATEGORIA','DATA DE VENCIMENTO','VALOR LÍQUIDO'], dtype=str)
stone["VALOR LÍQUIDO"] = stone["VALOR LÍQUIDO"].apply(tratar_valor_liquido)
stone.dropna(subset=['VALOR LÍQUIDO'], inplace=True)
stone["VALOR LÍQUIDO"] = stone["VALOR LÍQUIDO"].astype(float)

# Converter a coluna "DATA DE VENCIMENTO" para o tipo datetime
stone["DATA DE VENCIMENTO"] = pd.to_datetime(stone["DATA DE VENCIMENTO"], format="%d/%m/%Y")
resultado_stone = stone.groupby("DATA DE VENCIMENTO")["VALOR LÍQUIDO"].sum().reset_index()

# Ordenar o DataFrame pela coluna "DATA DE VENCIMENTO"
resultado_stone = resultado_stone.sort_values(by="DATA DE VENCIMENTO")
resultado_stone.rename(columns={"DATA DE VENCIMENTO": "data"}, inplace=True)
resultado_stone.rename(columns={"VALOR LÍQUIDO": "valor"}, inplace=True)


df_desp_rec = rec.merge(desp, on='data', how='outer', suffixes=('_rec', '_desp'))

#receitas projetadas
df_desp_rec_projetado = resultado_stone.merge(desp, on='data', how='outer', suffixes=('_rec', '_desp'))


# Replace NaN values with 0 in specific columns
df_desp_rec['valor_rec'].fillna(0, inplace=True)
df_desp_rec['valor_desp'].fillna(0, inplace=True)

#projetado
df_desp_rec_projetado['valor_rec'].fillna(0, inplace=True)
df_desp_rec_projetado['valor_desp'].fillna(0, inplace=True)



# Ordenar o DataFrame pela data
df_desp_rec.sort_values(by='data', inplace=True)
df_desp_rec_projetado.sort_values(by='data', inplace=True)



# Inicializar as colunas 'Saldo Anterior' e 'Saldo' com 0 para a primeira linha
df_desp_rec['Saldo Anterior'] = 0.0
df_desp_rec['Saldo'] = 0.0
df_desp_rec_projetado['Saldo Anterior'] = 0.0
df_desp_rec_projetado['Saldo'] = 0.0

# Calcular o saldo acumulado real
for i in range(len(df_desp_rec)):
    valor_rec = df_desp_rec.loc[i, 'valor_rec']
    valor_desp = df_desp_rec.loc[i, 'valor_desp']
    
    if i == 0:
        # Para a primeira linha, o Saldo Anterior é 0
        saldo_anterior = 338319.02
    else:
        # Para as linhas seguintes, o Saldo Anterior é o Saldo da linha anterior
        saldo_anterior = df_desp_rec.loc[i - 1, 'Saldo']
    
    df_desp_rec.loc[i, 'Saldo Anterior'] = saldo_anterior
    df_desp_rec.loc[i, 'Saldo'] = saldo_anterior + valor_rec - valor_desp

# Calcular o saldo acumulado projetado
for i in range(len(df_desp_rec_projetado)):
    valor_rec = df_desp_rec_projetado.loc[i, 'valor_rec']
    valor_desp = df_desp_rec_projetado.loc[i, 'valor_desp']
    
    if i == 0:
        # Para a primeira linha, o Saldo Anterior é 0
        saldo_anterior = 487068.13
    else:
        # Para as linhas seguintes, o Saldo Anterior é o Saldo da linha anterior
        saldo_anterior = df_desp_rec_projetado.loc[i - 1, 'Saldo']
    
    df_desp_rec_projetado.loc[i, 'Saldo Anterior'] = saldo_anterior
    df_desp_rec_projetado.loc[i, 'Saldo'] = saldo_anterior + valor_rec - valor_desp

# Calcular o saldo do dia (valor_rec - valor_desp)
df_desp_rec['Saldo do Dia'] = df_desp_rec['valor_rec'] - df_desp_rec['valor_desp']
df_desp_rec_projetado['Saldo do Dia'] = df_desp_rec_projetado['valor_rec'] - df_desp_rec_projetado['valor_desp']

# Formatar as colunas
df_desp_rec['Saldo'] = df_desp_rec['Saldo'].apply(formatar_diferenca)
df_desp_rec['Saldo do Dia'] = df_desp_rec['Saldo do Dia'].apply(formatar_diferenca)
df_desp_rec['Saldo Anterior'] = df_desp_rec['Saldo Anterior'].apply(formatar_diferenca)

# Formatar as colunas projetado
df_desp_rec_projetado['Saldo'] = df_desp_rec_projetado['Saldo'].apply(formatar_diferenca)
df_desp_rec_projetado['Saldo do Dia'] = df_desp_rec_projetado['Saldo do Dia'].apply(formatar_diferenca)
df_desp_rec_projetado['Saldo Anterior'] = df_desp_rec_projetado['Saldo Anterior'].apply(formatar_diferenca)




with tab1:
    # Filtrar por mês e ano
    desp_rec_mes = df_desp_rec[filtro_mes(numero_mes_selecionado, df_desp_rec) & filtro_ano(int(ano_selecionado), df_desp_rec)]
    desp_rec_mes = desp_rec_mes.loc[:,['data', 'valor_rec', 'valor_desp', 'Saldo do Dia', 'Saldo']]
    desp_rec_mes.columns = ["Data", "Receitas", "Despesas","Saldo do Dia", "Saldo"]

    desp_rec_mes['Despesas'] = desp_rec_mes['Despesas'].apply(formatar_diferenca).apply(formatar_moeda)
    desp_rec_mes['Receitas'] = desp_rec_mes['Receitas'].apply(formatar_diferenca).apply(formatar_moeda)
    desp_rec_mes['Saldo do Dia'] = desp_rec_mes['Saldo do Dia'].apply(formatar_moeda)
    desp_rec_mes['Saldo'] = desp_rec_mes['Saldo'].apply(formatar_moeda)
    desp_rec_mes["Data"] = desp_rec_mes["Data"].dt.strftime("%d/%m/%Y")

    st.subheader("Fluxo de Caixa do Mês")
    st.dataframe(desp_rec_mes, use_container_width=True, height=500)

with tab2:
    st.subheader("Fluxo de Caixa Completo")
    df_desp_rec = df_desp_rec.loc[:,['data', 'valor_rec', 'valor_desp', 'Saldo do Dia', 'Saldo']]
    df_desp_rec.columns = ["Data", "Receitas", "Despesas","Saldo do Dia", "Saldo"]
    df_desp_rec['Despesas'] = df_desp_rec['Despesas'].apply(formatar_diferenca).apply(formatar_moeda)
    df_desp_rec['Receitas'] = df_desp_rec['Receitas'].apply(formatar_diferenca).apply(formatar_moeda)
    df_desp_rec['Saldo do Dia'] = df_desp_rec['Saldo do Dia'].apply(formatar_moeda)
    df_desp_rec['Saldo'] = df_desp_rec['Saldo'].apply(formatar_moeda)
    df_desp_rec["Data"] = df_desp_rec["Data"].dt.strftime("%d/%m/%Y")
    st.dataframe(df_desp_rec, use_container_width=True, height=500)

with tab3:
    meses = [(i, calendar.month_name[i]) for i in range(1, 13)]
    mes_atual = datetime.now().month
    
    mes_inicio = st.selectbox(
        'Selecione o Mês de inicio da vizualização', 
        options=meses, 
        format_func=lambda x: x[1],  # Mostrar apenas o nome do mês
        index=mes_atual - 1, key="mes_inicio"
    )
    numero_mes_inico = mes_inicio[0]
    
    df_desp_rec_projetado = df_desp_rec_projetado[filtro_inicio(numero_mes_inico, df_desp_rec_projetado) & filtro_ano(int(ano_selecionado), df_desp_rec_projetado)]
    st.subheader("Fluxo de Caixa Projetado")
    df_desp_rec_projetado = df_desp_rec_projetado.loc[:,['data', 'valor_rec', 'valor_desp', 'Saldo do Dia', 'Saldo']]
    df_desp_rec_projetado.columns = ["Data", "Receitas", "Despesas","Saldo do Dia", "Saldo"]
    df_desp_rec_projetado['Despesas'] = df_desp_rec_projetado['Despesas'].apply(formatar_diferenca).apply(formatar_moeda)
    df_desp_rec_projetado['Receitas'] = df_desp_rec_projetado['Receitas'].apply(formatar_diferenca).apply(formatar_moeda)
    df_desp_rec_projetado['Saldo do Dia'] = df_desp_rec_projetado['Saldo do Dia'].apply(formatar_moeda)
    df_desp_rec_projetado['Saldo'] = df_desp_rec_projetado['Saldo'].apply(formatar_moeda)
    df_desp_rec_projetado["Data"] = df_desp_rec_projetado["Data"].dt.strftime("%d/%m/%Y")
    st.dataframe(df_desp_rec_projetado, use_container_width=True, height=500)





