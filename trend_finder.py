
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime

st.set_page_config(page_title="Trend Finder Fallback – USA ➜ ITA", layout="centered")
st.title("🔍 Trend Finder (con fallback)")
st.markdown("Questa versione utilizza i feed ufficiali di Google Trends se disponibili, altrimenti una lista di trend attuali stimati.")

# Lista alternativa precompilata
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

DEFAULT_IT_TRENDS = [
    "Puma",
    "Nike Air Max",
    "Saldi estivi",
    "Scarpe comode",
    "Hoka donna",
    "New Balance",
    "Moda estate 2025",
    "Loafers donna",
    "Scarpe eleganti",
    "Sandali platform"
]

# Funzione che tenta di leggere il feed, ma ha fallback
def get_trending_keywords_rss(geo="US"):
    url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            st.warning(f"Feed non disponibile (errore {response.status_code}). Uso lista predefinita.")
            return DEFAULT_US_TRENDS if geo == "US" else DEFAULT_IT_TRENDS

        soup = BeautifulSoup(response.content, 'xml')
        titles = soup.find_all('title')[1:]  # salta il primo <title>
        keywords = [title.text.strip() for title in titles][:20]
        return keywords
    except Exception as e:
        st.error(f"Errore di rete: {str(e)} – Uso fallback.")
        return DEFAULT_US_TRENDS if geo == "US" else DEFAULT_IT_TRENDS

if st.button("🔁 Analizza trend ora"):
    trends_usa = get_trending_keywords_rss("US")
    trends_ita = get_trending_keywords_rss("IT")

    st.subheader("📈 Trend attuali negli USA")
    st.write(trends_usa)

    st.subheader("🇮🇹 Presenti anche in Italia?")
    results = []

    for keyword in trends_usa:
        is_in_italy = keyword in trends_ita
        results.append({
            "Keyword": keyword,
            "Presente in Italia": "✅ Sì" if is_in_italy else "❌ No"
        })

    df_result = pd.DataFrame(results)
    st.dataframe(df_result)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"rss_fallback_trend_{timestamp}.csv"
    st.download_button("📥 Scarica risultati", data=df_result.to_csv(index=False), file_name=filename, mime="text/csv")
