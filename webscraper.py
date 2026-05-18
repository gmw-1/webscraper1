import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import plotly.express as px

# Muat variabel lingkungan
load_dotenv()

# Konfigurasi dasar untuk Selenium
def setup_webdriver():
    options = Options()
    options.add_argument("headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    driver = webdriver.Chrome(options=options)
    return driver

# Fungsi untuk melakukan web scraping menggunakan Selenium dan BeautifulSoup
def scrape_website(url):
    driver = setup_webdriver()
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    # Contoh ekstraksi data untuk website e-commerce
    items = soup.find_all("div", class_="item")
    data = []
    for item in items:
        try:
            title = item.find("h2").get_text(strip=True)
            price = item.find("span", class_="price").get_text(strip=True)
            data.append({"Judul": title, "Harga": price})
        except Exception as e:
            continue
    driver.quit()
    return data

# Fungsi analisis data menggunakan pandas
def analisis_data(data):
    df = pd.DataFrame(data)
    if not df.empty:
        # Ubah harga ke format numerik, menghapus simbol mata uang jika diperlukan
        df["Harga"] = df["Harga"].replace('[\$,]', '', regex=True).astype(float)
    return df

# Fungsi untuk membuat laporan otomatis
def generate_laporan(df):
    laporan = {
        "Waktu_Laporan": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Jumlah_Item": len(df),
        "Harga_Rata_Rata": round(df["Harga"].mean(), 2) if not df.empty else 0,
        "Harga_Tertinggi": round(df["Harga"].max(), 2) if not df.empty else 0,
        "Harga_Terendah": round(df["Harga"].min(),2) if not df.empty else 0
    }
    return laporan

# Fungsi utama aplikasi Streamlit
def main():
    st.set_page_config(page_title="Aplikasi Web Scraping dan Analisis Data", layout="wide")
    st.title("Aplikasi Web Scraping, Analisis Data, dan Automasi Laporan")
    
    # Sidebar Input URL dan Pengaturan
    st.sidebar.header("Pengaturan Web Scraping")
    url_input = st.sidebar.text_input("Masukkan URL website", "https://contoh.com")
    if st.sidebar.button("Mulai Scraping"):
        with st.spinner("Melakukan scraping..."):
            data = scrape_website(url_input)
            st.session_state["data_scraped"] = data
    
    # Tampilkan data scraping
    if "data_scraped" in st.session_state:
        data = st.session_state["data_scraped"]
        st.subheader("Data Hasil Scraping")
        st.write(data)
        df = analisis_data(data)
        st.subheader("Analisis Data")
        st.dataframe(df)
        
        # Tampilkan statistik dasar dalam tabel
        if not df.empty:
            stats = {
                "Rata-rata Harga": [round(df["Harga"].mean(),2)],
                "Harga Terendah": [round(df["Harga"].min(),2)],
                "Harga Tertinggi": [round(df["Harga"].max(),2)]
            }
            stats_df = pd.DataFrame(stats)
            st.table(stats_df)
        
        # Buat visualisasi menggunakan Plotly
        if not df.empty:
            fig = px.bar(df, x="Judul", y="Harga", title="Perbandingan Harga Item")
            st.plotly_chart(fig, use_container_width=True)
        
        # Automasi pembuatan laporan
        laporan = generate_laporan(df)
        st.subheader("Laporan Otomatis")
        st.json(laporan)
        
        # Tombol download laporan sebagai file CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(label="Unduh Data sebagai CSV", data=csv, file_name=f"data_scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")
        
        # Tombol download ringkasan laporan
        json_laporan = json.dumps(laporan, indent=4)
        st.download_button(label="Unduh Laporan sebagai JSON", data=json_laporan, file_name="laporan.json", mime="application/json")

if __name__ == "__main__":
    main()
