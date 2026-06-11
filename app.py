import streamlit as st
import os
from datetime import datetime

# Instalação automática do navegador para não dar erro no Linux do Streamlit
try:
    import playwright
except ImportError:
    os.system("pip install playwright")
os.system("playwright install chromium")

from playwright.sync_api import sync_playwright

# --- CONFIGURAÇÃO DA SINTESI ---
URL_SGCOR_SINTESI = "https://sintesi.sgcor.com.br"

# --- FUNÇÃO DO ROBÔ NAVEGADOR ---
def executar_download_sgcor(usuario, senha, tipo_relatorio, data_ini, data_fim):
    with sync_playwright() as p:
        # Abre o navegador real em segundo plano com tamanho padrão de tela
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        
        # 1. Acessa a tela de login da Sintesi
        page.goto(f"{URL_SGCOR_SINTESI}/login")
        page.wait_for_load_state("networkidle")
        
        # 2. Preenche os campos de Usuário e Senha exatamente como você faz no teclado
        page.fill("input[name='email']", usuario)
        page.fill("input[name='password']", senha)
        
        # 3. Clica no botão de Entrar
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        
        # Se o login falhar, avisa na tela
        if "/login" in page.url:
            browser.close()
            raise Exception("Falha no login. Verifique se o seu usuário ou a senha estão corretos.")
        
        # 4. Navega direto para a página do relatório selecionado
        if tipo_relatorio == "Produção":
            url_relatorio = f"{URL_SGCOR_SINTESI}/relatorios/producao-anual"
        else:
            url_relatorio = f"{URL_SGCOR_SINTESI}/relatorios/comissoes"
            
        page.goto(url_relatorio)
        page.wait_for_load_state("networkidle")
        
        # 5. Preenche os campos de data
        page.fill("input[name='data_inicial']", data_ini)
        page.fill("input[name='data_final']", data_fim)
        
        # 6. Captura o download do Excel gerado pelo SGCOR
        with page.expect_download() as download_info:
            # Clica no botão que gera a planilha (Exportar ou Gerar)
            page.click("button:has-text('Exportar'), button:has-text('Gerar'), input[type='submit']")
            
        download = download_info.value
        
        # Salva temporariamente no servidor
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
        with st.spinner("Abrindo navegador virtual, fazendo login no SGCOR e gerando sua planilha..."):
            try:
                d_ini = data_inicio.strftime("%d/%m/%Y")
                d_fim = data_fim.strftime("%d/%m/%Y")
                
                # Executa o robô navegador real
                arquivo_gerado = executar_download_sgcor(user_sgcor, pass_sgcor, tipo, d_ini, d_fim)
                
                with open(arquivo_gerado, "rb") as file:
                    st.success("✅ Relatório gerado com sucesso!")
                    st.write("👉 Clique no botão abaixo para baixar seu arquivo formatado:")
                    st.download_button(
                        label="📥 Clique aqui para Baixar o Arquivo Excel",
                        data=file,
                        file_name="RELAÇAO DE CLIENTES ATIVOS.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"❌ Erro na automação: {e}")
