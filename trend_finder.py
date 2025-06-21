
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Trend Finder USA ➜ ITA", layout="centered")
st.title("🔍 Trend Finder: dagli USA all'Italia")
st.markdown("Questa app individua i trend attuali negli Stati Uniti e verifica se sono popolari anche in Italia.")

pytrends = TrendReq(hl='en-US', tz=360)

# ✅ Funzione aggiornata: prende trending keyword da Google Trends RSS (no API pytrends)
@st.cache_data(show_spinner=False)
def get_us_trending_searches():
    url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    titles = soup.find_all('title')[1:]  # Salta il primo <title> (titolo del feed)
    keywords = [title.text for title in titles][:10]
    return keywords

@st.cache_data(show_spinner=False)
def compare_interest(keyword):
    pytrends.build_payload([keyword], cat=0, timeframe='today 3-m', geo='IT', gprop='')
    df = pytrends.interest_over_time()
    return df[[keyword]] if not df.empty else None

@st.cache_data(show_spinner=False)
def find_shopify_stores(keyword):
    headers = {"User-Agent": "Mozilla/5.0"}
    query = f'{keyword} site:myshopify.com'
    url = f'https://www.google.com/search?q={query}'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = [a['href'] for a in soup.select('a[href^="http"]') if "myshopify.com" in a['href']]
    return links[:5]

if st.button("🔁 Trova trend ora"):
    trends = get_us_trending_searches()
    st.subheader("📈 Trend USA attuali")
    st.write(trends)

    results = []

    for keyword in trends:
        with st.spinner(f"Analisi per: {keyword}"):
            trend_data = compare_interest(keyword)
            if trend_data is not None:
                mean_val = trend_data[keyword].mean()
                shopify_sites = find_shopify_stores(keyword)
                results.append({
                    "Keyword": keyword,
                    "Interesse Medio in Italia": round(mean_val, 2),
                    "Shopify trovati": ", ".join(shopify_sites)
                })

                # 🔍 Visualizza grafico temporale per ogni keyword
                st.subheader(f"📊 Interesse in Italia per: {keyword}")
                st.line_chart(trend_data)

    df_out = pd.DataFrame(results)
    st.subheader("📄 Riepilogo Analisi")
    st.dataframe(df_out)

    # 🗃️ Salvataggio CSV con timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"trend_analysis_{timestamp}.csv"
    st.download_button("📥 Scarica CSV", data=df_out.to_csv(index=False), file_name=filename, mime="text/csv")
