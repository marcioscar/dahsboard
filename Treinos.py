"""Módulo_para_gerenciamento_e_visualização_de_treinos."""

import os
import streamlit as st
from db import conexao
import re
import uuid
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import pdfkit
from PyPDF2 import PdfReader, PdfWriter
 

pasta_assets = os.path.join(os.path.dirname(__file__), 'assets')
arquivo_layout = 'semana6.pdf'
caminho_layout = os.path.join(pasta_assets, arquivo_layout)
arquivo_template = 'template.jinja'
css = open('assets/style.css', 'r').read()
pasta_impressao = os.path.join(os.path.dirname(__file__), 'impressoes')

# Verificar se a pasta de impressões existe, se não, criar
if not os.path.exists(pasta_impressao):
    os.makedirs(pasta_impressao)

# Verificar se o arquivo de layout existe


# Listar arquivos de layout disponíveis
arquivos_layout = [f for f in os.listdir(pasta_assets) if f.endswith('.pdf')]
if not arquivos_layout:
    st.warning("Nenhum arquivo de layout PDF encontrado na pasta assets.")
else:
    arquivo_layout_padrao = 'semana6.pdf' if 'semana6.pdf' in arquivos_layout else arquivos_layout[0]
    caminho_layout = os.path.join(pasta_assets, arquivo_layout_padrao)

loader = FileSystemLoader(pasta_assets)
env = Environment(loader=loader)
template = env.get_template(arquivo_template)


if 'db' not in st.session_state:
    db = conexao() 
else:
    db = st.session_state.db

treinos = db["banco_treinos"]
treino_semana = db["treinos"]

# Mapeamento de exercícios para nomes de arquivos GIF
mapeamento_videos = {
    "Abdominal Declinado": "abd_declinado.gif",
    "Abdominal Máquina": "abd_maquina.gif",
    "Agachamento": "agachamento.gif",
    "Apoio": "apoio.gif",
    "Apoio Pé no banco": "apoio_pe_banco.gif",
    "Barra no Graviton": "barra_graviton.gif",
    "Cadeira Extensora": "cadeira_extensora.gif",
    "Crucifixo reto com halteres": "crucifixo_reto_alteres.gif",
    "Crucifixo Cross Over": "desenvolvimento_militar_sentado.gif",
    "Crucifixo com Halteres": "crucifixo_halteres.gif",
    "Crucifixo Invertido Máquina": "crucifixo_invertido_maquina.gif",
    "Desenvolvimento Militar Sentado": "crucifixo_cross_over.gif",
    "Desenvolvimento com Halteres": "desenvolvimento_halteres.gif",
    "Desenvolvimento Máquina": "desenvolvimento_maquina.gif",
    "Elevação Lateral Curvado": "elevacao_lateral_curvado.gif",
    "Elevação Frontal Alternado Sentado": "elevacao_frontal_alternado_sentado.gif",
    "Elevação Lateral": "elevacao_lateral.gif",
    "Flying Reto Alternado": "flying_reto_alternado.gif",
    "Levantamento Terra": "levantamento_terra.gif",
    "Leg 45º": "leg_horizontal.gif",
    "Leg Horizontal": "leg_horizontal.gif",
    "Martelo Alternado": "martelo_alternado.gif",
    "Paralela Máquina": "paralela_maquina.gif",
    "Pull Down Articulado": "pulldown_articulado.gif",
    "Pull Down com Barra": "pulldown_barra.gif",
    "Puxador Frente": "puxador_frente.gif",
    "Remada Alta com Barra": "remada_alta_barra.gif",
    "Remada Sentada com Triangulo": "remada_sentada_triangulo.gif",
    "Rosca Direta Barra 'W'": "rosca_direta_w.gif",
    "Rosca Testa Halteres": "rosca_testa_halteres.gif",
    "Rosca Francesa Halteres": "rosca_francesa_halteres.gif",
    "Rosca Testa com Barra": "rosca_testa_barra.gif",
    "Supino Máquina": "supino_maquina.gif",
    "Supino Inclinado": "supino_inclinado.gif",
    "Supino Reto": "supino_reto.gif",
    "Triceps Pulley com Barra": "triceps_pulley_barra.gif",
    "Triceps Pulley com Corda": "triceps_pulley_corda.gif",
    "Triceps Pulley Unilateral": "triceps_pulley_unilateral.gif",
    "_Producao": "producao.gif"
}

videos = [
  "_Producao",
  "Abdominal Declinado",
  "Abdominal Máquina",
  "Agachamento",
  "Apoio",
  "Apoio Pé no banco",
  "Barra no Graviton",
  "Cadeira Extensora",
  "Crucifixo reto com halteres",
  "Crucifixo Cross Over",
  "Crucifixo com Halteres",
  "Crucifixo Invertido Máquina",
  "Desenvolvimento Militar Sentado",
  "Desenvolvimento com Halteres",
  "Desenvolvimento Máquina",
  "Elevação Lateral Curvado",
  "Elevação Frontal Alternado Sentado",
  "Elevação Lateral",
  "Flying Reto Alternado",
  "Levantamento Terra",
  "Leg 45º",
  "Leg Horizontal",
  "Martelo Alternado",
  "Paralela Máquina",
  "Pull Down Articulado",
  "Pull Down com Barra",
  "Puxador Frente",
  "Remada Alta com Barra",
  "Remada Sentada com Triangulo",
  "Rosca Direta Barra 'W'",
  "Rosca Testa Halteres",
  "Rosca Francesa Halteres",
  "Rosca Testa com Barra",
  "Supino Máquina",
  "Supino Inclinado",
  "Supino Reto",
  "Triceps Pulley com Barra",
  "Triceps Pulley com Corda",
  "Triceps Pulley Unilateral"
]

tab1, tab2 = st.tabs(["📈 Cadastrar Treinos", "📆 Semana treinos"])

with tab1:
    st.subheader("Treinos")

    with st.form('cadastro'):
        col1, col2 = st.columns(2)
        with col1:
            treino = st.selectbox('Treino',['Treino1', 'Treino2', 'Treino3', 'Treino4', 'Treino5', 'Treino6'] )
            grupo = st.selectbox('Grupos',['ABDOME', 'BICEPS',"COSTAS",'GLUTEOS',"MEMBROS SUPERIORES 1",'MEMBROS SUPERIORES 2','MEMBROS INFERIORES GERAL','MEMBROS SUPERIORES GERAL' ,"OMBROS",'PANTURRILHA','PEITORAL','POSTERIORES DE COXAS','QUADS', 'TRICEPS'])
            exercicio = st.text_input('Exercício').upper()
        with col2:
            repeticoes = st.text_input('Repetições')
            video_selecionado = st.selectbox('Video', videos)
            observacao = st.text_input('Observação')
        submit = st.form_submit_button('Cadastrar', type='primary')


    if submit:
        st.write(f"Treino: {treino}")

        # Verificar se já existe um documento com este treino e grupo
        treino_existente = treinos.find_one({"treino": treino, "grupo": grupo})
        
        # Usar o mapeamento para obter o nome do arquivo GIF
        video_final = mapeamento_videos.get(video_selecionado, video_selecionado)
        
        if treino_existente:
            # Se existir, atualizar o documento existente
            resultado = treinos.update_one(
                {"_id": treino_existente["_id"]},
                {"$push": {
                    "exercicios": {
                        "exercicio": exercicio,
                        "observacao": observacao,
                        "video": video_final,
                        "repeticoes": repeticoes
                    }
                }}
            )
            doc_id = treino_existente["_id"]
            st.session_state.treino_id = doc_id
            st.toast(f'Treino atualizado com sucesso! ID: {doc_id}')
        else:
            # Se não existir, criar um novo documento
            novo_treino = {
                "treino": treino,
                "grupo": grupo,
                "exercicios": [{
                    "exercicio": exercicio,
                    "observacao": observacao,
                    "video": video_final,
                    "repeticoes": repeticoes
                }]
            }
            resultado = treinos.insert_one(novo_treino)
            doc_id = resultado.inserted_id
            st.session_state.treino_id = doc_id
            st.toast(f'Novo treino cadastrado com sucesso! ID: {doc_id}')
        
        st.rerun()

    # Buscar o treino pelo ID armazenado na sessão
    if 'treino_id' in st.session_state:
        treino_selecionado = treinos.find_one({"_id": st.session_state.treino_id})
    else:
        # Fallback para buscar pelo nome do treino se não houver ID na sessão
        treino_selecionado = treinos.find_one({"treino": treino})

    if treino_selecionado and "exercicios" in treino_selecionado:
        st.write("Exercícios do treino:")
        for i, exercicio in enumerate(treino_selecionado["exercicios"], 1):
            st.write(f"{i}. {exercicio['exercicio']}: {exercicio['repeticoes']} repetições")
    else:
        st.write("Nenhum exercício encontrado para este treino.")

with tab2:
    with st.form('cad_semana'):
        st.subheader("Cadastrar treinos da semana")
        treinos_lista = list(treinos.find())
        treinos_nomes = [treino['treino'] for treino in treinos_lista]
        treinos_nomes_unicos = list(dict.fromkeys(treinos_nomes))
        col1, col2 = st.columns(2)
        with col1:
            selecionar_treino = st.selectbox('Selecione o treino', treinos_nomes_unicos)
        # Encontrar o documento completo do treino selecionado
        treino_selecionado = next((t for t in treinos_lista if t['treino'] == selecionar_treino), None)
        if treino_selecionado:
            st.write(f"ID do treino: {treino_selecionado['_id']}")
            st.write(f"Nome do treino: {treino_selecionado.get('treino', 'Não especificado')}")
        else:
            st.write("Nenhum treino selecionado.")
        with col2:
            semanas = [
            "01 - (29/12 a 04/01)",
            "02 - (05/01 a 11/01)",
            "03 - (12/01 a 18/01)",
            "04 - (19/01 a 25/01)",
            "05 - (26/01 a 01/02)",
            "06 - (02/02 a 08/02)",
            "07 - (09/02 a 15/02)",
            "08 - (16/02 a 22/02)",
            "09 - (23/02 a 01/03)",
            "10 - (02/03 a 08/03)",
            "11 - (09/03 a 15/03)",
            "12 - (16/03 a 22/03)",
            "13 - (23/03 a 29/03)",
            "14 - (30/03 a 05/04)",
            "15 - (06/04 a 12/04)",
            "16 - (13/04 a 19/04)",
            "17 - (20/04 a 26/04)",
            "18 - (27/04 a 03/05)",
            "19 - (04/05 a 10/05)",
            "20 - (11/05 a 17/05)",
            "21 - (18/05 a 24/05)",
            "22 - (25/05 a 31/05)",
            "23 - (01/06 a 07/06)",
            "24 - (08/06 a 14/06)",
            "25 - (15/06 a 21/06)",
            "26 - (22/06 a 28/06)",
            "27 - (29/06 a 05/07)",
            "28 - (06/07 a 12/07)",
            "29 - (13/07 a 19/07)",
            "30 - (20/07 a 26/07)",
            "31 - (27/07 a 02/08)",
            "32 - (03/08 a 09/08)",
            "33 - (10/08 a 16/08)",
            "34 - (17/08 a 23/08)",
            "35 - (24/08 a 30/08)",
            "36 - (31/08 a 06/09)",  
            "37 - (07/09 a 13/09)",
            "38 - (14/09 a 20/09)",  
            "39 - (21/09 a 27/09)",  
            "40 - (28/09 a 04/10)",
            "41 - (05/10 a 11/10)",
            "42 - (12/10 a 18/10)",
            "43 - (19/10 a 25/10)",
            "44 - (26/10 a 01/11)",
            "45 - (02/11 a 08/11)",
            "46 - (09/11 a 15/11)",
            "47 - (16/11 a 22/11)",
            "48 - (23/11 a 29/11)",
            "49 - (30/11 a 06/12)",  
            "50 - (07/12 a 13/12)",
            "51 - (14/12 a 20/12)",
            "52 - (21/12 a 27/12)",
            "53 - (28/12 a 03/01)"
            ]
            semana = st.selectbox('selecione a semana', semanas)
            submit = st.form_submit_button('Cadastrar', type='primary')

    if submit:
        # Extrair apenas o número da semana
        match = re.match(r"(\d+) -", semana)
        if match:
            numero_semana = match.group(1)
            
            # Verificar se o treino selecionado existe e tem exercícios
            if treino_selecionado and "exercicios" in treino_selecionado:
                # Criar a lista de exercícios no formato desejado
                exercicios_formatados = []
                for exercicio in treino_selecionado["exercicios"]:
                    # Gerar um ID único para cada exercício
                    execid = str(uuid.uuid4())
                    
                    exercicio_formatado = {
                        "nome": exercicio["exercicio"],
                        "Repeticoes": exercicio["repeticoes"],
                        "obs": exercicio.get("observacao", ""),
                        "video": exercicio.get("video", ""),
                        "carga": 'carga',
                        
                    }
                    exercicios_formatados.append(exercicio_formatado)
                
                # Criar o documento completo
                documento = {
                    "grupo": treino_selecionado.get("grupo", ""),
                    "semana": int(numero_semana),
                    "exercicios": exercicios_formatados
                    
                }
                
                # Inserir o documento na coleção
                resultado = treino_semana.insert_one(documento)
                
                # Verificar se existem outros grupos para o mesmo treino
                outros_grupos = list(treinos.find({"treino": selecionar_treino, "_id": {"$ne": treino_selecionado["_id"]}}))
                
                # Inserir os outros grupos
                for grupo in outros_grupos:
                    if "exercicios" in grupo:
                        # Criar a lista de exercícios para este grupo
                        exercicios_grupo = []
                        for exercicio in grupo["exercicios"]:
                            execid = str(uuid.uuid4())
                            exercicio_formatado = {
                                "nome": exercicio["exercicio"],
                                "Repeticoes": exercicio["repeticoes"],
                                "obs": exercicio.get("observacao", ""),
                                "video": exercicio.get("video", ""),
                                "carga": 'carga',
                            }
                            exercicios_grupo.append(exercicio_formatado)
                        
                        # Criar o documento para este grupo
                        documento_grupo = {
                            "grupo": grupo.get("grupo", ""),
                            "semana": int(numero_semana),
                            "exercicios": exercicios_grupo
                        }
                        
                        # Inserir o documento na coleção
                        treino_semana.insert_one(documento_grupo)
                
                st.write(f"Treino: {selecionar_treino}")
                st.write(f"Semana: {numero_semana}")
                
                st.toast("Treino da semana cadastrado com sucesso!")
            else:
                st.error("O treino selecionado não possui exercícios cadastrados.")
        else:
            st.error("Formato de semana inválido.")

    with st.form('imprime treino'):
        st.subheader("Imprimir treino")
        semana_selecionada = st.selectbox('Selecione a semana', semanas)
        mesclar_com_layout = st.checkbox('Mesclar com layout', value=True)
        
        # Opção para selecionar o arquivo de layout
        if mesclar_com_layout and arquivos_layout:
            arquivo_layout_selecionado = st.selectbox('Selecione o arquivo de layout', arquivos_layout, 
                                                     index=arquivos_layout.index(arquivo_layout_padrao) if arquivo_layout_padrao in arquivos_layout else 0)
            caminho_layout = os.path.join(pasta_assets, arquivo_layout_selecionado)
        
        submit = st.form_submit_button('Imprimir', type='primary')

    if submit:
        match = re.match(r"(\d+) -", semana_selecionada)
        if match:
            numero_semana = match.group(1)
        st.write(f"Semana: {numero_semana}")
        treinos_semana = list(treino_semana.find({"semana": int(numero_semana)}))
        

        if treinos_semana:
            # Agrupar treinos por grupo
            treinos_por_grupo = {}
            for treino in treinos_semana:
                grupo = treino.get("grupo", "Sem grupo")
                if grupo not in treinos_por_grupo:
                    treinos_por_grupo[grupo] = []
                treinos_por_grupo[grupo].append(treino)
            
            templates_var = {
                'stylesheet': css
            }
            # Gerar arquivos HTML separados para cada grupo
            for grupo, treinos in treinos_por_grupo.items():
                # Criar um HTML separado para cada grupo
                grupo_html = ''
                
                # Adicionar o conteúdo do grupo
                for treino in treinos:
                    if "exercicios" in treino:
                        # Criar uma tabela HTML personalizada para os exercícios
                        grupo_html += f'<table class="table-auto w-full text-left">\n'
                        grupo_html += '<tbody class="text-sm divide-y divide-gray-500">\n'
                        
                        for i, exercicio in enumerate(treino["exercicios"], 1):
                            grupo_html += '<tr>\n'
                            grupo_html += '<td>\n'
                            grupo_html += f'<div class="font-extrabold text-3xl mb-2">{i} - {exercicio.get("nome", "")}</div>\n'
                            grupo_html += '<div class="pl-8 space-y-1">\n'
                            grupo_html += f'<div class="items-center"><svg width="24px" height="22px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M9.5 19.75C9.91421 19.75 10.25 19.4142 10.25 19C10.25 18.5858 9.91421 18.25 9.5 18.25V19.75ZM11 5V5.75C11.3033 5.75 11.5768 5.56727 11.6929 5.28701C11.809 5.00676 11.7448 4.68417 11.5303 4.46967L11 5ZM9.53033 2.46967C9.23744 2.17678 8.76256 2.17678 8.46967 2.46967C8.17678 2.76256 8.17678 3.23744 8.46967 3.53033L9.53033 2.46967ZM9.5 18.25H9.00028V19.75H9.5V18.25ZM9 5.75H11V4.25H9V5.75ZM11.5303 4.46967L9.53033 2.46967L8.46967 3.53033L10.4697 5.53033L11.5303 4.46967ZM1.25 12C1.25 16.2802 4.72011 19.75 9.00028 19.75V18.25C5.54846 18.25 2.75 15.4517 2.75 12H1.25ZM2.75 12C2.75 8.54822 5.54822 5.75 9 5.75V4.25C4.71979 4.25 1.25 7.71979 1.25 12H2.75Z" fill="#1C274C"/><path opacity="0.5" d="M13 19V18.25C12.6967 18.25 12.4232 18.4327 12.3071 18.713C12.191 18.9932 12.2552 19.3158 12.4697 19.5303L13 19ZM14.4697 21.5303C14.7626 21.8232 15.2374 21.8232 15.5303 21.5303C15.8232 21.2374 15.8232 20.7626 15.5303 20.4697L14.4697 21.5303ZM14.5 4.25C14.0858 4.25 13.75 4.58579 13.75 5C13.75 5.41421 14.0858 5.75 14.5 5.75V4.25ZM15 18.25H13V19.75H15V18.25ZM12.4697 19.5303L14.4697 21.5303L15.5303 20.4697L13.5303 18.4697L12.4697 19.5303ZM14.5 5.75H15V4.25H14.5V5.75ZM21.25 12C21.25 15.4518 18.4518 18.25 15 18.25V19.75C19.2802 19.75 22.75 16.2802 22.75 12H21.25ZM22.75 12C22.75 7.71979 19.2802 4.25 15 4.25V5.75C18.4518 5.75 21.25 8.54822 21.25 12H22.75Z" fill="#1C274C"/></svg> {exercicio.get("Repeticoes", "")}</div>\n'
                            grupo_html += '</div>\n'
                            grupo_html += '</td>\n'
                            grupo_html += '</tr>\n'
                        grupo_html += '</tbody>\n'
                        grupo_html += '</table>\n\n'
                        
                
                # Criar um nome de variável válido para o Jinja2
                nome_variavel = re.sub(r'[^a-zA-Z0-9]', '_', grupo.lower())
                templates_var[nome_variavel] = grupo_html
                
        
        html = template.render(**templates_var)
        
        # Definir o nome base do arquivo
        nome_base = f'treinos_semana_{semana_selecionada[:2]}'
        
        nome_relatorio = f'{nome_base}.pdf'
        
      
        caminho_relatorio = os.path.join(pasta_impressao, nome_relatorio)
        
        # Configurações para o pdfkit
        options = {
            'quiet': '',
            'disable-smart-shrinking': '',
            'no-stop-slow-scripts': '',
            'enable-local-file-access': '',
            'disable-external-links': '',
            'disable-javascript': '',
            'encoding': 'UTF-8'
        }
        
        
            # Gerar o PDF usando o método escolhido
       
        pdfkit.from_string(html, output_path=caminho_relatorio, options=options)
        
        # Mesclar com o layout
        try:
            # Ler o PDF gerado e o layout
            pdf_gerado = PdfReader(caminho_relatorio)
            pdf_layout = PdfReader(caminho_layout)
            
            # Criar um novo PDF
            pdf_final = PdfWriter()
            
            # Mesclar cada página do PDF gerado com o layout
            for i, pagina_gerada in enumerate(pdf_gerado.pages):
                # Criar uma cópia da página do layout
                pagina_layout = pdf_layout.pages[0]  # Usar sempre a primeira página do layout
                
                # Mesclar a página do layout com a página do PDF gerado
                pagina_gerada.merge_page(pagina_layout, expand=False)
                
                # Adicionar a página mesclada ao PDF final
                pdf_final.add_page(pagina_gerada)
            
            # Salvar o PDF final
            with open(caminho_relatorio, 'wb') as arquivo_saida:
                pdf_final.write(arquivo_saida)
                
            st.toast("Arquivo PDF gerado e mesclado com sucesso!", icon='🎉')
        except Exception as e:
            st.error(f"Erro ao mesclar PDFs: {str(e)}")
            st.toast("Arquivo PDF gerado sem mesclagem!", icon='⚠️')
        
            