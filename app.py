import streamlit as st
import requests
from bs4 import BeautifulSoup
import io
from datetime import datetime

# --- FUNÇÃO DO ROBÔ SGCOR SUPER ESTÁVEL ---
def extrair_relatorio_sgcor_estavel(usuario, senha, tipo_relatorio, data_ini, data_fim):
    # Inicia uma sessão de navegação virtual
    session = requests.Session()
    
    # URL base do sistema SGCOR
    url_base = "https://sistema.sgcor.com.br"
    
    # 1. Abre a página de login para capturar tokens de segurança se houver
    print("Conectando ao SGCOR...")
    pagina_login = session.get(f"{url_base}/login")
    soup = BeautifulSoup(pagina_login.text, 'html.parser')
    
    # Procura por campos ocultos de segurança (ex: _token) comuns em sistemas web
    token = soup.find('input', {'name': '_token'})
    token_valor = token['value'] if token else ''
    
    # Dados para enviar no formulário de Login
    payload_login = {
        "_token": token_valor,
        "email": usuario,
        "password": senha
    }
    
    # 2. Realiza o Login real
    print("Realizando autenticação...")
    resposta_login = session.post(f"{url_base}/login", data=payload_login)
    
    # 3. Define a rota interna do relatório escolhido
    if tipo_relatorio == "Produção":
        url_relatorio = f"{url_base}/relatorios/producao-anual/exportar"
    else:
        url_relatorio = f"{url_base}/relatorios/comissoes/exportar"
        
    filtros = {
        "data_inicial": data_ini,
        "data_final": data_fim,
        "formato": "excel"
    }
    
    # 4. Faz a requisição do arquivo Excel direto para a memória do Streamlit
    print("Baixando planilha...")
    download = session.get(url_relatorio, params=filtros)
    
    if download.status_code == 405 or download.status_code == 404:
        raise Exception("O SGCOR recusou o formato de requisição direta. Verifique os dados ou o link.")
        
    if len(download.content) < 500:
        raise Exception("Dados inválidos retornados. Verifique se seu e-mail e senha estão corretos.")
        
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
        with st.spinner("O robô está processando os dados no SGCOR... Aguarde..."):
            try:
                d_ini = data_inicio.strftime("%d/%m/%Y")
                d_fim = data_fim.strftime("%d/%m/%Y")
                
                # Executa o extrator leve
                conteudo_planilha = extrair_relatorio_sgcor_estavel(user_sgcor, pass_sgcor, tipo, d_ini, d_fim)
                
                nome_final = f"Relatorio_{tipo}_{d_ini.replace('/','-')}.xlsx"
                
                st.success("✅ Relatório gerado com sucesso!")
                st.download_button(
                    label="📥 Clique aqui para Baixar o Arquivo Excel",
                    data=conteudo_planilha,
                    file_name=nome_final,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Status do Robô: {e}")
