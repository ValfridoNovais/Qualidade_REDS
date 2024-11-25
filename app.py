import streamlit as st
import pandas as pd
from spellchecker import SpellChecker
import nltk
from nltk.corpus import stopwords
import difflib
import PyPDF2

# Configuração inicial
nltk.download('punkt')
nltk.download('stopwords')

# Função para carregar e extrair texto do Código Penal em PDF
@st.cache_resource
def load_codigo_penal(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        texto = ""
        for page in pdf_reader.pages:
            texto += page.extract_text()
    return texto

# Função para correção ortográfica
def verificar_ortografia(texto):
    spell = SpellChecker(language='pt')
    texto = texto.lower()  # Converte para minúsculas
    palavras = texto.split()
    erros = {palavra: spell.correction(palavra) for palavra in palavras if palavra not in spell}
    return erros

# Função para análise de concordância (básica)
def verificar_concordancia(texto):
    stop_words = set(stopwords.words('portuguese'))
    palavras = [palavra for palavra in texto.lower().split() if palavra.isalpha() and palavra not in stop_words]
    return "Concordância gramatical básica não detectou erros."

# Função para verificar compatibilidade da natureza com o histórico
def verificar_natureza(historico, natureza_codigo, codigo_penal):
    # Busca pelo código associado à natureza no texto do Código Penal
    if natureza_codigo in codigo_penal:
        trechos = difflib.get_close_matches(historico.lower(), [codigo_penal.lower()], cutoff=0.6)
        if trechos:
            return f"Compatível com a natureza {natureza_codigo}."
        else:
            return f"Incompatível com a natureza {natureza_codigo}."
    return "Natureza não encontrada no Código Penal."

# Interface do Streamlit
st.title("Verificação de Classificação Jurídica e Ortográfica")
st.write("Este programa analisa erros ortográficos, concordância gramatical e verifica a coerência entre o histórico e a natureza jurídica com base no Código Penal Brasileiro.")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("Carregue um arquivo CSV com as colunas: reds, natureza_codigo, natureza, historico", type=["csv"])

if uploaded_file:
    # Carregar dados do CSV
    data = pd.read_csv(uploaded_file)
    st.write("Dados carregados:")
    st.dataframe(data.head())

    # Carregar o Código Penal
    codigo_penal = load_codigo_penal("E:\\GitHub\\Qualidade_REDS\\documentos\\codigo_penal.pdf")

    # Processar os dados
    resultados = []
    for _, row in data.iterrows():
        historico = str(row['historico']).upper() if not pd.isnull(row['historico']) else ""
        natureza = str(row['natureza']).upper() if not pd.isnull(row['natureza']) else ""
        natureza_codigo = str(row['natureza_codigo']).upper() if not pd.isnull(row['natureza_codigo']) else ""
        
        erros_ortografia = verificar_ortografia(historico)
        analise_concordancia = verificar_concordancia(historico)
        compatibilidade = verificar_natureza(historico, natureza_codigo, codigo_penal)
        
        resultados.append({
            'reds': row['reds'],
            'natureza_codigo': natureza_codigo,
            'natureza': natureza,
            'historico': historico,
            'Erros Ortográficos': erros_ortografia,
            'Concordância': analise_concordancia,
            'Compatibilidade': compatibilidade
        })
    
    # Exibir os resultados
    resultados_df = pd.DataFrame(resultados)
    st.write("Resultados da análise:")
    st.dataframe(resultados_df)

    # Botão para download dos resultados
    st.download_button(
        label="Baixar Resultados",
        data=resultados_df.to_csv(index=False),
        file_name="resultados_analise.csv",
        mime="text/csv"
    )
else:
    st.info("Por favor, carregue um arquivo CSV para análise.")
