import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="NN Mağaza", page_icon="⚡", layout="centered")

def bazani_qur():
    conn = sqlite3.connect("magaza_sistemi.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mehsullar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mehsul_adi TEXT,
            kateqoriya TEXT,
            miqdar INTEGER,
            alis_qiymeti REAL,
            satis_qiymeti REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS satislar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mehsul_id INTEGER,
            mehsul_adi TEXT,
            kateqoriya TEXT,
            miqdar INTEGER,
            satis_qiymeti REAL,
            tarix TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

bazani_qur()

st.markdown("<h1 style='text-align: center; color: #00d2ff;'>⚡ NN Mağaza</h1>", unsafe_allow_html=True)

menyu = st.sidebar.radio("Menyu:", ["🛒 Satış Ekranı", "📦 Məhsul Əlavə Et", "📊 Mövcud Stok", "📈 Satış Hesabatı"])

if menyu == "🛒 Satış Ekranı":
    st.subheader("🛒 Satış Ekranı")
    conn = sqlite3.connect("magaza_sistemi.db")
    df = pd.read_sql_query("SELECT * FROM mehsullar WHERE miqdar > 0", conn)
    conn.close()
    
    if not df.empty:
        axtar = st.text_input("🔍 Məhsul və ya Kateqoriya axtar:")
        if axtar:
            df = df[df['mehsul_adi'].str.contains(axtar, case=False) | df['kateqoriya'].str.contains(axtar, case=False)]
        
        mehsul_listesi = df.apply(lambda r: f"{r['mehsul_adi']} ({r['kateqoriya']}) - Stok: {r['miqdar']}", axis=1).tolist()
        secilen_str = st.selectbox("Məhsul seçin:", mehsul_listesi)
        
        if secilen_str:
            idx = mehsul_listesi.index(secilen_str)
            mehsul_row = df.iloc[idx]
            miktar = st.number_input("Satış sayı:", min_value=1, max_value=int(mehsul_row['miqdar']), value=1)
            
            st.metric("Cəmi Məbləğ:", f"{(miktar * mehsul_row['satis_qiymeti']):.2f} AZN")
            
            if st.button("Satışı Tamamla 💸"):
                conn = sqlite3.connect("magaza_sistemi.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE mehsullar SET miqdar = ? WHERE id = ?", (int(mehsul_row['miqdar']) - miktar, int(mehsul_row['id'])))
                cursor.execute("INSERT INTO satislar (mehsul_id, mehsul_adi, kateqoriya, miqdar, satis_qiymeti) VALUES (?, ?, ?, ?, ?)", 
                               (int(mehsul_row['id']), mehsul_row['mehsul_adi'], mehsul_row['kateqoriya'], miktar, mehsul_row['satis_qiymeti']))
                conn.commit()
                conn.close()
                st.success(f"{miktar} ədəd {mehsul_row['mehsul_adi']} satıldı!")
                st.rerun()

elif menyu == "📦 Məhsul Əlavə Et":
    st.subheader("📦 Yeni Məhsul Əlavə Et")
    conn = sqlite3.connect("magaza_sistemi.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT kateqoriya FROM mehsullar")
    movcud_kat = [r[0] for r in cursor.fetchall() if r[0]]
    conn.close()
    
    kat_sec = st.selectbox("Kateqoriya:", ["Yeni yarat..."] + movcud_kat)
    kateqoriya = st.text_input("Kateqoriya adı:", value="" if kat_sec == "Yeni yarat..." else kat_sec)
    mehsul_adi = st.text_input("Məhsulun adı:")
    miqdar = st.number_input("Miqdarı:", min_value=0, value=1)
    alis = st.number_input("Alış qiyməti:", min_value=0.0, value=0.0)
    satis = st.number_input("Satış qiyməti:", min_value=0.0, value=0.0)
    
    if st.button("Bazaya Əlavə Et"):
        conn = sqlite3.connect("magaza_sistemi.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO mehsullar (mehsul_adi, kateqoriya, miqdar, alis_qiymeti, satis_qiymeti) VALUES (?, ?, ?, ?, ?)", 
                       (mehsul_adi, kateqoriya, miqdar, alis, satis))
        conn.commit()
        conn.close()
        st.success(f"{mehsul_adi} uğurla əlavə edildi!")
        st.rerun()

elif menyu == "📊 Mövcud Stok":
    st.subheader("📊 Anbardakı Məhsullar")
    conn = sqlite3.connect("magaza_sistemi.db")
    df = pd.read_sql_query("SELECT * FROM mehsullar", conn)
    conn.close()
    st.dataframe(df)

elif menyu == "📈 Satış Hesabatı":
    st.subheader("📈 Satış Hesabatı")
    conn = sqlite3.connect("magaza_sistemi.db")
    df = pd.read_sql_query("SELECT * FROM satislar", conn)
    conn.close()
    st.dataframe(df)
    st.metric("Ümumi Qazanc:", f"{(df['miqdar'] * df['satis_qiymeti']).sum():.2f} AZN")
