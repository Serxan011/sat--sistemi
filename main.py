import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# Qovluq və Baza qurulması
if not os.path.exists("sekiller"): os.makedirs("sekiller")
conn = sqlite3.connect("magaza.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS mehsullar (id INTEGER PRIMARY KEY, ad TEXT, kat TEXT, alis REAL, satis REAL, sekil TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS satislar (id INTEGER PRIMARY KEY, mehsul TEXT, say INTEGER, toplam REAL, tarix DATE)")

st.title("⚡ NN Mağaza İdeal Kassa")

menu = st.sidebar.radio("Menyu:", ["🛒 Kassa", "📦 Məhsul Əlavə", "📊 Hesabat"])

if menu == "📦 Məhsul Əlavə":
    st.header("Yeni Məhsul")
    ad = st.text_input("Məhsul adı:")
    kat = st.text_input("Kateqoriya:")
    alis = st.number_input("Alış qiyməti:")
    edv = st.selectbox("ƏDV faizi:", [0, 18])
    satis = st.number_input("Satış qiyməti:")
    sekil = st.file_uploader("Şəkil yüklə:", type=['jpg', 'png'])
    
    maya = alis * (1 + edv/100)
    st.write(f"Maya dəyəri: {maya:.2f} AZN")
    
    if st.button("Bazaya vur"):
        yol = ""
        if sekil:
            yol = f"sekiller/{sekil.name}"
            with open(yol, "wb") as f: f.write(sekil.getbuffer())
        conn.execute("INSERT INTO mehsullar (ad, kat, alis, satis, sekil) VALUES (?,?,?,?,?)", (ad, kat, maya, satis, yol))
        conn.commit()
        st.success("Məhsul əlavə edildi!")

elif menu == "🛒 Kassa":
    df = pd.read_sql("SELECT * FROM mehsullar", conn)
    axtar = st.text_input("🔍 Məhsul axtar:")
    if axtar: df = df[df['ad'].str.contains(axtar, case=False)]
    
    if 'sebet' not in st.session_state: st.session_state.sebet = []
    
    for _, row in df.iterrows():
        c1, c2 = st.columns([1, 3])
        if row['sekil'] and os.path.exists(row['sekil']): c1.image(row['sekil'], width=80)
        c2.write(f"**{row['ad']}** - {row['satis']} AZN")
        if c2.button("Səbətə at", key=row['id']):
            st.session_state.sebet.append({"ad": row['ad'], "toplam": row['satis']})
            
    if st.button("Satışı Tamamla"):
        for item in st.session_state.sebet:
            conn.execute("INSERT INTO satislar (mehsul, say, toplam, tarix) VALUES (?,?,?,?)", (item['ad'], 1, item['toplam'], datetime.now().date()))
        conn.commit()
        st.session_state.sebet = []
        st.success("Satış tamamlandı!")

elif menu == "📊 Hesabat":
    df_satis = pd.read_sql("SELECT * FROM satislar", conn)
    st.write(df_satis)
    st.metric("Ümumi dövriyyə:", f"{df_satis['toplam'].sum():.2f} AZN")
