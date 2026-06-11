import streamlit as st
import os
import subprocess
from datetime import datetime

# Garante a instalação do navegador Chromium no servidor antes de iniciar
try:
    import playwright
except ImportError:
    subprocess.run(["pip", "install", "playwright"])
    
# Comando oficial do Playwright para baixar o navegador correto com suas dependências Linux
if not os.path.exists("/home/appuser/.cache/ms-playwright"):
    subprocess.run(["playwright", "install", "chromium"])

from playwright.sync_api import sync_playwright

# --- CONFIGURAÇÃO DEFINITIVA DA SINTESI ---
URL_SGCOR_SINTESI = "https://sintesi.sgcor.com.br"

# --- FUNÇÃO DO ROBÔ NAVEGADOR (PLAYWRIGHT REAL) ---
def executar_download_sgcor(usuario, senha, tipo_relatorio, data_ini, data_fim):
    with sync_playwright() as p:
        # Lança o navegador ignorando restrições de sandbox do Linux da nuvem
        browser = p.chromium.launch(
            headless=True, 
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # 1. Abre a tela de login real da Sintesi
        page.goto(f"{URL_SGCOR_SINTESI}/login", wait_until="networkidle")
        
        # 2. Preenche os campos simulando a digitação humana
        page.fill("input[name='email']", usuario)
        page.fill("input[name='password']", senha)
        
        # 3. Clica no botão de entrar e aguarda a autenticação
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        
        # Se continuar na página de login, o SGCOR barrou a senha/usuário
        if "/login" in page.url:
            browser.close()
            raise Exception("Falha no login do SGCOR. Certifique-se de que o usuário (código/CPF) e a senha estão corretos.")
        
        # 4. Vai direto para a página interna de exportação do relatório selecionado
        if tipo_relatorio == "Produção":
            url_alvo = f"{URL_SGCOR_SINTESI}/relatorios/producao-anual"
        else:
            url_alvo = f"{URL_SGCOR_SINTESI}/relatorios/comissoes"
            
        page.goto(url_alvo, wait_until="networkidle")
        
        # 5. Preenche as datas nos filtros da tela do SGCOR
        page.fill("input[name='data_inicial']", data_ini)
        page.fill("input[name='data_final']", data_fim)
        
        # 6. Escuta o gatilho de download e força a geração da planilha Excel
        with page.expect_download() as download_info:
            # Encontra e clica no botão gerador por texto ou tipo
            page.click("button:has-text('Exportar'), button:has-text('Gerar'), input[type='submit']")
            
        download = download_info.value
        
        # Caminho temporário seguro dentro da nuvem
        caminho_temporario = os.path.join("/tmp", "RELAÇAO DE CLIENTES ATIVOS.xlsx")
        download.save_as(caminho_temporario)
        
        browser.close()
        return caminho_temporario

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
        with st.spinner("Abrindo navegador virtual seguro, fazendo login e extraindo seu relatório..."):
            try:
                d_ini = data_inicio.strftime("%d/%m/%Y")
                d_fim = data_fim.strftime("%d/%m/%Y")
                
                # Dispara a automação pelo navegador real simulado
                arquivo_gerado = executar_download_sgcor(user_sgcor, pass_sgcor, tipo, d_ini, d_fim)
                
                with open(arquivo_gerado, "rb") as file:
                    st.success("✅ Relatório gerado com sucesso!")
                    st.write("👉 Clique no botão abaixo para baixar. Depois, basta arrastar para sua pasta do Google Drive!")
                    st.download_button(
                        label="📥 Clique aqui para Baixar o Arquivo Excel",
                        data=file,
                        file_name="RELAÇAO DE CLIENTES ATIVOS.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"❌ Erro na automação: {e}")
