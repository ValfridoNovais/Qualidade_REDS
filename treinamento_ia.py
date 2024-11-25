import streamlit as st
import pandas as pd
import json
import os
from spellchecker import SpellChecker
import PyPDF2

# Caminho do arquivo de feedback
FEEDBACK_FILE = "feedback_ia.json"

# Mapeamento de códigos para naturezas
CODES_TO_NATURES = {
    "C01155": "FURTO",
    "C01157": "ROUBO"
}

# Palavras-chave para cada natureza
KEYWORDS = {
    "FURTO": ["subtrair", "sem violência", "ausência de grave ameaça"],
    "ROUBO": ["violência", "grave ameaça", "força", "coação"]
}

# Carregar ou criar o arquivo de feedback
def carregar_feedback():
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r") as f:
            return json.load(f)
    return {}

def salvar_feedback(feedback):
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedback, f, indent=4)

# Carregar o Código Penal
@st.cache_resource
def load_codigo_penal(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        texto = ""
        for page in pdf_reader.pages:
            texto += page.extract_text()
    return texto

# Função para análise baseada em palavras-chave
def analisar_por_palavras_chave(historico, natureza_codigo):
    natureza = CODES_TO_NATURES.get(natureza_codigo, "").upper()  # Traduz o código para o nome da natureza
    if not natureza:
        return f"Código {natureza_codigo} não encontrado no mapeamento."
    
    palavras_chave = KEYWORDS.get(natureza, [])
    historico_lower = historico.lower()

    # Verificar presença das palavras-chave
    palavras_encontradas = [palavra for palavra in palavras_chave if palavra in historico_lower]

    if palavras_encontradas:
        return f"Compatível com {natureza}. Palavras-chave encontradas: {', '.join(palavras_encontradas)}"
    else:
        return f"Incompatível com {natureza}. Nenhuma palavra-chave encontrada."

# Interface do Streamlit
st.title("Treinamento da IA com Feedback")
st.write("Selecione um REDS para análise e forneça seu feedback sobre a resposta do programa.")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("Carregue um arquivo CSV com as colunas: reds, natureza_codigo, natureza, historico", type=["csv"])

if uploaded_file:
    # Carregar dados do CSV
    data = pd.read_csv(uploaded_file)
    st.write("Dados carregados:")
    st.dataframe(data.head())

    # Carregar o Código Penal
    codigo_penal = load_codigo_penal("E:\\GitHub\\Qualidade_REDS\\documentos\\codigo_penal.pdf")

    # Selecionar REDS
    reds_list = data["reds"].unique()
    selected_reds = st.selectbox("Selecione um REDS:", reds_list)

    # Filtrar dados do REDS selecionado
    selected_data = data[data["reds"] == selected_reds].iloc[0]
    historico = str(selected_data["historico"]).upper()
    natureza_codigo = str(selected_data["natureza_codigo"]).upper()

    # Analisar inconsistências com palavras-chave
    resultado_palavras_chave = analisar_por_palavras_chave(historico, natureza_codigo)

    st.write(f"Análise para o REDS {selected_reds}:")
    st.write(f"Histórico: {historico}")
    st.write(f"Natureza Código: {natureza_codigo}")
    st.write(f"Resultado da Análise por Palavras-Chave: {resultado_palavras_chave}")

    # Feedback do Usuário
    feedback_data = carregar_feedback()
    feedback = st.radio("A análise está correta?", ["Sim", "Não"])

    if st.button("Enviar Feedback"):
        if selected_reds not in feedback_data:
            feedback_data[selected_reds] = {
                "historico": historico,
                "natureza_codigo": natureza_codigo,
                "resultado_palavras_chave": resultado_palavras_chave,
                "feedback": feedback
            }
            salvar_feedback(feedback_data)
            st.success("Feedback enviado com sucesso!")
        else:
            st.warning("O feedback para este REDS já foi enviado.")
else:
    st.info("Por favor, carregue um arquivo CSV para análise.")

# Exibir feedback salvo
st.write("Feedback acumulado:")
feedback_data = carregar_feedback()
st.json(feedback_data)
