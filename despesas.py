import streamlit as st
import pandas as pd
# desp = st.session_state.despesas
# db = st.session_state.db
from db import conexao
from datetime import datetime
import time
import locale
from bson import ObjectId


if 'db' not in st.session_state:
    db = conexao() 
else:
    db = st.session_state.db


despesas = db["despesas"]

def formatar_data(data):
        return data.strftime('%d-%m-%Y')
def formatar_moeda(valor):
        return locale.currency(valor, grouping=True, symbol=False)

filtro = {
    "data": {"$gte": datetime(2025, 1, 1)},  # Data maior ou igual a 1 de janeiro de 2025
    "pago": False  # Somente registros onde pago é False
}
# Executar a consulta com o filtro e o limite
data_desp = despesas.find(filtro).limit(1500)

df_desp =  pd.DataFrame(list(data_desp))
df_desp['data'] = df_desp['data'].apply(formatar_data)
df_desp['valor_formatado'] = df_desp['valor'].apply(formatar_moeda)

desp = df_desp.drop(columns=[ 'referencia', 'tipo', 'valor'])


# Adicionar coluna de seleção
desp["Pagar"] = False  

# Criar DataFrame editável
st.subheader("Despesas Abertas")
# Criar uma cópia do DataFrame para exibição sem "_id" e "pago"
desp_exibir = desp.drop(columns=["_id", "pago"], errors="ignore")

# Adicionar coluna de seleção na cópia para exibição
desp_exibir["Pagar"] = False  

# Criar DataFrame editável sem exibir "_id" e "pago"

df_editado = st.data_editor(desp_exibir, num_rows="fixed")

# Botão para capturar a linha selecionada
if st.button("Pagar Conta"):
    linha_selecionada = df_editado[df_editado["Pagar"] == True]

    if linha_selecionada.empty:
        st.warning("Nenhuma linha foi selecionada!")
    else:
        # Resgatar o ID da linha original
        id_linha = desp.loc[linha_selecionada.index, "_id"].values[0]
        despesa_linha = linha_selecionada["descricao"].values[0]
        id_linha = ObjectId(id_linha)  
        
        resultado = despesas.update_one({"_id": id_linha}, {"$set": {"pago": True}})

        if resultado.modified_count == 0:
            st.toast(f"Falha ao atualizar {despesa_linha}.")
        else:
            st.toast(f"{despesa_linha} Pago com Sucesso!!")
            time.sleep(1)
            st.rerun()     