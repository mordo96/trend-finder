import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Trend Finder USA ➜ ITA", layout="centered")

st.title("🔍 Trend Finder: dagli USA all'Italia")
st.markdown("Questo strumento ti aiuta a trovare prodotti di tendenza negli Stati Uniti e verificarne il potenziale in Italia.")

# Initialize pytrends
pytrends = TrendReq(hl='en-US', tz=360)

@st.cache_data(show_spinner=False)
def get_us_trending_searches():
    df = pytrends.trending_searches(pn='united_states')
    return df[0].tolist()

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
    st.write(trends[:10])

    results = []
    for keyword in trends[:10]:
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

    df_out = pd.DataFrame(results)
    st.subheader("📊 Risultati dell'analisi")
    st.dataframe(df_out)
    st.download_button("📥 Scarica CSV", data=df_out.to_csv(index=False), file_name="trend_analysis.csv", mime="text/csv")
