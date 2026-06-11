import streamlit as st
import requests
from datetime import datetime

# --- FUNÇÃO DO ROBÔ INTEGRADO SGCOR (MÉTODO REFORÇADO) ---
def extrair_relatorio_sgcor_csv_nativo(usuario, senha, tipo_relatorio, data_ini, data_fim):
    session = requests.Session()
    
    url_base = "https://sintesi.sgcor.com.br"
    url_login = f"{url_base}/index.php?op=login"
    
    # Headers completos idênticos ao do navegador para o servidor não desconfiar
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": url_base,
        "Referer": url_base
    })
    
    # 1. Abre a página inicial para pegar o cookie de sessão limpo
    resposta_inicial = session.get(url_base)
    
    # 2. Dados de login idênticos ao script do Google que funcionou
    payload_login = {
        "username": str(usuario).strip(), 
        "password": str(senha).strip(),
        "op": "login_validar"
    }
    
    # 3. Faz o POST de login
    resposta_login = session.post(url_login, data=payload_login, allow_redirects=True)
    
    # Se na página de resposta ainda aparecer a tela de login, é porque a senha/user falhou
    if "op=login" in resposta_login.url or "SGCOR - Login" in resposta_login.text:
        raise Exception("O SGCOR recusou o acesso. Verifique se digitou o Usuário e Senha corretamente.")
    
    # 4. Define as rotas do relatório nativo em CSV
    if tipo_relatorio == "Produção":
        url_relatorio = f"{url_base}/index.php?op=relatorios&form=producao_anual&exportar=csv"
    else:
        url_relatorio = f"{url_base}/index.php?op=relatorios&form=comissoes&exportar=csv"
        
    url_relatorio += f"&data_inicial={data_ini}&data_final={data_fim}"
    
    # 5. Solicita o download do arquivo CSV
    download = session.get(url_relatorio)
    
    if download.status_code != 200:
        raise Exception(f"Erro no servidor do SGCOR ao buscar o relatório. Status: {download.status_code}")
        
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
user_sgcor = "chcatunda"
pass_sgcor = "Cretapoi@8755"

if st.button("🚀 Disparar Extração SGCOR", use_container_width=True):
    if not user_sgcor or not pass_sgcor:
        st.warning("Por favor, preencha seu usuário e senha do SGCOR.")
    else:
        with st.spinner("Conectando ao SGCOR da Sintesi e baixando o arquivo..."):
            try:
                d_ini = data_inicio.strftime("%d/%m/%Y")
                d_fim = data_fim.strftime("%d/%m/%Y")
                
                conteudo_csv = extrair_relatorio_sgcor_csv_nativo(user_sgcor, pass_sgcor, tipo, d_ini, d_fim)
                
                nome_final = f"Relatorio_{tipo}_{d_ini.replace('/','-')}_a_{d_fim.replace('/','-')}.csv"
                
                st.success("✅ Relatório extraído com sucesso!")
                
                st.download_button(
                    label="📥 Clique aqui para Baixar o Arquivo CSV",
                    data=conteudo_csv,
                    file_name=nome_final,
                    mime="text/csv",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Ocorreu um problema: {e}")
