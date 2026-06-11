import streamlit as st
import requests
from datetime import datetime

# --- FUNÇÃO DO ROBÔ INTEGRADO SGCOR (MÉTODO ORIGINAL QUE FUNCIONOU) ---
def extrair_relatorio_sgcor_direto(usuario, senha, tipo_relatorio, data_ini, data_fim):
    session = requests.Session()
    
    url_base = "https://sintesi.sgcor.com.br"
    url_login = f"{url_base}/index.php?op=login"
    
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Origin": url_base,
        "Referer": url_base
    })
    
    # 1. Captura a página inicial para cookies (Exatamente como o primeiro código)
    session.get(url_base)
    
    # 2. Payload original que deu certo
    payload_login = {
        "username": usuario,
        "password": senha,
        "op": "login_validar"
    }
    
    # 3. Faz o Login original
    session.post(url_login, data=payload_login)
    
    # 4. Define as rotas internas mudando para a exportação nativa em CSV
    if tipo_relatorio == "Produção":
        url_relatorio = f"{url_base}/index.php?op=relatorios&form=producao_anual&exportar=csv"
    else:
        url_relatorio = f"{url_base}/index.php?op=relatorios&form=comissoes&exportar=csv"
        
    url_relatorio += f"&data_inicial={data_ini}&data_final={data_fim}"
    
    # 5. Solicita a planilha
    download = session.get(url_relatorio)
    
    if download.status_code != 200:
        raise Exception("Não foi possível conectar ao SGCOR para gerar o relatório.")
        
    return download.content

# --- INTERFACE WEB DO STREAMLIT ---
st.set_page_config(page_title="Sintesi Corretora - SGCOR", page_icon="📊")

st.title("📊 Extrator de Relatórios SGCOR")
st.write("Aceda e descarregue os seus relatórios direto pelo seu navegador.")

tipo = st.selectbox("Qual relatório deseja?", ["Produção", "Comissões"])

data_inicio = st.date_input("Data Inicial", datetime.today())
data_fim = st.date_input("Data Final", datetime.today())

st.divider()
st.subheader("🔑 Credenciais do SGCOR")

# 🔒 CREDENCIAIS CONFIGURADAS DIRETAMENTE NO SISTEMA:
user_sgcor = "chcatunda"
pass_sgcor = "Cretapoi@8755"

st.info("🔒 Os seus dados de acesso já estão configurados no robô.")

if st.button("🚀 Disparar Extração SGCOR", use_container_width=True):
    with st.spinner("A conectar ao SGCOR da Sintesi e a preparar o seu arquivo..."):
        try:
            d_ini = data_inicio.strftime("%d/%m/%Y")
            d_fim = data_fim.strftime("%d/%m/%Y")
            
            # Executa a extração com o método antigo de login
            conteudo_csv = extrair_relatorio_sgcor_direto(user_sgcor, pass_sgcor, tipo, d_ini, d_fim)
            
            nome_final = f"Relatorio_{tipo}_{d_ini.replace('/','-')}_a_{d_fim.replace('/','-')}.csv"
            
            st.success("✅ Relatório gerado com sucesso!")
            
            # Botão configurado estritamente para o formato CSV que você precisa
            st.download_button(
                label="📥 Clique aqui para Baixar o Arquivo CSV",
                data=conteudo_csv,
                file_name=nome_final,
                mime="text/csv",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"❌ Ocorreu um problema: {e}")
