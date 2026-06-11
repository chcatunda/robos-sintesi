import streamlit as st
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- FUNÇÃO DO ROBÔ SGCOR COM NAVEGADOR VIRTUAL ---
def executar_download_sgcor(usuario, senha, tipo_relatorio, data_ini, data_fim):
    # Configurações para o navegador rodar escondido na nuvem
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Pasta temporária para salvar o arquivo na nuvem
    pasta_download = "/tmp"
    prefs = {"download.default_directory": pasta_download}
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Inicia o navegador
    servico = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servico, options=chrome_options)
    
    try:
        # 1. Acessa o site oficial do SGCOR
        driver.get("https://sistema.sgcor.com.br/login")
        time.sleep(3)
        
        # 2. Preenche os dados de Login
        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(usuario)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(senha)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(5)
        
        # 3. Navega até a área de Relatórios
        driver.get("https://sistema.sgcor.com.br/relatorios")
        time.sleep(3)
        
        if tipo_relatorio == "Produção":
            driver.find_element(By.LINK_TEXT, "Produção Anual").click()
        else:
            driver.find_element(By.LINK_TEXT, "Extrato de Comissões").click()
        time.sleep(3)
        
        # 4. Preenche os filtros de data
        driver.find_element(By.ID, "data_inicial").clear()
        driver.find_element(By.ID, "data_inicial").send_keys(data_ini)
        driver.find_element(By.ID, "data_final").clear()
        driver.find_element(By.ID, "data_final").send_keys(data_fim)
        
        # 5. Clica para Gerar e aguarda o download
        driver.find_element(By.XPATH, "//button[contains(text(), 'Gerar')]").click()
        time.sleep(8) # Tempo para o SGCOR criar o Excel
        
        # Identifica o arquivo gerado na pasta
        arquivos = os.listdir(pasta_download)
        arquivo_excel = None
        for arq in arquivos:
            if arq.endswith(".xlsx") or arq.endswith(".xls"):
                arquivo_excel = os.path.join(pasta_download, arq)
                break
                
        if not arquivo_excel:
            raise Exception("O SGCOR não gerou o arquivo a tempo. Verifique os dados ou tente novamente.")
            
        return arquivo_excel

    finally:
        driver.quit()

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
        with st.spinner("O robô está abrindo o SGCOR e gerando sua planilha... Aguarde..."):
            try:
                d_ini = data_inicio.strftime("%d/%m/%Y")
                d_fim = data_fim.strftime("%d/%m/%Y")
                
                # Executa o robô navegador
                caminho_arquivo = executar_download_sgcor(user_sgcor, pass_sgcor, tipo, d_ini, d_fim)
                
                nome_final = f"Relatorio_{tipo}_{d_ini.replace('/','-')}.xlsx"
                
                with open(caminho_arquivo, "rb") as file:
                    st.success("✅ Relatório gerado com sucesso!")
                    st.download_button(
                        label="📥 Clique aqui para Baixar o Arquivo Excel",
                        data=file,
                        file_name=nome_final,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"❌ Erro na automação: {e}")
