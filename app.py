import streamlit as st
import requests
from datetime import datetime

# --- FUNÇÃO DO ROBÔ TOTALMENTE MAPEADA PELO CÓDIGO FONTE ---
def extrair_tombamento_carteira_sgcor(usuario, senha, data_ini, data_fim, ramo_id, filtrar_por):
    session = requests.Session()
    
    url_base = "https://sintesi.sgcor.com.br"
    url_login = f"{url_base}/index.php?op=login"
    
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Origin": url_base,
        "Referer": url_base
    })
    
    # 1. Abre a página inicial (Método original que funciona)
    session.get(url_base)
    
    # 2. Payload de autenticação original
    payload_login = {
        "username": usuario,
        "password": senha,
        "op": "login_validar"
    }
    
    # 3. Realiza o login na Sintesi
    session.post(url_login, data=payload_login)
    
    # 4. ROTA EXATA EXTRAÍDA DO SGCOR DO CARLOS (Usa ajax.php e as variáveis corretas)
    url_exportar = f"{url_base}/ajax.php?opRel=tombamentoCarteira&acao=gerar"
    
    # Dados exatos que o formulário do SGCOR envia quando você clica em "Gerar CSV"
    payload_relatorio = {
        "tipoRel": "TC01",
        "periodo": data_ini,        # Data Inicial (dd/mm/aaaa)
        "periodo2": data_fim,       # Data Final (dd/mm/aaaa)
        "ramoId": ramo_id,          # ID do Ramo selecionado
        "filtrarPor": filtrar_por,  # Filtro de data escolhido
        "corretorId": "1",          # Trava automática na Sintesi Corretora
        "companhiaId": "",          # Todos(as)
        "produtorRepasse": "",      # Todos(as)
        "grafico": "",
        "csv": "t"                  # 't' ativa o download nativo em formato CSV!
    }
    
    # 5. Faz a requisição POST simulando o clique do botão "Gerar CSV"
    download = session.post(url_exportar, data=payload_relatorio)
    
    if download.status_code != 200:
        raise Exception("O servidor do SGCOR não respondeu corretamente ao pedido do relatório.")
        
    return download.content

# --- INTERFACE WEB DO STREAMLIT (SINTESI) ---
st.set_page_config(page_title="Sintesi Corretora - SGCOR", page_icon="📊")

st.title("📊 Extrator Gerencial - Tombamento de Carteira")
st.write("Gere e baixe seu relatório legítimo em CSV de forma automatizada.")

# Seletores visuais idênticos aos do SGCOR
filtrar_por = st.selectbox(
    "Filtrar datas por:",
    ["dataVigenciaInicial", "dataVigenciaFinal", "dataEmitida"],
    format_func=lambda x: "Início de Vigência" if x == "dataVigenciaInicial" else "Final de Vigência" if x == "dataVigenciaFinal" else "Emissão da Apólice"
)

# Mapeamento dos ramos principais do seu sistema
ramos_disponiveis = {
    "7": "AUTOMÓVEL",
    "62": "ACIDENTES PESSOAIS INDIVIDUAL",
    "70": "AGRÍCOLA",
    "65": "FROTA",
    "19": "RESIDENCIAL",
    "20": "EMPRESARIAL",
    "74": "TRANSPORTE",
    "61": "PLANO DE SAUDE",
    "40": "VIDA EM GRUPO"
}
ramo_selecionado = st.selectbox("Selecione o Ramo:", list(ramos_disponiveis.keys()), format_func=lambda x: ramos_disponiveis[x])

data_inicio = st.date_input("Período Inicial", datetime.today())
data_fim = st.date_input("Período Final", datetime.today())

st.divider()

# 🔒 DADOS DE ACESSO FIXOS DO CARLOS (PRONTOS E TRANCADOS)
user_sgcor = "chcatunda"
pass_sgcor = "Cretapoi@8755"

st.info("🔒 Credenciais de acesso chcatunda configuradas com sucesso.")

if st.button("🚀 Disparar Extração SGCOR", use_container_width=True):
    with st.spinner("Conectando ao SGCOR e processando o Tombamento de Carteira..."):
        try:
            # Formatação de datas padrão Brasil exigida pelo SGCOR
            d_ini = data_inicio.strftime("%d/%m/%Y")
            d_fim = data_fim.strftime("%d/%m/%Y")
            
            # Puxa o conteúdo binário do CSV processado pelo ajax.php
            conteudo_csv = extrair_tombamento_carteira_sgcor(
                user_sgcor, pass_sgcor, d_ini, d_fim, ramo_selecionado, filtrar_por
            )
            
            nome_final = f"Tombamento_Carteira_{d_ini.replace('/','-')}_a_{d_fim.replace('/','-')}.csv"
            
            st.success("✅ CSV Gerado com Sucesso pelo Motor Interno!")
            
            st.download_button(
                label="📥 Clique aqui para Baixar o Arquivo CSV",
                data=conteudo_csv,
                file_name=nome_final,
                mime="text/csv",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"❌ Falha no processamento: {e}")
