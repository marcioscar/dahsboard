from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient
import pymongo
import os
import pandas as pd
import locale
import plotly.express as px
import calendar


locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
st.set_page_config(page_title="Quattor Dashboard", page_icon="icon.png", layout="wide")




try:
    # start example code here
    load_dotenv()
    uri = os.getenv("DATABASE_URL")
    client = MongoClient(uri, server_api=pymongo.server_api.ServerApi(
    version="1", strict=True, deprecation_errors=True))
    # end example code here
except Exception as e:
    raise Exception(
        "Erro: ", e)


db = client["quattor"]
receitas = db["receitas"]
data_rec = receitas.find()

despesas = db["despesas"]
data_desp = despesas.find()



salarios = db["folha"]
data_sal = salarios.find()

# Salarios
pipeline = [
    {"$unwind": "$salarios"},
    {
        "$group": {
            "_id": "$salarios.referencia",
            "salario": {"$sum": "$salarios.valor"},
        }
    },
]

sal_modalidades = [
    {"$unwind": "$salarios"},
    {
        "$group": {
            "_id": {
                "referencia": "$salarios.referencia",
                "modalidade": "$modalidade"
            },
            "total_salario": {"$sum": "$salarios.valor"}
        }
    },
    {
        "$project": {
            "_id": 0,
            "referencia": "$_id.referencia",
            "modalidade": "$_id.modalidade",
            "total_salario": 1
        }
    }
]


# Executar o pipeline de agregação
resultado = list(salarios.aggregate(pipeline))  # Convertendo para uma lista
sal_modalidades = pd.DataFrame(list(salarios.aggregate(sal_modalidades)))  



# Converter o resultado em um DataFrame do pandas
total_salarios = pd.DataFrame(resultado)
total_salarios.rename(columns={"_id": "referencia"}, inplace=True)

df_rec =  pd.DataFrame(list(data_rec))
df_desp =  pd.DataFrame(list(data_desp))
df_sal =  pd.DataFrame(list(data_sal))

rec_desp = pd.merge(df_desp, df_rec, on="data", how="outer",suffixes=("_desp", "_rec"))[['data', 'valor_desp', 'valor_rec']]


def filtro_mes(mes,df):
    return df['data'].dt.month == mes

def filtro_ano(ano,df):
    return df['data'].dt.year == ano

def filtro_forma(forma):
    return df_rec['forma'] == forma

def formatar_moeda(valor):
    return locale.currency(valor, grouping=True, symbol=False)

def formatar_data(data):
    return data.strftime('%d-%m-%Y')

df_rec['data_formatada'] = df_rec['data'].apply(formatar_data)
df_rec['valor_formatado'] = df_rec['valor'].apply(formatar_moeda)

df_desp['data_formatada'] = df_desp['data'].apply(formatar_data)
df_desp['valor_formatado'] = df_desp['valor'].apply(formatar_moeda)

df_rec = df_rec.drop(columns=['_id', 'status'])
df_desp = df_desp.drop(columns=['_id', 'referencia'])

# Obter os nomes e números dos meses
meses = [(i, calendar.month_name[i]) for i in range(1, 13)]
anos = ['2024','2025','2026','2027']

# Obter o índice do mês atual
mes_atual = datetime.now().month
ano_atual = datetime.now().year

# Ano atual como string
ano_atual = str(datetime.now().year)

# Determinar o índice do ano atual na lista
index_ano_atual = anos.index(ano_atual)

st.logo('logohor.png', icon_image='icon.png')

# Selectbox com o ano atual selecionado
ano_selecionado = st.sidebar.selectbox(
    'Selecione o Ano', 
    options=anos, 
    index=index_ano_atual  # Define o ano atual como selecionado
)

mes_selecionado = st.sidebar.selectbox(
    'Selecione o Mês', 
    options=meses, 
    format_func=lambda x: x[1],  # Mostrar apenas o nome do mês
    index=mes_atual - 1
)
# Extrair o número do mês selecionado
numero_mes_selecionado = mes_selecionado[0]

ano = 2024
#receitas 
df_mes_pedido_rec = df_rec[filtro_mes(numero_mes_selecionado, df_rec) & filtro_ano(int(ano_selecionado),df_rec)]
df_mes_anterior_rec = df_rec[filtro_mes(numero_mes_selecionado-1, df_rec) & filtro_ano(int(ano_selecionado), df_rec)]

mes_anterior_rec = df_mes_anterior_rec['valor'].sum()
mes_atual_rec = df_mes_pedido_rec['valor'].sum()

#despesas 
df_mes_pedido_desp = df_desp[filtro_mes(numero_mes_selecionado, df_desp) & filtro_ano(int(ano_selecionado),df_desp)]
df_desp_periodo= df_desp[filtro_ano(int(ano_selecionado),df_desp)]


df_mes_anterior_desp = df_desp[filtro_mes(numero_mes_selecionado-1, df_desp) & filtro_ano(int(ano_selecionado), df_desp)]

mes_anterior_desp = df_mes_anterior_desp['valor'].sum()
mes_atual_desp = df_mes_pedido_desp['valor'].sum()

nome_mes_atual = calendar.month_abbr[numero_mes_selecionado].lower()

if numero_mes_selecionado == 1:
    nome_mes_anterior = calendar.month_abbr[12].lower()
    mes_ano_anterior = f"{nome_mes_anterior}-{int(ano_selecionado) - 1}"
    mes_ano_atual = f"{nome_mes_atual}-{ano_selecionado}"
    
else:
    nome_mes_anterior = calendar.month_abbr[numero_mes_selecionado-1].lower()
    mes_ano_anterior = f"{nome_mes_anterior}-{ano_selecionado}"    
    mes_ano_atual = f"{nome_mes_atual}-{ano_selecionado}"


tot_mes = total_salarios[total_salarios["referencia"] == mes_ano_atual]["salario"]
tot_mes_anterior = total_salarios[total_salarios["referencia"] == mes_ano_anterior]["salario"]

sal_modalidades = sal_modalidades.dropna(subset=['referencia'])
sal_modalidades_filtrado = sal_modalidades[sal_modalidades["referencia"] == mes_ano_atual]
sal_modalidades_filtrado_ano  = sal_modalidades[sal_modalidades["referencia"].str.contains(ano_selecionado)]


total_salarios_mes = tot_mes.iloc[0] if not tot_mes.empty else 0
total_salarios_mes_anterior = tot_mes_anterior.iloc[0] if not tot_mes_anterior.empty else 0


# CSS para ajustar a fonte do metric


container = st.container(border=True)
col1, col2,col3 = st.columns(3)

col1.metric(label="Receitas", value=f"R$ {formatar_moeda(mes_atual_rec)}", delta=formatar_moeda(mes_atual - mes_anterior_rec), border=True )
col2.metric(label="Despesas + Salários", value=f"R$ {formatar_moeda(mes_atual_desp)}", delta=formatar_moeda(mes_atual - mes_anterior_desp),border=True)
col3.metric(label="Salários", value=f"R$ {formatar_moeda(total_salarios_mes)}", delta=formatar_moeda(total_salarios_mes - total_salarios_mes_anterior), border=True)




col1, col2, col3 = st.columns(3)
with col1:
    with st.expander('Receitas'):
        st.dataframe(
            df_mes_pedido_rec.groupby(['forma'])['valor'].sum().apply(formatar_moeda),use_container_width=True
        )
with col2:
    with st.expander('Despesas'):
        st.dataframe(
            df_mes_pedido_desp.groupby(['conta'])['valor'].sum().apply(formatar_moeda),use_container_width=True
        )        
with col3:
    with st.expander('Salários por Modalidades'):
        st.dataframe(
            sal_modalidades_filtrado[['modalidade', 'total_salario']]
            .rename(columns={'modalidade': 'Modalidade', 'total_salario': 'Total'})
            .assign(Total=sal_modalidades_filtrado['total_salario'].apply(formatar_moeda))
            .sort_values(by='Total')
            .set_index('Modalidade'), 
            use_container_width=True
        )

sal_modalidades_ordenado = sal_modalidades_filtrado_ano.sort_values(by='total_salario', ascending=True)

# Converter a coluna 'referencia' para um tipo de dado datetime
sal_modalidades_ordenado['referencia_dt'] = pd.to_datetime(sal_modalidades_ordenado['referencia'], format='%b-%Y')

# Ordenar o DataFrame por 'referencia_dt'
sal_modalidades_ordenado = sal_modalidades_ordenado.sort_values(by='referencia_dt')

# Converter a coluna 'referencia' de volta para o formato desejado
sal_modalidades_ordenado['referencia'] = sal_modalidades_ordenado['referencia_dt'].dt.strftime('%b-%Y')



col1, col2 = st.columns(2)
# Criar o gráfico de barras
with col1:
    grafico = px.bar(
        sal_modalidades_ordenado, 
        x='referencia', 
        y='total_salario', 
        color='modalidade', 
        labels={'total_salario': 'Total Salário', 'modalidade': 'Modalidade', 'referencia': 'Referência'},
        title='Salários por Área',
        
    )
    grafico.update_yaxes(tickprefix="R$ ", tickformat=",2f")
    st.plotly_chart(grafico, use_container_width=True)



# Adicionar uma coluna datetime para ordenação
df_desp_periodo['data_ordenacao'] = pd.to_datetime(df_desp_periodo['data'])

# Formatar a coluna 'mes_ano' no formato desejado
df_desp_periodo['mes_ano'] = df_desp_periodo['data_ordenacao'].dt.strftime('%b-%Y')  # Ex.: "Jan-2024"

# Agrupar e somar os valores por 'conta' e 'mes_ano'
resultado = (
    df_desp_periodo.groupby(['conta', 'mes_ano'], as_index=False)
    .agg({'valor': 'sum'})
)

# Ordenar o DataFrame pelo mês e ano (baseado na coluna datetime)
resultado['data_ordenacao'] = pd.to_datetime(resultado['mes_ano'], format='%b-%Y')
resultado = resultado.sort_values(by='data_ordenacao').drop(columns='data_ordenacao')


with col2:
    grafico = px.bar(
        resultado, 
        x='mes_ano', 
        y='valor', 
        color='conta', 
        title='Despesas por Conta',
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={'valor': 'Total', 'mes_ano': 'Referência'},
        hover_data={"valor": ":.2f"},
        
    )
    
    grafico.update_yaxes(tickprefix="R$ ", tickformat=",2f")
    st.plotly_chart(grafico, use_container_width=True)   


#receita e despesas filtradas
df_mes_pedido_rec_desp = rec_desp[filtro_mes(numero_mes_selecionado, rec_desp) & filtro_ano(int(ano_selecionado),rec_desp)]

# Converter a coluna 'data' para datetime
df_mes_pedido_rec_desp['data'] = pd.to_datetime(df_mes_pedido_rec_desp['data'])

# Agrupar e somar os valores de 'valor_desp' e 'valor_rec' para cada dia
resultado_diario = df_mes_pedido_rec_desp.groupby(df_mes_pedido_rec_desp['data'].dt.date).agg({
    'valor_desp': 'sum',
    'valor_rec': 'sum'
}).reset_index()

# Renomear as colunas para clareza
resultado_diario.columns = ['data', 'Total despesas', 'Total Receitas']

# Calcular a soma acumulada dos valores diários
resultado_diario['Despesas'] = resultado_diario['Total despesas'].cumsum()
resultado_diario['Receitas'] = resultado_diario['Total Receitas'].cumsum()

# Criar o gráfico de linhas com valores acumulados
rec_des_grafico = px.line(resultado_diario, x='data', y=['Despesas', 'Receitas'],
                          labels={'value': 'Valor', 'variable': 'Tipo', 'data': 'Data'},
                          title=f"Resultado: {formatar_moeda(mes_atual_rec-mes_atual_desp)}",
                          color_discrete_map={
                            'Total despesas acumuladas': 'orange',  # Cor da linha para Total despesas acumuladas
                             }
                          )

# Atualizar o eixo x para exibir o formato desejado
rec_des_grafico.update_xaxes(tickformat="%d-%b\n%Y")

# Atualizar o eixo y para formatar como moeda brasileira
rec_des_grafico.update_yaxes(tickprefix="R$ ", tickformat=",.2f")

# Exibir o gráfico no Streamlit
st.plotly_chart(rec_des_grafico, use_container_width=True) 