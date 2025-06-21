
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime

# Moduli AI gratuiti
from transformers import pipeline
from keybert import KeyBERT

st.set_page_config(page_title="Trend Finder + AI Open Source", layout="centered")
st.title("🔍 Trend Finder con AI Gratuita")
st.markdown("Analizza trend dagli USA e arricchiscili con AI open-source locale (classificazione, keyword, traduzione).")

# 🔧 Inizializza modelli
@st.cache_resource
def load_ai_models():
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    translator = pipeline("translation_en_to_it", model="Helsinki-NLP/opus-mt-en-it")
    keyword_extractor = KeyBERT()
    return classifier, translator, keyword_extractor

classifier, translator, keyword_extractor = load_ai_models()

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

            # Traduzione
            translation = translator(trend)[0]["translation_text"]

            # Keyword extraction (mock sentence)
            keywords = keyword_extractor.extract_keywords(f"{trend} is trending in the US market", top_n=2)
            keywords_out = ", ".join([kw[0] for kw in keywords])

            results.append({
                "Trend": trend,
                "Categoria AI": best_label,
                "Confidenza": f"{score:.2f}",
                "Traduzione IT": translation,
                "Parole Chiave": keywords_out
            })

    df_result = pd.DataFrame(results)
    st.dataframe(df_result)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"trend_ai_analysis_{timestamp}.csv"
    st.download_button("📥 Scarica risultati", data=df_result.to_csv(index=False), file_name=filename, mime="text/csv")
