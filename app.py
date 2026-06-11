import streamlit as st
import requests
import io
from datetime import datetime

# --- FUNÇÃO DO ROBÔ SGCOR VIA REQUISIÇÃO DIRETA NA MEMÓRIA ---
def extrair_relatorio_sgcor_api(usuario, senha, tipo_relatorio, data_ini, data_fim):
    # Cria uma sessão de navegação virtual limpa
    session = requests.Session()
    
    # Descobre o domínio correto do SGCOR com base no e-mail digitado
    dominio_base = "sgcor.com.br"
    if "@" in usuario:
        empresa = usuario.split("@")[1].split(".")[0]
        # Se for um e-mail corporativo (não comercial), tenta o subdomínio correspondente
        if empresa not in ["gmail", "outlook", "hotmail", "yahoo", "live"]:
            dominio_base = f"{empresa}.sgcor.com.br"

    # URL de login ajustada dinamicamente
    url_login = f"https://{dominio_base}/login" 
    payload_login = {
        "email": usuario,
        "password": senha
    }
    
    # Realiza o Login no sistema da corretora
    response = session.post(url_login, data=payload_login)
    
    # Define as URLs dos relatórios com base no tipo selecionado
    if tipo_relatorio == "Produção":
        url_relatorio = f"https://{dominio_base}/relatorios/producao-anual/exportar"
    else:
        url_relatorio = f"https://{dominio_base}/relatorios/comissoes/exportar"
        
    filtros = {
        "data_inicial": data_ini,
        "data_final": data_fim,
        "formato": "excel"
    }
    
    # Solicita o download e guarda o conteúdo direto na memória (evita travar o disco local)
    download = session.get(url_relatorio, params=filtros)
    
    if download.status_code != 200:
        raise Exception("Não foi possível conectar ao SGCOR. Verifique se o e-mail ou a senha estão corretos.")
        
    return download.content

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
                
                # Executa a extração direto para a memória do navegador
                conteudo_excel = extrair_relatorio_sgcor_api(user_sgcor, pass_sgcor, tipo, d_ini, d_fim)
                
                nome_final = f"Relatorio_{tipo}_{d_ini.replace('/','-')}.xlsx"
                
                st.success("✅ Relatório gerado com sucesso!")
                st.download_button(
                    label="📥 Clique aqui para Baixar o Arquivo Excel",
                    data=conteudo_excel,
                    file_name=nome_final,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ {e}")
