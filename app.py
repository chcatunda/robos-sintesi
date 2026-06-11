import streamlit as st
import requests
import re
from datetime import datetime

# --- FUNÇÃO DO ROBÔ INTEGRADO SGCOR (CORRIGIDA PARA EXCEL) ---
def extrair_relatorio_sgcor_direto(usuario, senha, tipo_relatorio, data_ini, data_fim):
    session = requests.Session()
    
    # Endereço oficial da Sintesi que você me passou
    url_base = "https://sintesi.sgcor.com.br"
    url_login = f"{url_base}/index.php?op=login"
    
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Origin": url_base,
        "Referer": url_base
    })
    
    # 1. Captura a página inicial paracookies
    resposta_inicial = session.get(url_base)
    
    payload_login = {
        "username": usuario, # Ajustado para username conforme você lembrou
        "password": senha,
        "op": "login_validar"
    }
    
    # 2. Faz o Login
    resposta_autenticacao = session.post(url_login, data=payload_login)
    
    # 3. Define as rotas internas de exportação baseadas no link da Sintesi
    if tipo_relatorio == "Produção":
        url_relatorio = f"{url_base}/index.php?op=relatorios&form=producao_anual&exportar=excel"
    else:
        url_relatorio = f"{url_base}/index.php?op=relatorios&form=comissoes&exportar=excel"
        
    url_relatorio += f"&data_inicial={data_ini}&data_final={data_fim}"
    
    # 4. Solicita a planilha
    download = session.get(url_relatorio)
    
    if download.status_code != 200:
        raise Exception("Não foi possível conectar ao SGCOR para gerar o relatório.")
        
    # Retorna o conteúdo bruto do arquivo enviado pelo servidor
    return download.content

# --- INTERFACE WEB DO STREAMLIT ---
st.set_page_config(page_title="Sintesi Corretora - SGCOR", page_icon="📊")

st.title("📊 Extrator de Relatórios SGCOR")
st.write("Acesse e baixe seus relatórios direto pelo seu navegador.")

tipo = st.selectbox("Qual relatório deseja?", ["Produção", "Comissões"])

# Campos de data visuais que você gostou!
data_inicio = st.date_input("Data Inicial", datetime.today())
data_fim = st.date_input("Data Final", datetime.today())

st.divider()
st.subheader("🔑 Credenciais do SGCOR")
user_sgcor = st.text_input("Usuário de Login") # Mudado de E-mail para Usuário
pass_sgcor = st.text_input("Senha de Acesso", type="password")

if st.button("🚀 Disparar Extração SGCOR", use_container_width=True):
    if not user_sgcor or not pass_sgcor:
        st.warning("Por favor, preencha seu usuário e senha do SGCOR.")
    else:
        with st.spinner("Conectando ao SGCOR da Sintesi e preparando sua planilha..."):
            try:
                # Formata as datas para o padrão do SGCOR
                d_ini = data_inicio.strftime("%d/%m/%Y")
                d_fim = data_fim.strftime("%d/%m/%Y")
                
                # Executa a extração do conteúdo binário (Excel)
                conteudo_excel = extrair_relatorio_sgcor_direto(user_sgcor, pass_sgcor, tipo, d_ini, d_fim)
                
                nome_final = f"Relatorio_{tipo}_{d_ini.replace('/','-')}_a_{d_fim.replace('/','-')}.xlsx"
                
                st.success("✅ Relatório gerado com sucesso!")
                
                # Botão de download configurado estritamente para formato EXCEL (.xlsx)
                st.download_button(
                    label="📥 Clique aqui para Baixar o Arquivo Excel",
                    data=conteudo_excel,
                    file_name=nome_final,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Ocorreu um problema: {e}")
