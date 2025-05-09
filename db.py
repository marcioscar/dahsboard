from bson import ObjectId
from dotenv import load_dotenv
import pandas as pd
from pymongo import MongoClient
import streamlit as st
import pymongo
from datetime import datetime
import os

filtro = {
    "data": {"$gte": datetime(2025, 1, 1)}  # Data maior ou igual a 1 de janeiro de 2025
}

filtro_despesas = {
    "data": {"$gte": datetime(2025, 1, 1)},  # Data maior ou igual a 1 de janeiro de 2025
    "$or": [
        {"pago": True},   # Registros onde pago é True
        {"pago": {"$exists": False}}  # Registros onde pago não existe
    ]
}
@st.cache_resource
def conexao():
    try:
        load_dotenv()
        uri = os.getenv("DATABASE_URL")
        client = MongoClient(uri, server_api=pymongo.server_api.ServerApi(
        version="1", strict=True, deprecation_errors=True))
    except Exception as e:
        raise Exception(
            "Erro: ", e)
    db = client["quattor"]
    st.session_state.db = db
    return  db

def df_desp():
    db = conexao()
    despesas = db["despesas"]
    data_desp = despesas.find(filtro_despesas)
    df_desp =  pd.DataFrame(list(data_desp)) 
    df_desp_agrupado = df_desp.groupby(['data'])['valor'].sum().reset_index()
    st.session_state.df_desp = df_desp_agrupado
    return df_desp_agrupado

def df_rec():
    db = conexao()
    receitas = db["receitas"]
    data_rec = receitas.find(filtro)
    df_rec =  pd.DataFrame(list(data_rec)) 
    df_rec_agrupado = df_rec.groupby(['data'])['valor'].sum().reset_index()
    st.session_state.df_rec = df_rec_agrupado   
    return df_rec_agrupado

def df_salario():
    db = conexao()
    folha = db["folha"]
    funcionarios = folha.find().sort("nome", 1)
    df_funcionarios = pd.DataFrame(list(funcionarios)) 
    # df_rec_agrupado = df_rec.groupby(['data'])['valor'].sum().reset_index()
    st.session_state.df_salario = df_funcionarios   
    return df_funcionarios

def folha():
    db = conexao()
    folha = db["folha"]
    return folha

def cadastrar_funcionario(nome, funcao, modalidade,conta):
    db = conexao()
    folha = db["folha"]
    folha.insert_one({"nome": nome, "funcao": funcao, "modalidade": modalidade, "conta": conta})
    return folha

def edit_funcionario(id,nome, funcao, modalidade,conta):
    db = conexao()
    folha = db["folha"]
    filtro = {"_id": ObjectId(id)}
    folha.update_one(filtro, {"$set": {"nome": nome, "funcao": funcao, "modalidade": modalidade, "conta": conta}})
    return folha
    
def apagar_funcionario(id):
    db = conexao()
    folha = db["folha"]
    filtro = {"_id": ObjectId(id)}
    folha.delete_one(filtro)
    return folha