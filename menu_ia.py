import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import spacy
import pickle

# Inicializa o modelo do spaCy
nlp = spacy.load("pt_core_news_sm")

# Função para classificação por regras simples
def classificar_regras_simples(texto):
    palavras_furto = ["furtou", "subtração", "levou", "apropriou-se"]
    palavras_roubo = ["roubou", "assalto", "ameaçou", "violência"]
    palavras_ameaca = ["ameaçou", "disse que ia", "prometeu"]
    
    if any(p in texto.lower() for p in palavras_roubo):
        return "Roubo"
    elif any(p in texto.lower() for p in palavras_furto):
        return "Furto"
    elif any(p in texto.lower() for p in palavras_ameaca):
        return "Ameaça"
    return "Não identificado"

# Função para classificação por aprendizado de máquina
def treinar_modelo_ml(data, labels):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data)
    y = labels

    modelo = RandomForestClassifier()
    modelo.fit(X, y)
    
    return modelo, vectorizer

# Configurações do Streamlit
st.sidebar.title("Inteligências de Classificação")
opcao = st.sidebar.radio("Escolha o tipo de inteligência:", ["Regras Simples", "Proximidade/Contexto", "Machine Learning"])

st.title("Treinamento e Classificação de Texto")
st.write("Escolha a abordagem na barra lateral e insira os textos para classificar ou treinar.")

# Upload de Dados
uploaded_file = st.sidebar.file_uploader("Carregue um arquivo CSV com colunas 'Texto' e 'Categoria'", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Pré-visualização dos dados:")
    st.write(df.head())

# Treinamento baseado na escolha
if opcao == "Regras Simples":
    st.subheader("Classificação com Regras Simples")
    texto = st.text_area("Digite um texto para classificar:")
    if texto:
        resultado = classificar_regras_simples(texto)
        st.write(f"Resultado da Classificação: {resultado}")

elif opcao == "Proximidade/Contexto":
    st.subheader("Classificação com Proximidade e Contexto (spaCy)")
    texto = st.text_area("Digite um texto para classificar:")
    if texto:
        doc = nlp(texto)
        palavras_roubo = ["arma", "assalto"]
        palavras_furto = ["furtou", "subtração"]
        palavras_ameaca = ["ameaçou", "intimidou"]
        
        if any(token.text in palavras_roubo for token in doc):
            resultado = "Roubo"
        elif any(token.text in palavras_furto for token in doc):
            resultado = "Furto"
        elif any(token.text in palavras_ameaca for token in doc):
            resultado = "Ameaça"
        else:
            resultado = "Não identificado"
        st.write(f"Resultado da Classificação: {resultado}")

elif opcao == "Machine Learning":
    st.subheader("Treinamento e Classificação com Machine Learning")
    if uploaded_file:
        if st.button("Treinar Modelo"):
            data = df["Texto"].values
            labels = df["Categoria"].values
            modelo_ml, vectorizer = treinar_modelo_ml(data, labels)
            st.success("Modelo treinado com sucesso!")
            # Salva o modelo treinado
            with open("modelo_ml.pkl", "wb") as f:
                pickle.dump((modelo_ml, vectorizer), f)

    # Classificação com o modelo treinado
    if st.button("Classificar Texto"):
        texto = st.text_area("Digite um texto para classificar:")
        if texto:
            try:
                with open("modelo_ml.pkl", "rb") as f:
                    modelo_ml, vectorizer = pickle.load(f)
                X_test = vectorizer.transform([texto])
                resultado = modelo_ml.predict(X_test)
                st.write(f"Resultado da Classificação: {resultado[0]}")
            except FileNotFoundError:
                st.error("Modelo ainda não treinado. Por favor, faça o treinamento antes de classificar.")

