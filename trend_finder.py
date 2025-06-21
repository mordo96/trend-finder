
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime

# Moduli AI gratuiti
from transformers import pipeline
from keybert import KeyBERT

st.set_page_config(page_title="Trend Finder AI – Solo Classificazione", layout="centered")
st.title("🔍 Trend Finder (AI locale)")
st.markdown("Analizza trend dagli USA con modelli gratuiti locali (classificazione e parole chiave).")

# 🔧 Inizializza modelli (senza traduzione per evitare crash su Streamlit Cloud)
@st.cache_resource
def load_ai_models():
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    keyword_extractor = KeyBERT()
    return classifier, keyword_extractor

classifier, keyword_extractor = load_ai_models()

# Lista fallback di trend USA
DEFAULT_US_TRENDS = [
    "Adidas Samba",
    "Nike Air Max",
    "Onitsuka Tiger",
    "Puma Speedcat",
    "Hoka slip on",
    "New Balance 9060",
    "Loafers sneaker",
    "Mary Jane shoes",
    "Metallic sneakers",
    "Salomon XT-6"
]

if st.button("🔁 Analizza trend con AI"):
    candidate_labels = ["fashion", "technology", "fitness", "lifestyle", "streetwear", "sneakers"]

    results = []
    st.subheader("📊 Analisi trend USA (con AI)")

    for trend in DEFAULT_US_TRENDS:
        with st.spinner(f"Analisi per: {trend}"):
            # Classificazione
            classification = classifier(trend, candidate_labels)
            best_label = classification["labels"][0]
            score = classification["scores"][0]

            # Keyword extraction (mock sentence)
            keywords = keyword_extractor.extract_keywords(f"{trend} is trending in the US market", top_n=2)
            keywords_out = ", ".join([kw[0] for kw in keywords])

            results.append({
                "Trend": trend,
                "Categoria AI": best_label,
                "Confidenza": f"{score:.2f}",
                "Parole Chiave": keywords_out
            })

    df_result = pd.DataFrame(results)
    st.dataframe(df_result)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"trend_ai_classification_{timestamp}.csv"
    st.download_button("📥 Scarica risultati", data=df_result.to_csv(index=False), file_name=filename, mime="text/csv")
