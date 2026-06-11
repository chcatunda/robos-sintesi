import streamlit as st
import os
import time
from datetime import datetime
from DrissionPage import ChromiumOptions, ChromiumPage

# --- FUNÇÃO DO ROBÔ SGCOR COM NAVEGADOR ULTRA LEVE ---
def executar_download_sgcor(usuario, senha, tipo_relatorio, data_ini, data_fim):
    # Configura o navegador para rodar em modo invisível (headless) na nuvem
    co = ChromiumOptions()
    co.set_argument('--headless')
    co.set_argument('--no-sandbox')
    
    # Pasta temporária para salvar o arquivo Excel
    pasta_download = "/tmp"
    co.set_paths(download_path=pasta_download)
    
    # Inicializa o navegador virtual
    page = ChromiumPage(co)
    
    try:
        # 1. Acessa a página de login do SGCOR
        page.get("https://sistema.sgcor.com.br/login")
        time.sleep(2)
        
        # 2. Preenche o e-mail e a senha nos campos corretos
        page.ele("css:input[type='email']").input(usuario)
        page.ele("css:input[type='password']").input(senha)
        
        # 3. Clica no botão de Entrar
        page.ele("css:button[type='submit']").click()
        time.sleep(4)
        
        # 4. Vai direto para a página de relatórios
        page.get("https://sistema.sgcor.com.br/relatorios")
        time.sleep(2)
        
        if tipo_relatorio == "Produção":
            page.ele("text:Produção Anual").click()
        else:
            page.ele("text:Extrato de Comissões").click()
        time.sleep(2)
        
        # 5. Preenche as datas dos filtros
        page.ele("#data_inicial").clear()
        page.ele("#data_inicial").input(data_ini)
        page.ele("#data_final").clear()
        page.ele("#data_final").input(data_fim)
        
        # 6. Dispara o botão para Gerar e aguarda o download concluir
        page.ele("xpath://button[contains(text(), 'Gerar')]").click()
        time.sleep(7)
        
        # Procura o arquivo .xlsx gerado na pasta temporária
        arquivos = os.listdir(pasta_download)
        arquivo_excel = None
        for arq in arquivos:
            if arq.endswith(".xlsx") or arq.endswith(".xls"):
                arquivo_excel = os.path.join(pasta_download, arq)
                break
                
        if not arquivo_excel:
            raise Exception("O SGCOR demorou a responder ou os dados de login estão incorretos.")
            
        return arquivo_excel

    finally:
        page.quit()

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
        with st.spinner("O robô está abrindo o SGCOR e recolhendo a sua planilha... Aguarde..."):
            try:
                d_ini = data_inicio.strftime("%d/%m/%Y")
                d_fim = data_fim.strftime("%d/%m/%Y")
                
                # Executa o robô navegador invisível
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
                st.error(f"❌ Status do Robô: {e}")
