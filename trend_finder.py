
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime

st.set_page_config(page_title="Trend Finder RSS – USA ➜ ITA", layout="centered")
st.title("🔍 Trend Finder: dagli USA all'Italia")
st.markdown("Scopri i trend attuali negli Stati Uniti e verifica se sono presenti anche tra i trend italiani.")

# ✅ Recupera trending topic via Google Trends RSS
def get_trending_keywords_rss(geo="US"):
    url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    titles = soup.find_all('title')[1:]  # salta il primo <title> (titolo del feed)
    keywords = [title.text.strip() for title in titles][:20]
    return keywords

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

    # CSV download
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"rss_trend_comparison_{timestamp}.csv"
    st.download_button("📥 Scarica risultati", data=df_result.to_csv(index=False), file_name=filename, mime="text/csv")
