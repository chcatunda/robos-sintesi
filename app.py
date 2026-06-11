import streamlit as st
import requests
from datetime import datetime

# --- FUNÇÃO DO ROBÔ INTEGRADO AO MOTOR DE TOMBAMENTO DO SGCOR ---
def extrair_tombamento_carteira_sgcor(usuario, senha, data_ini, data_fim, ramo_id, filtrar_por, companhia_id, produtor_id, corretor_id):
    session = requests.Session()
    
    url_base = "https://sintesi.sgcor.com.br"
    url_login = f"{url_base}/index.php?op=login"
    
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Origin": url_base,
        "Referer": url_base
    })
    
    # 1. Ativa os cookies de sessão na página inicial
    session.get(url_base)
    
    # 2. Dados de acesso
    payload_login = {
        "username": usuario,
        "password": senha,
        "op": "login_validar"
    }
    
    # 3. Executa o login
    session.post(url_login, data=payload_login)
    
    # 4. Endereço exato do motor de relatórios do SGCOR da Sintesi
    url_exportar = f"{url_base}/ajax.php?opRel=tombamentoCarteira&acao=gerar"
    
    # Payload completo espelhando as variáveis exatas do sistema
    payload_relatorio = {
        "tipoRel": "TC01",
        "periodo": data_ini,          # Data Inicial (dd/mm/aaaa)
        "periodo2": data_fim,         # Data Final (dd/mm/aaaa)
        "ramoId": ramo_id,            # ID do Ramo Escolhido
        "filtrarPor": filtrar_por,    # Campo de filtragem por data
        "corretorId": corretor_id,    # ID da Corretora
        "companhiaId": companhia_id,  # ID da Seguradora
        "produtorRepasse": produtor_id, # ID do Produtor de Repasse
        "grafico": "",
        "csv": "t"                    # Comando crucial que força a geração do CSV nativo
    }
    
    # 5. Dispara a requisição simulação o clique de exportação
    download = session.post(url_exportar, data=payload_relatorio)
    
    if download.status_code != 200:
        raise Exception("O servidor do SGCOR não respondeu ao chamado de extração de dados.")
        
    return download.content

# --- INTERFACE VISUAL DO STREAMLIT ---
st.set_page_config(page_title="Sintesi Corretora - SGCOR", page_icon="📊", layout="wide")

st.title("📊 Extrator Automático - Tombamento de Carteira (TC01)")
st.write("Gere e baixe seus relatórios em CSV legítimos estruturados diretamente para o seu computador.")

st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Filtros de Período")
    data_inicio = st.date_input("Data Inicial", datetime.today())
    data_fim = st.date_input("Data Final", datetime.today())
    
    filtrar_por = st.selectbox(
        "Filtrar datas por:",
        ["dataVigenciaInicial", "dataVigenciaFinal", "dataEmitida"],
        format_func=lambda x: "Início de Vigência" if x == "dataVigenciaInicial" else "Final de Vigência" if x == "dataVigenciaFinal" else "Emissão da Apólice"
    )

with col2:
    st.subheader("🔍 Filtros de Estrutura")
    
    # Dicionário com todos os Ramos mapeados do seu SGCOR
    ramos = {
        "7": "AUTOMÓVEL", "62": "ACIDENTES PESSOAIS INDIVIDUAL", "70": "AGRÍCOLA", "69": "AUTO ROUBO",
        "33": "AUTO SEG FRANQUIA", "67": "CAMINHÃO", "39": "CARTAO DE CREDITO", "23": "CONDOMÍNIO",
        "20": "EMPRESARIAL", "75": "EQUIPAMENTOS", "51": "EQUIPAMENTOS MOVEIS", "65": "FROTA",
        "24": "MARITIMA EMPRESARIAL", "63": "MOTO", "61": "PLANO DE SAUDE", "71": "R. C. PROFISSIONAL",
        "66": "R.C.F. - VEÍCULOS", "19": "RESIDENCIAL", "73": "RISCOS DE ENGENHARIA", 
        "64": "ROUBO + RASTREADOR", "60": "SEGURO GARANTIA", "74": "TRANSPORTE", "68": "UTILITÁRIO CARGA",
        "72": "VIAGEM", "40": "VIDA EM GRUPO", "35": "VIDA INDIVIDUAL"
    }
    ramo_id = st.selectbox("Selecione o Ramo:", list(ramos.keys()), format_func=lambda x: ramos[x], index=0)

    # Principais Seguradoras extraídas do seu código fonte
    companhias = {
        "": "Todos(as)", "10": "AZUL COMPANHIA DE SEGUROS", "5": "BRADESCO AUTO/RE", "1": "HDI SEGUROS S/A",
        "3": "MAPFRE VERA CRUZ", "12": "PORTO SEGURO", "14": "SUL AMERICA", "13": "TÓKIO MARINE", "2": "YELUM SEGUROS"
    }
    companhia_id = st.selectbox("Selecione a Seguradora:", list(companhias.keys()), format_func=lambda x: companhias[x])

    corretores = {"": "Todos(as)", "1": "SINTESI CORRETORA DE SEGUROS"}
    corretor_id = st.selectbox("Corretora:", list(corretores.keys()), format_func=lambda x: corretores[x], index=1)
    
    produtores = {"": "Todos(as)", "2": "CARLOS HENRIQUE - PRODUÇÃO", "98": "ROZIANE CATUNDA"}
    produtor_id = st.selectbox("Produtor Repasse:", list(produtores.keys()), format_func=lambda x: produtores[x])

st.divider()

# 🔒 SUAS CREDENCIAIS DEFINITIVAS CONFIGURADAS NATIIVAMENTE
user_sgcor = "chcatunda"
pass_sgcor = "Cretapoi@8755"

st.info(f"🔒 Robô configurado e pronto para operar com o login corporativo: **{user_sgcor}**")

if st.button("🚀 Disparar Extração SGCOR", use_container_width=True):
    with st.spinner("Conectando ao motor ajax do SGCOR e gerando o relatório..."):
        try:
            # Formata as datas no modelo dd/mm/aaaa exigido pelo SGCOR
            d_ini = data_inicio.strftime("%d/%m/%Y")
            d_fim = data_fim.strftime("%d/%m/%Y")
            
            # Dispara a extração via POST
            conteudo_csv = extrair_tombamento_carteira_sgcor(
                user_sgcor, pass_sgcor, d_ini, d_fim, ramo_id, filtrar_por, companhia_id, produtor_id, corretor_id
            )
            
            nome_final = f"TC01_{d_ini.replace('/','')}{datetime.now().strftime('%H%M%S')}.csv"
            
            st.success("✅ Relatório de Tombamento de Carteira gerado com sucesso!")
            
            st.download_button(
                label="📥 Clique aqui para Baixar o Arquivo CSV",
                data=conteudo_csv,
                file_name=nome_final,
                mime="text/csv",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"❌ Ocorreu um problema no processamento: {e}")
