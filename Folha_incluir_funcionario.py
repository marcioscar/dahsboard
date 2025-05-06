from datetime import datetime
import time
from bson import ObjectId
import streamlit as st
from db import cadastrar_funcionario, df_salario, edit_funcionario, folha
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


folha = folha()

funcionarios = df_salario()
# st.write(funcionarios)
# funcionarios["salarios"] = funcionarios["salarios"].apply(lambda x: x[0]["valor"] if isinstance(x, list) and len(x) > 0 else None)
# funcionarios["salarios"] = funcionarios["salarios"].apply(
#     lambda x: ", ".join(str(item["valor"]) for item in x) if isinstance(x, list) else None
# )

funcionarios["pago"] = funcionarios["salarios"].apply(
    lambda x: x[-1]["pago"] if isinstance(x, list) and len(x) > 0 and isinstance(x[-1], dict) and "pago" in x[-1] else False
)

funcionarios["valor"] = funcionarios["salarios"].apply(
    lambda x: x[-1]["valor"] if isinstance(x, list) and len(x) > 0 and isinstance(x[-1], dict) and "pago" in x[-1] else False
)
# funcionarios["salarios"] = funcionarios["salarios"].apply(
#     lambda x: x[-3:] if isinstance(x, list) else []
# )
funcionarios["salarios"] = funcionarios["salarios"].apply(
    lambda x: [{"valor": item["valor"], "pago": item["pago"], 'sal_id': item.get("sal_id", str(item.get("_id", "")))} for item in x[-3:]] if isinstance(x, list) else []
)



funcionarios["ultimos"] = funcionarios["salarios"].apply(
    lambda x: [item["valor"] for item in x][-3:] if isinstance(x, list) else []
)

col1, col2 = st.columns(2)
with col1:
    st.markdown('#### Funcionários')

with col2:
    pagos = st.toggle('Pagos')
if pagos:
    funcionarios = funcionarios[funcionarios['pago'] == True]
    
funcionarios["pagar"] = False  
funcionario = st.data_editor(funcionarios,column_config={
        "ultimos": st.column_config.AreaChartColumn(
            "Últimos 3 Salários",
            help="Últimos 3 salários",
            width="medium"),
        'valor': st.column_config.NumberColumn(
             'salario',
             format="dollar"
        ),
    },
    
    column_order=["nome",'funcao',"conta",'pago','valor','pagar' ,"ultimos"], num_rows='Fixed', key="data_editor_funcionarios", 
     use_container_width=True
)


if 'total_salarios_mes' in st.session_state:
    total_salarios_mes = st.session_state.total_salarios_mes
else:
    total_salarios_mes = 0

    
nomes = funcionarios["nome"].to_list()
total = funcionarios["valor"].sum()



@st.dialog("Novo salário")
def salario():
    nome = st.selectbox(
        'Selecione o funcionario', 
        options=nomes, 
        # key="despesa"
    )
    valor = st.number_input('Valor',value=None , min_value=0.01)
    data = datetime.combine(st.date_input('Data', format="DD/MM/YYYY"), datetime.min.time())
    referencia = data.strftime('%b-%Y').lower()

    if st.button("Cadastrar"):
        if valor is None or valor <= 0:
            st.error('Preencher o valor')
            st.stop()
        else:    
            id_salario = ObjectId() 
            folha.update_one(
                {"nome": nome},
                {"$push": {
                    "salarios": {
                        "_id": id_salario,
                        "valor": valor,
                        "data": data,
                        "sal_id": str(id_salario),
                        "fgts": valor * 0.08,
                        "ferias": valor / 12,
                        "decimo": valor / 12,
                        "referencia": referencia,
                        "pago": False,
                    }
                }}
            )

        # despesas.insert_one({"conta": conta,"descricao": descricao,"valor": valor,"data": data, 'referencia': referencia, 'pago': False, 'tipo': 'fixa'})
        st.rerun()

@st.dialog("Pagar salário")
def pagar():
    linha_selecionada = funcionario[funcionario["pagar"] == True]
    if linha_selecionada.empty:
        st.warning("Nenhuma linha foi selecionada!")
    else:
        for index in linha_selecionada.index:
            # Usar o índice da linha selecionada no DataFrame EDITADO para encontrar a linha correspondente no DataFrame ORIGINAL
            id_linha = funcionarios.loc[index, "_id"]
            nome_funcionario = funcionarios.loc[index, "nome"]
            conta_funcionario = funcionarios.loc[index, "conta"]
            
            # Encontrar o último salário não pago
            ultimo_salario_nao_pago = None
            for salario in reversed(funcionarios.loc[index, "salarios"]):
                if isinstance(salario, dict) and "pago" in salario and not salario["pago"]:
                    ultimo_salario_nao_pago = salario
                    break
        
            if ultimo_salario_nao_pago:
                id_salario = ultimo_salario_nao_pago["sal_id"]
                valor_salario = ultimo_salario_nao_pago["valor"]
                
                st.write(nome_funcionario ) 
                st.write( conta_funcionario)
                val_sal = st.number_input('Salário', value=valor_salario) 
                
                # Atualizar o status de pagamento
                def atualizar():
                    resultado = folha.update_one(
                        {"_id": ObjectId(id_linha), "salarios.sal_id": id_salario},
                        {"$set": {"salarios.$.valor": val_sal}}
                    )
                    if resultado.modified_count == 0:
                        st.toast(f"Falha ao atualizar o pagamento de {nome_funcionario}.")
                    else:
                        st.toast(f"Pagamento de {nome_funcionario} atualizado com sucesso!")
                        st.rerun()

                def pagar():
                    resultado = folha.update_one(
                        {"_id": ObjectId(id_linha), "salarios.sal_id": id_salario},
                        {"$set": {"salarios.$.pago": True, "salarios.$.valor": val_sal}}
                    )
                    if resultado.modified_count == 0:
                        st.toast(f"Falha ao atualizar o pagamento de {nome_funcionario}.")
                    else:
                        st.toast(f"Pagamento de {nome_funcionario} atualizado com sucesso!")
                        time.sleep(1)
                        st.rerun()
                def apagar():
                    resultado = folha.update_one(
                        {"_id": ObjectId(id_linha)},
                        {"$pull": {"salarios": {"sal_id": id_salario}}}
                    )
                    if resultado.modified_count == 0:
                        st.toast(f"Falha ao atualizar o pagamento de {nome_funcionario}.")
                    else:
                        st.toast(f"Pagamento de {nome_funcionario} atualizado com sucesso!")
                        time.sleep(1)
                        st.rerun()

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button('💸 Pagar'):
                    pagar()
            with col2:
                if st.button('✅ Atualizar'):
                    atualizar()
            with col3:
               if st.button('🗑️ Apagar'):   
                    apagar()

@st.dialog("Novo Funcionário")
def funcionario():
    with st.form("funcionario"):
        nome = st.text_input("Nome")
        funcao = st.selectbox('Função', options=['Administrativo','Contrato', 'Coordenador','Estágiário', 'Professor' ])
        modalidade = st.selectbox("Modalidade", options=['Judô', 'Musculação', 'Pilates', 'Natação','Ballet', 'Aulas','Geral', 'Boxe','Muaithay', 'Prime' ])
        conta = st.text_input("Conta")
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            cadastrar_funcionario(nome, funcao, modalidade, conta)
            st.success("Funcionário cadastrado com sucesso!")
            st.rerun()

# @st.dialog("Editar Funcionário")
# def editar_funcionario(id,nome, funcao, modalidade,conta):
#     with st.form("funcionario"):
#         modalidade_index = list(funcionarios["modalidade"].unique()).index(modalidade) if modalidade in funcionarios["modalidade"].unique() else 0
#         funcao_index = list(funcionarios["funcao"].unique()).index(funcao) if funcao in funcionarios["funcao"].unique() else 0
#         nome = st.text_input("Nome", value=nome)
#         funcao = st.selectbox('Função', options=['Administrativo','Contrato', 'Coordenador','Estágiário', 'Professor' ], index=funcao_index)
#         modalidade = st.selectbox("Modalidade", options=['Judô', 'Musculação', 'Pilates', 'Natação','Ballet', 'Aulas','Geral', 'Boxe','Muaithay', 'Prime' ], index=modalidade_index)
#         conta = st.text_input("Conta", value=conta)
#         submitted = st.form_submit_button("Editar")
#         if submitted:
#             edit_funcionario(id,nome, funcao, modalidade, conta)
#             st.success("Funcionário editado com sucesso!")
#             st.rerun()
    
    

col1, col2, col3, col4  = st.columns(4)
with col1:
    if st.button("Novo Salário", icon="➕"):
        salario()   
with col2:
    if st.button("Pagar Salário", icon="✅"):
        pagar()
with col3:
    if st.button("Novo Funcionário", icon="🏋"):
        funcionario()  

# with col4:
#     if st.button("Editar Funcionário", icon="📝"):
#         editar_funcionario()



col1, col2 = st.columns(2)
with col1:
    st.metric(label="Total Salários", value=f"R$ {locale.format_string('%.2f', total, grouping=True)}")
with col2:
    if total_salarios_mes is not None:
        st.metric(label="Total Salários Mes", value=f"R$ {locale.format_string('%.2f', total_salarios_mes, grouping=True)}")

