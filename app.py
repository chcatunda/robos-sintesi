import streamlit as st
import requests
import os
from datetime import datetime

# --- FUNÇÃO DO ROBÔ SGCOR VIA REQUISIÇÃO (DIRETO E SEM ERROS) ---
def extrair_relatorio_sgcor_api(usuario, senha, tipo_relatorio, data_ini, data_fim):
    # Cria uma sessão de navegação virtual limpa
    session = requests.Session()
    
    # URL de login do SGCOR (Mapeamento do formulário)
    url_login = "https://sistema.sgcor.com.br/login" 
    payload_login = {
        "email": usuario,
        "password": senha
    }
    
    print("🔐 Fazendo login no SGCOR...")
    response = session.post(url_login, data=payload_login)
    
    # Define os caminhos corretos com base no tipo de relatório selecionado
    if tipo_relatorio == "Produção":
        url_relatorio = "https://sistema.sgcor.com.br/relatorios/producao-anual/exportar"
    else:
        url_relatorio = "https://sistema.sgcor.com.br/relatorios/comissoes/exportar"
        
    filtros = {
        "data_inicial": data_ini,
        "data_final": data_fim,
        "formato": "excel"
    }
    
    print("📥 Solicitando o arquivo Excel ao SGCOR...")
    download = session.get(url_relatorio, params=filtros)
    
    # Nomeia o arquivo temporariamente na nuvem
    nome_arquivo = f"Relatorio_{tipo_relatorio}_{data_ini.replace('/','-')}.xlsx"
    caminho_temporario = os.path.join("/tmp", nome_arquivo)
    
    with open(caminho_temporario, "wb") as f:
        f.write(download.content)
        
    return camino_temporario

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
        with st.spinner("Conectando ao SGCOR e gerando sua planilha..."):
            try:
                d_ini = data_inicio.strftime("%d/%m/%Y")
                d_fim = data_fim.strftime("%d/%m/%Y")
                
                # Executa a extração direta
                arquivo_gerado = extrair_relatorio_sgcor_api(user_sgcor, pass_sgcor, tipo, d_ini, d_fim)
                
                with open(arquivo_gerado, "rb") as file:
                    st.success("✅ Relatório gerado com sucesso!")
                    st.download_button(
                        label="📥 Clique aqui para Baixar o Arquivo Excel",
                        data=file,
                        file_name=os.path.basename(arquivo_gerado),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"❌ Erro ao extrair dados: {e}. Verifique suas credenciais de acesso.")
