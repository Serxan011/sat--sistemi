import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="NN Mağaza Pro", layout="wide")

def bazani_qur():
    conn = sqlite3.connect("magaza_sistemi.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mehsullar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mehsul_adi TEXT, kateqoriya TEXT, miqdar INTEGER,
            alis_qiymeti REAL, satis_qiymeti REAL, sekil_url TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS satislar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mehsul_adi TEXT, miqdar INTEGER, toplam_qiymet REAL, tarih TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

bazani_qur()

st.title("⚡ NN Mağaza Pro")

# Yan Menyu
menyu = st.sidebar.radio("Menyu:", ["🛒 Kassa (Səbətli)", "📦 Məhsul Əlavə", "📊 Stok", "📈 Satışlar"])

# 1. KASSA (Səbət sistemi)
if menyu == "🛒 Kassa (Səbətli)":
    st.subheader("Səbətli Satış Sistemi")
    conn = sqlite3.connect("magaza_sistemi.db")
    df = pd.read_sql("SELECT * FROM mehsullar WHERE miqdar > 0", conn)
    conn.close()
    
    if 'sebet' not in st.session_state: st.session_state.sebet = []
    
    col1, col2 = st.columns(2)
    with col1:
        secilen_mehsul = st.selectbox("Məhsul seç:", df['mehsul_adi'].tolist())
        miktar = st.number_input("Say:", min_value=1, value=1)
        if st.button("Səbətə əlavə et"):
            row = df[df['mehsul_adi'] == secilen_mehsul].iloc[0]
            st.session_state.sebet.append({"ad": secilen_mehsul, "say": miktar, "qiymet": row['satis_qiymeti'] * miktar})
            
    with col2:
        st.write("### Səbətiniz:")
        for i, item in enumerate(st.session_state.sebet):
            if st.button(f"Sil: {item['ad']}", key=f"sil_{i}"):
                st.session_state.sebet.pop(i)
                st.rerun()
            st.write(f"{item['ad']} - {item['say']} ədəd - {item['qiymet']} AZN")
            
    if st.button("Satışı tamamla"):
        st.session_state.sebet = []
        st.success("Satış uğurla tamamlandı!")

# 2. MƏHSUL ƏLAVƏ (ƏDV ilə)
elif menyu == "📦 Məhsul Əlavə":
    mehsul_adi = st.text_input("Adı:")
    kat = st.text_input("Kateqoriya:")
    miqdar = st.number_input("Miqdar:")
    alis = st.number_input("Alış:")
    satis_net = st.number_input("Satış (ƏDV-siz):")
    edv = st.selectbox("ƏDV dərəcəsi:", [0, 18])
    satis_edvli = satis_net * (1 + edv/100)
    sekil = st.text_input("Şəkil linki (URL):")
    
    if st.button("Əlavə et"):
        conn = sqlite3.connect("magaza_sistemi.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO mehsullar (mehsul_adi, kateqoriya, miqdar, alis_qiymeti, satis_qiymeti, sekil_url) VALUES (?,?,?,?,?,?)",
                       (mehsul_adi, kat, miqdar, alis, satis_edvli, sekil))
        conn.commit()
        conn.close()
        st.success("Əlavə edildi!")

elif menyu == "📊 Stok":
    conn = sqlite3.connect("magaza_sistemi.db")
    df = pd.read_sql("SELECT * FROM mehsullar", conn)
    st.dataframe(df)
