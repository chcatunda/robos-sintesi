import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# --- CONFIGURAÇÃO DEFINITIVA DA SINTESI ---
URL_SGCOR_SINTESI = "https://sintesi.sgcor.com.br"

# --- FUNÇÃO DO ROBÔ VIA REQUISIÇÃO COM COOKIES INTELIGENTES ---
def extrair_relatorio_sgcor_api(usuario, senha, tipo_relatorio, data_ini, data_fim):
    # Cria uma sessão que imita o comportamento de salvar cookies de um navegador real
    session = requests.Session()
    
    # Se disfarça completamente de um navegador Google Chrome atualizado
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": f"{URL_SGCOR_SINTESI}/login"
    })
    
    # PASSO 1: Abre a página de login para capturar o token de segurança oculto (CSRF)
    url_tela_login = f"{URL_SGCOR_SINTESI}/login"
    resposta_tela = session.get(url_tela_login)
    
    # Varre a página procurando pelo código de segurança do SGCOR
    soup = BeautifulSoup(resposta_tela.text, 'html.parser')
    token_oculto = soup.find('input', {'name': '_token'})
    token_valor = token_oculto['value'] if token_oculto else ''
    
    # PASSO 2: Prepara os dados de login exatamente no formato que o formulário do SGCOR pede
    payload_login = {
        "_token": token_valor,
        "email": usuario,        # O SGCOR pode ler o campo como email ou usuário
        "usuario": usuario,
        "password": senha
    }
    
    # Envia os dados para efetuar o login e validar a sessão
    resposta_login = session.post(url_tela_login, data=payload_login)
    
    # PASSO 3: Mapeia o link de exportação do Excel dentro da Sintesi
    if tipo_relatorio == "Produção":
        url_exportar = f"{URL_SGCOR_SINTESI}/relatorios/producao-anual/exportar"
    else:
        url_exportar = f"{URL_SGCOR_SINTESI}/relatorios/comissoes/exportar"
        
    # Parâmetros de filtro que você selecionou na tela
    filtros = {
        "data_inicial": data_ini,
        "data_final": data_fim,
        "formato": "excel"
    }
    
    # PASSO 4: Solicita o download do arquivo usando a sessão autenticada
    download = session.get(url_exportar, params=filtros)
    
    # Se o download falhar ou voltar para a tela de login, significa erro de credenciais
    if download.status_code != 200 or "login" in download.url:
        raise Exception("O SGCOR recusou o acesso. Certifique-se de que seu Usuário e Senha estão corretos e tente novamente.")
        
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
user_sgcor = st.text_input("Usuário / Login (Código, CPF ou Login normal)")
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
                
                # Executa a extração direta ultra-rápida
                conteudo_excel = extrair_relatorio_sgcor_api(user_sgcor, pass_sgcor, tipo, d_ini, d_fim)
                
                # Define o nome que você solicitou para salvar no Drive
                nome_final = "RELAÇAO DE CLIENTES ATIVOS.xlsx"
                
                st.success("✅ Relatório gerado com sucesso!")
                st.write("👉 Clique no botão abaixo para baixar seu arquivo formatado. Depois, basta jogá-lo no seu Google Drive!")
                
                st.download_button(
                    label="📥 Clique aqui para Baixar o Arquivo Excel",
                    data=conteudo_excel,
                    file_name=nome_final,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ {e}")
