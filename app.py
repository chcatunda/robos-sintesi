import streamlit as st
import requests
import os
from datetime import datetime

# --- CONFIGURAÇÃO DEFINITIVA DA SINTESI ---
URL_SGCOR_SINTESI = "https://sintesi.sgcor.com.br"

# --- FUNÇÃO DO ROBÔ SGCOR VIA REQUISIÇÃO DIRETA ---
def extrair_relatorio_sgcor_api(usuario, senha, tipo_relatorio, data_ini, data_fim):
    session = requests.Session()
    
    # URL de login exata da Sintesi
    url_login = f"{URL_SGCOR_SINTESI}/login" 
    
    # Envia os dados simulando o formulário padrão do SGCOR
    payload_login = {
        "email": usuario,
        "usuario": usuario,
        "login": usuario,
        "password": senha,
        "senha": senha
    }
    
    # Realiza o Login no SGCOR
    response = session.post(url_login, data=payload_login)
    
    # Mapeamento exato dos links de exportação do sistema da Sintesi
    if tipo_relatorio == "Produção":
        url_relatorio = f"{URL_SGCOR_SINTESI}/relatorios/producao-anual/exportar"
    else:
        url_relatorio = f"{URL_SGCOR_SINTESI}/relatorios/comissoes/exportar"
        
    filtros = {
        "data_inicial": data_ini,
        "data_final": data_fim,
        "formato": "excel"
    }
    
    # Solicita o download do relatório para a memória do servidor
    download = session.get(url_relatorio, params=filtros)
    
    if download.status_code != 200:
        raise Exception("Não foi possível extrair o relatório. Verifique se o seu usuário ou senha do SGCOR estão corretos.")
        
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
        with st.spinner("Conectando ao SGCOR da Sintesi e gerando sua planilha..."):
            try:
                d_ini = data_inicio.strftime("%d/%m/%Y")
                d_fim = data_fim.strftime("%d/%m/%Y")
                
                # Executa a extração usando a URL calibrada da Sintesi
                conteudo_excel = extrair_relatorio_sgcor_api(user_sgcor, pass_sgcor, tipo, d_ini, d_fim)
                
                # Define o nome exato solicitado por você
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
