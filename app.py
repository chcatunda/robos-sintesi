import streamlit as st
import requests
from datetime import datetime

# --- FUNÇÃO DO ROBÔ INTEGRADO SGCOR (NATIVO CSV) ---
def extrair_relatorio_sgcor_csv_nativo(usuario, senha, tipo_relatorio, data_ini, data_fim):
    session = requests.Session()
    
    url_base = "https://sintesi.sgcor.com.br"
    url_login = f"{url_base}/index.php?op=login"
    
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    })
    
    # 1. Captura cookies iniciais de sessão
    session.get(url_base)
    
    payload_login = {
        "username": usuario, 
        "password": senha,
        "op": "login_validar"
    }
    
    # 2. Faz o Login Real
    session.post(url_login, data=payload_login)
    
    # 3. Define as rotas mudando o final para buscar o CSV nativo do SGCOR
    # NOTA: Se no sistema o termo for diferente de 'csv', é só me avisar que ajustamos!
    if tipo_relatorio == "Produção":
        url_relatorio = f"{url_base}/index.php?op=relatorios&form=producao_anual&exportar=csv"
    else:
        url_relatorio = f"{url_base}/index.php?op=relatorios&form=comissoes&exportar=csv"
        
    url_relatorio += f"&data_inicial={data_ini}&data_final={data_fim}"
    
    # 4. Solicita o relatório em formato de texto (CSV)
    download = session.get(url_relatorio)
    
    if "SGCOR - Login" in download.text or download.status_code != 200:
        raise Exception("Erro na autenticação ou sessão expirada. Verifique suas credenciais.")
        
    return download.content

# --- INTERFACE WEB DO STREAMLIT ---
st.set_page_config(page_title="Sintesi Corretora - SGCOR", page_icon="📊")

st.title("📊 Extrator de Relatórios SGCOR")
st.write("Acesse e baixe seus relatórios direto pelo seu navegador.")

tipo = st.selectbox("Qual relatório deseja?", ["Produção", "Comissões"])

data_inicio = st.date_input("Data Inicial", datetime.today())
data_fim = st.date_input("Data Final", datetime.today())

st.divider()
st.subheader("🔑 Credenciais do SGCOR")
user_sgcor = st.text_input("Usuário de Login")
pass_sgcor = st.text_input("Senha de Acesso", type="password")

if st.button("🚀 Disparar Extração SGCOR", use_container_width=True):
    if not user_sgcor or not pass_sgcor:
        st.warning("Por favor, preencha seu usuário e senha do SGCOR.")
    else:
        with st.spinner("Conectando ao SGCOR da Sintesi e baixando o CSV..."):
            try:
                d_ini = data_inicio.strftime("%d/%m/%Y")
                d_fim = data_fim.strftime("%d/%m/%Y")
                
                conteudo_csv = extrair_relatorio_sgcor_csv_nativo(user_sgcor, pass_sgcor, tipo, d_ini, d_fim)
                
                nome_final = f"Relatorio_{tipo}_{d_ini.replace('/','-')}_a_{d_fim.replace('/','-')}.csv"
                
                st.success("✅ Relatório extraído com sucesso!")
                
                # Entrega o arquivo CSV legítimo enviado pelo sistema
                st.download_button(
                    label="📥 Clique aqui para Baixar o Arquivo CSV",
                    data=conteudo_csv,
                    file_name=nome_final,
                    mime="text/csv",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Ocorreu um problema: {e}")
