import streamlit as st

if 'df_desp' not in st.session_state:
    st.error('Dados não carregados. Favor entrar no Dashboard primeiro')
    st.stop() 

if 'df_rec' not in st.session_state:
    st.error('Dados não carregados. Favor entrar no Dashboard primeiro')
    st.stop() 

desp = st.session_state.df_desp
rec = st.session_state.df_rec
ano_selecionado = st.session_state.ano_selecionado
numero_mes_selecionado = st.session_state.mes_selecionado[0]

def filtro_mes(mes,df):
    return df['data'].dt.month == mes

def filtro_ano(ano,df):
    return df['data'].dt.year == ano


def formatar_diferenca(valor):
    if valor > 0:
        return f"{valor:,.2f}"  # Seta para cima
    elif valor < 0:
        return f"{(valor):,.2f}"  # Seta para baixo e valor absoluto
    return f"{valor:,.2f}"  # Caso seja zero, mantém normal


def formatar_moeda(valor):
    return f"{valor}".replace(",", "X").replace(".", ",").replace("X", ".")  
    

df_desp_rec = rec.merge(desp, on='data', how='outer', suffixes=('_rec', '_desp'))

# Replace NaN values with 0 in specific columns
df_desp_rec['valor_rec'].fillna(0, inplace=True)
df_desp_rec['valor_desp'].fillna(0, inplace=True)

# Ordenar o DataFrame pela data
df_desp_rec.sort_values(by='data', inplace=True)


# Inicializar as colunas 'Saldo Anterior' e 'Saldo' com 0 para a primeira linha
df_desp_rec['Saldo Anterior'] = 0.0
df_desp_rec['Saldo'] = 0.0

# Calcular o saldo acumulado
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

# Calcular o saldo do dia (valor_rec - valor_desp)
df_desp_rec['Saldo do Dia'] = df_desp_rec['valor_rec'] - df_desp_rec['valor_desp']

# Formatar as colunas
df_desp_rec['Saldo'] = df_desp_rec['Saldo'].apply(formatar_diferenca)
df_desp_rec['Saldo do Dia'] = df_desp_rec['Saldo do Dia'].apply(formatar_diferenca)
df_desp_rec['Saldo Anterior'] = df_desp_rec['Saldo Anterior'].apply(formatar_diferenca)



# Filtrar por mês e ano
desp_rec_mes = df_desp_rec[filtro_mes(numero_mes_selecionado, df_desp_rec) & filtro_ano(int(ano_selecionado), df_desp_rec)]
desp_rec_mes = desp_rec_mes.loc[:,['data', 'valor_rec', 'valor_desp', 'Saldo do Dia', 'Saldo']]
desp_rec_mes.columns = ["Data", "Receitas", "Despesas","Saldo do Dia", "Saldo"]

desp_rec_mes['Despesas'] = desp_rec_mes['Despesas'].apply(formatar_diferenca).apply(formatar_moeda)
desp_rec_mes['Receitas'] = desp_rec_mes['Receitas'].apply(formatar_diferenca).apply(formatar_moeda)
desp_rec_mes['Saldo do Dia'] = desp_rec_mes['Saldo do Dia'].apply(formatar_moeda)
desp_rec_mes['Saldo'] = desp_rec_mes['Saldo'].apply(formatar_moeda)
desp_rec_mes["Data"] = desp_rec_mes["Data"].dt.strftime("%d/%m/%Y")


# Exibir os DataFrames
st.subheader("Fluxo de Caixa do Mês")
st.dataframe(desp_rec_mes)

st.subheader("Fluxo de Caixa Completo")
df_desp_rec = df_desp_rec.loc[:,['data', 'valor_rec', 'valor_desp', 'Saldo do Dia', 'Saldo']]
df_desp_rec.columns = ["Data", "Receitas", "Despesas","Saldo do Dia", "Saldo"]
df_desp_rec['Despesas'] = df_desp_rec['Despesas'].apply(formatar_diferenca).apply(formatar_moeda)
df_desp_rec['Receitas'] = df_desp_rec['Receitas'].apply(formatar_diferenca).apply(formatar_moeda)
df_desp_rec['Saldo do Dia'] = df_desp_rec['Saldo do Dia'].apply(formatar_moeda)
df_desp_rec['Saldo'] = df_desp_rec['Saldo'].apply(formatar_moeda)
df_desp_rec["Data"] = df_desp_rec["Data"].dt.strftime("%d/%m/%Y")


st.dataframe(df_desp_rec)








