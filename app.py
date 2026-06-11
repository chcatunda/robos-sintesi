import streamlit as st
import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# --- FUNÇÃO DO ROBÔ SGCOR OFICIAL PARA NUVEM ---
def executar_download_sgcor(usuario, senha, tipo_relatorio, data_ini, data_fim):
    # Comando crucial: força o servidor do Streamlit a instalar o navegador interno deles
    st.info("Configurando navegadores no servidor... Só um momento...")
    os.system("playwright install chromium")
    
    with sync_playwright() as p:
        # Abre o navegador em modo invisível dentro do servidor
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context()
        page = context.new_page()
        
        # 1. Acessa o SGCOR
        page.goto("https://sistema.sgcor.com.br/login")
        time.sleep(2)
        
        # 2. Faz o Login
        page.fill("input[type='email']", usuario)
        page.fill("input[type='password']", senha)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        
        # 3. Vai para a página de Relatórios
        page.goto("https://sistema.sgcor.com.br/relatorios")
        time.sleep(2)
        
        if tipo_relatorio == "Produção":
            page.click("text=Produção Anual")
        else:
            page.click("text=Extrato de Comissões")
        time.sleep(2)
        
        # 4. Preenche os campos de data
        page.locator("#data_inicial").clear()
        page.locator("#data_inicial").fill(data_ini)
        page.locator("#data_final").clear()
        page.locator("#data_final").fill(data_fim)
        
        # 5. Captura e gerencia o Download que vai cair na nuvem
        pasta_download = "/tmp"
        with page.expect_download() as download_info:
            page.click("button:has-text('Gerar')")
        
        download = download_info.value
        nome_final = f"Relatorio_{tipo_relatorio}_{data_ini.replace('/','-')}.xlsx"
        caminho_salvo = os.path.join(pasta_download, nome_final)
        
        download.save_as(caminho_salvo)
        browser.close()
        
        return caminho_salvo

# --- INTERFACE WEB DO STREAMLIT ---
st.set_page_config(page_title="Sintesi Corretora - SGCOR", page_icon="📊")

st.title("📊 Extrator de Relatórios SGCOR")
st.write("Acesse e baixe seus relatórios direto pelo celular, tablet ou computador.")

tipo = st.selectbox("Qual relatório deseja?", ["Produção", "Comissões"])
data_inicio = st.date_input("Data Inicial", datetime.today())
data_fim = st.date_input("Data Final", datetime.today())

st.divider()
st.subheader("🔑 Credenciais do SGCOR")
user_sgcor = st.text_input("E-mail de Login")
pass_sgcor = st.text_input("Senha de Acesso", type="password")

if st.button("🚀 Disparar Extração SGCOR", use_container_width=True):
    if not user_sgcor or not pass_sgcor:
        st.warning("Por favor, preencha seu usuário e senha do SGCOR.")
    else:
        with st.spinner("O robô está iniciando o navegador e acessando o SGCOR... Aguarde..."):
            try:
                d_ini = data_inicio.strftime("%d/%m/%Y")
                d_fim = data_fim.strftime("%d/%m/%Y")
                
                # Executa a função oficial
                caminho_arquivo = executar_download_sgcor(user_sgcor, pass_sgcor, tipo, d_ini, d_fim)
                
                with open(caminho_arquivo, "rb") as file:
                    st.success("✅ Relatório gerado com sucesso!")
                    st.download_button(
                        label="📥 Clique aqui para Baixar o Arquivo Excel",
                        data=file,
                        file_name=os.path.basename(caminho_arquivo),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"❌ Erro na automação: {e}")
