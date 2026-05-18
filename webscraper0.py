import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import json
import plotly.express as px

# ---------- Selenium Setup ----------
def setup_webdriver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    return webdriver.Chrome(options=options)

# ---------- Scraping ----------
def scrape_website(url):
    driver = setup_webdriver()
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    data = []
    for item in soup.find_all("div", class_="item"):
        title = item.find("h2")
        price = item.find("span", class_="price")
        if title and price:
            data.append({"Judul": title.get_text(strip=True), "Harga": price.get_text(strip=True)})
    return data

# ---------- App ----------
def main():
    st.set_page_config(page_title="Web Scraper", layout="wide")
    st.title("Web Scraper & Analisis Data")

    url = st.sidebar.text_input("URL", "https://contoh.com")
    if st.sidebar.button("Scrape"):
        if not url.startswith("http"):
            st.error("URL tidak valid")
            return
        with st.spinner("Scraping..."):
            data = scrape_website(url)

        if not data:
            st.warning("Tidak ada data ditemukan.")
            return

        df = pd.DataFrame(data)
        df["Harga"] = df["Harga"].str.replace("[^0-9.]", "", regex=True).astype(float)

        # Tabel
        st.subheader("Data")
        st.dataframe(df, use_container_width=True)

        # Statistik
        st.subheader("Statistik")
        stats = pd.DataFrame([{
            "Rata-rata": df["Harga"].mean(),
            "Terendah": df["Harga"].min(),
            "Tertinggi": df["Harga"].max(),
            "Jumlah": len(df)
        }])
        st.table(stats)

        # Grafik
        fig = px.bar(df, x="Judul", y="Harga", title="Perbandingan Harga")
        st.plotly_chart(fig, use_container_width=True)

        # Laporan
        laporan = {
            "waktu": datetime.now().isoformat(),
            "jumlah_item": len(df),
            "harga_rata_rata": round(df["Harga"].mean(), 2),
            "harga_tertinggi": round(df["Harga"].max(), 2),
            "harga_terendah": round(df["Harga"].min(), 2),
        }
        st.subheader("Laporan")
        st.json(laporan)

        # Download
        col1, col2 = st.columns(2)
        col1.download_button("📥 CSV", df.to_csv(index=False).encode(), "data.csv", "text/csv")
        col2.download_button("📥 JSON", json.dumps(laporan, indent=2), "laporan.json", "application/json")


if __name__ == "__main__":
    main()
