import streamlit as st
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

# --- FUNÇÃO DO ROBÔ SGCOR ---
def executar_download_sgcor(usuario, senha, tipo_relatorio, data_ini, data_fim):
    # Força a instalação dos navegadores antes de abrir para não dar erro na nuvem
    os.system("playwright install chromium")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Acessa o SGCOR
        page.goto("https://sistema.sgcor.com.br/") 
        
        # Login
        page.fill("input[type='email']", usuario)
        page.fill("input[type='password']", senha)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        
        # Navegação no Menu do SGCOR
        page.click("text=Relatórios")
        if tipo_relatorio == "Produção":
            page.click("text=Produção Anual")
        elif tipo_relatorio == "Comissões":
            page.click("text=Extrato de Comissões")
            
        # Filtro de Datas
        page.fill("#data_inicial", data_ini)
        page.fill("#data_final", data_fim)
        
        # Captura o Download na Nuvem
        with page.expect_download() as download_info:
            page.click("button:has-text('Gerar')") 
            
        download = download_info.value
        nome_final = f"Relatorio_{tipo_relatorio}_{data_ini.replace('/','-')}.xlsx"
        
        caminho_temporario = os.path.join("/tmp", nome_final)
        download.save_as(caminho_temporario)
        browser.close()
        
        return caminho_temporario

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

if st.button("🚀 Disparar Robô SGCOR", use_container_width=True):
    if not user_sgcor or not pass_sgcor:
        st.warning("Por favor, preencha seu usuário e senha do SGCOR.")
    else:
        with st.spinner("O robô está navegando no SGCOR... Aguarde..."):
            try:
                d_ini = data_inicio.strftime("%d/%m/%Y")
                d_fim = data_fim.strftime("%d/%m/%Y")
                
                arquivo_gerado = executar_download_sgcor(user_sgcor, pass_sgcor, tipo, d_ini, d_fim)
                
                with open(arquivo_gerado, "rb") as file:
                    st.success("✅ Relatório gerado com sucesso!")
                    st.download_button(
                        label="📥 Clique aqui para Baixar o Arquivo Excel",
                        data=file,
                        file_name=os.path.basename(arquivo_gerado),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"❌ Erro na automação: {e}. Verifique se os dados estão corretos.")
