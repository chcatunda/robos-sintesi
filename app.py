import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# --- CONFIGURAÇÃO DEFINITIVA DA SINTESI ---
URL_SGCOR_SINTESI = "https://sintesi.sgcor.com.br"

# --- FUNÇÃO DO ROBÔ SGCOR COM COLETA DE SEGURANÇA (CSRF) ---
def extrair_relatorio_sgcor_api(usuario, senha, tipo_relatorio, data_ini, data_fim):
    # Cria uma sessão que guarda os cookies de navegação como um navegador real
    session = requests.Session()
    
    # Configura o robô para se disfarçar de um navegador comum (Chrome)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": URL_SGCOR_SINTESI
    })
    
    # PASSO 1: Entra na página de login para capturar os tokens de segurança obrigatórios do SGCOR
    url_login_tela = f"{URL_SGCOR_SINTESI}/login"
    reposta_tela = session.get(url_login_tela)
    
    # Procura por campos ocultos de segurança (como _token ou csrf) na página do SGCOR
    soup = BeautifulSoup(reposta_tela.text, 'html.parser')
    token_oculto = soup.find('input', {'name': '_token'})
    token_valor = token_oculto['value'] if token_oculto else ''
    
    # PASSO 2: Monta o formulário de login idêntico ao que o SGCOR exige
    payload_login = {
        "_token": token_valor, # Código de segurança injetado
        "email": usuario,
        "usuario": usuario,
        "login": usuario,
        "password": senha,
        "senha": senha
    }
    
    # Realiza o Login enviando a segurança junto
    resposta_login = session.post(url_login_tela, data=payload_login)
    
    # PASSO 3: Mapeamento dos links de exportação da Sintesi
    if tipo_relatorio == "Produção":
        url_relatorio = f"{URL_SGCOR_SINTESI}/relatorios/producao-anual/exportar"
    else:
        url_relatorio = f"{URL_SGCOR_SINTESI}/relatorios/comissoes/exportar"
        
    filtros = {
        "data_inicial": data_ini,
        "data_final": data_fim,
        "formato": "excel"
    }
    
    # Solicita o download do relatório
    download = session.get(url_relatorio, params=filtros)
    
    # Se o SGCOR recusar, avisa o motivo exato
    if download.status_code != 200:
        raise Exception("O SGCOR recusou o acesso. Certifique-se de que o painel está aberto no seu computador ou tente novamente.")
        
    return download.content

# --- INTERFACE WEB DO STREAMLIT ---
st.set_page_config(page_title="Sintesi Corretora - SGCOR", page_icon="📊")

st.title("📊 Extrator de Relatórios SGCOR")
st.write("Acesse e baixe seus relatórios direto pelo celular, tablet ou computador.")

st.divider()
st.subheader("📋 Configuração do Relatório")
tipo = st.selectbox("Qual relatório deseja?", ["Produção", "Comissões"])
data_inicio = st.date_input("Data Inicial", datetime.today())
data_fim = st.date_input("Data Final", datetime.today())

st.divider()
st.subheader("🔑 Credenciais de Acesso")
user_sgcor = st.text_input("Usuário / Login (Código, CPF ou Usuário normal)")
pass_sgcor = st.text_input("Senha de Acesso", type="password")

st.divider()
if st.button("🚀 Disparar Extração SGCOR", use_container_width=True):
    if not user_sgcor or not pass_sgcor:
        st.warning("Por favor, preencha seu usuário e senha do SGCOR.")
    else:
        with st.spinner("Conectando ao SGCOR de forma segura e gerando sua planilha..."):
            try:
                d_ini = data_inicio.strftime("%d/%m/%Y")
                d_fim = data_fim.strftime("%d/%m/%Y")
                
                # Executa a extração simulando o navegador real
                conteudo_excel = extrair_relatorio_sgcor_api(user_sgcor, pass_sgcor, tipo, d_ini, d_fim)
                
                nome_final = "RELAÇAO DE CLIENTES ATIVOS.xlsx"
                
                st.success("✅ Relatório gerado com sucesso!")
                st.write("👉 Clique no botão abaixo para baixar. Depois, basta arrastar o arquivo para dentro da sua pasta do Google Drive!")
                
                st.download_button(
                    label="📥 Clique aqui para Baixar o Arquivo Excel",
                    data=conteudo_excel,
                    file_name=nome_final,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ {e}")
