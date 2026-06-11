import streamlit as st
import os
import time
from datetime import datetime

# Configuração e instalação automática do navegador portátil para a nuvem
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURAÇÃO DA SINTESI ---
URL_SGCOR_SINTESI = "https://sintesi.sgcor.com.br"

# --- FUNÇÃO DO ROBÔ NAVEGADOR COM SELENIUM ---
def executar_download_sgcor(usuario, senha, tipo_relatorio, data_ini, data_fim):
    # Configura o navegador para rodar de forma ultra-leve e sem interface gráfica
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Define a pasta de downloads temporária dentro do servidor
    pasta_download = "/tmp"
    prefs = {"download.default_directory": pasta_download}
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Inicializa o navegador portátil
    servico = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servico, options=chrome_options)
    
    try:
        # 1. Acessa a tela de login da Sintesi
        driver.get(f"{URL_SGCOR_SINTESI}/login")
        time.sleep(3)
        
        # 2. Preenche Usuário e Senha
        driver.find_element(By.NAME, "email").send_keys(usuario)
        driver.find_element(By.NAME, "password").send_keys(senha)
        
        # 3. Clica no botão de Entrar
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(5)
        
        # Se o login falhar, avisa na tela
        if "/login" in driver.current_url:
            raise Exception("Falha no login. Verifique se o seu usuário ou a senha estão corretos no SGCOR.")
            
        # 4. Vai direto para a página do relatório selecionado
        if tipo_relatorio == "Produção":
            url_relatorio = f"{URL_SGCOR_SINTESI}/relatorios/producao-anual"
        else:
            url_relatorio = f"{URL_SGCOR_SINTESI}/relatorios/comissoes"
            
        driver.get(url_relatorio)
        time.sleep(4)
        
        # 5. Preenche os campos de data
        driver.find_element(By.NAME, "data_inicial").clear()
        driver.find_element(By.NAME, "data_inicial").send_keys(data_ini)
        driver.find_element(By.NAME, "data_final").clear()
        driver.find_element(By.NAME, "data_final").send_keys(data_fim)
        
        # 6. Dispara o download clicando no botão gerador
        # Procura por botões comuns do SGCOR como "Exportar" ou "Gerar"
        botoes = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
        clicou = False
        for botao in botoes:
            texto = botao.text or botao.get_attribute("value")
            if texto and any(palavra in texto.lower() for palabra in ["exportar", "gerar"]):
                botao.click()
                clicou = True
                break
                
        if not clicou:
            # Clique de segurança caso não ache pelo texto
            driver.find_element(By.CSS_SELECTOR, "form button, form input[type='submit']").click()
            
        # Aguarda o download ser processado pelo servidor
        time.sleep(6)
        
        caminho_final = os.path.join(pasta_download, "RELAÇAO DE CLIENTES ATIVOS.xlsx")
        
        # Como o SGCOR gera nomes variados, procura o arquivo baixado na pasta /tmp
        arquivos = os.listdir(pasta_download)
        for arquivo in arquivos:
            if arquivo.endswith(".xlsx"):
                os.rename(os.path.join(pasta_download, arquivo), caminho_final)
                break
                
        driver.quit()
        return caminho_final
        
    except Exception as e:
        driver.quit()
        raise e

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
        with st.spinner("Conectando de forma portátil ao SGCOR da Sintesi... Aguarde..."):
            try:
                d_ini = data_inicio.strftime("%d/%m/%Y")
                d_fim = data_fim.strftime("%d/%m/%Y")
                
                # Executa o novo robô portátil
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
