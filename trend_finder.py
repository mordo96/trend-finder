
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
import time
import datetime

st.set_page_config(page_title="Trend Finder USA ➜ ITA", layout="centered")
st.title("🔍 Trend Finder: dagli USA all'Italia")
st.markdown("Scopri cosa è popolare negli Stati Uniti oggi e verifica se c'è interesse anche in Italia.")

pytrends = TrendReq(hl='en-US', tz=360)

# ✅ Recupero automatico dei trending topic USA via RSS
@st.cache_data(show_spinner=False)
def get_us_trending_searches():
    url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    titles = soup.find_all('title')[1:]  # Salta il titolo del feed
    keywords = [title.text for title in titles][:10]
    return keywords

# ✅ Confronto con interesse in Italia
def compare_interest(keyword):
    time.sleep(2)
    try:
        pytrends.build_payload([keyword], cat=0, timeframe='today 3-m', geo='IT', gprop='')
        df = pytrends.interest_over_time()
        return df[[keyword]] if not df.empty else None
    except Exception:
        return None

# ✅ Trova store Shopify
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
    st.subheader("📈 Trend attuali negli USA")
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
                st.subheader(f"📊 Interesse in Italia per: {keyword}")
                st.line_chart(trend_data)
            else:
                st.warning(f"Nessun dato disponibile per '{keyword}' o richiesta bloccata.")

    df_out = pd.DataFrame(results)
    if not df_out.empty:
        st.subheader("📄 Riepilogo finale")
        st.dataframe(df_out)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"trend_analysis_{timestamp}.csv"
        st.download_button("📥 Scarica CSV", data=df_out.to_csv(index=False), file_name=filename, mime="text/csv")
