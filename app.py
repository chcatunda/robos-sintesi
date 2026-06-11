import streamlit as st
import requests
import re
import os
from datetime import datetime

# --- FUNÇÃO DO ROBÔ INTEGRADO SGCOR ---
def extrair_relatorio_sgcor_direto(usuario, senha, tipo_relatorio, data_ini, data_fim):
    # Cria uma sessão de navegação virtual limpa
    session = requests.Session()
    
    # Endereço oficial do SGCOR
    url_base = "https://sistema.sgcor.com.br"
    url_login = f"{url_base}/login"
    
    # Cabeçalho de simulação de navegador convencional
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Origin": url_base,
        "Referer": url_login
    })
    
    # 1. Captura o token de segurança da página de login
    resposta_inicial = session.get(url_login)
    
    token_busca = re.search(r'name="_token"\s+value="([^"]+)"', resposta_inicial.text)
    token_valor = token_busca.group(1) if token_busca else ""
    
    payload_login = {
        "_token": token_valor,
        "email": usuario,
        "password": senha
    }
    
    # 2. Faz o Login direto por baixo dos panos
    resposta_autenticacao = session.post(url_login, data=payload_login)
    
    # Verifica se as credenciais foram rejeitadas
    if "login" in resposta_autenticacao.url:
         if "error" in resposta_autenticacao.text or "credenciais" in resposta_autenticacao.text or "inválido" in resposta_autenticacao.text:
             raise Exception("Usuário ou senha inválidos no SGCOR. Verifique os dados digitados.")
    
    # 3. Define as rotas internas de exportação do Excel
    if tipo_relatorio == "Produção":
        url_relatorio = f"{url_base}/relatorios/producao-anual/exportar"
    else:
        url_relatorio = f"{url_base}/relatorios/comissoes/exportar"
        
    filtros = {
        "data_inicial": data_ini,
        "data_final": data_fim,
        "formato": "excel"
    }
    
    # 4. Solicita a planilha direto para a memória do servidor
    download = session.get(url_relatorio, params=filtros)
    
    if download.status_code != 200 or len(download.content) < 1000:
        raise Exception("Não foi possível gerar o relatório. Verifique o período ou as permissões do seu usuário.")
        
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
        with st.spinner("Conectando ao SGCOR e preparando sua planilha..."):
            try:
                d_ini = data_inicio.strftime("%d/%m/%Y")
                d_fim = data_fim.strftime("%d/%m/%Y")
                
                # Executa a extração
                conteudo_excel = extrair_relatorio_sgcor_direto(user_sgcor, pass_sgcor, tipo, d_ini, d_fim)
                
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
