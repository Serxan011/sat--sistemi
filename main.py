import streamlit as st
import sqlite3
import pandas as pd

# Səhifə Ayarları
st.set_page_config(page_title="NN Mağaza", page_icon="⚡", layout="centered")

# Verilənlər Bazası Qurulması
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

# Əsas Başlıq (Sadə dildə)
st.markdown("<h1 style='text-align: center; color: #00d2ff;'>⚡ NN Mağaza</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Satış və Sürətli Kassa Sistemi</p>", unsafe_allow_html=True)
st.write("---")

# Yan Menyuda Naviqasiya
menyu = st.sidebar.radio("Bölmələr:", ["🛒 Satış Ekranı", "📦 Məhsul Əlavə Et", "📊 Mövcud Stok", "📈 Satış Hesabatı"])

# 1. SATIŞ EKRANI
if menyu == "🛒 Satış Ekranı":
    st.subheader("Sürətli Satış")
    conn = sqlite3.connect("magaza_sistemi.db")
    df = pd.read_sql_query("SELECT * FROM mehsullar WHERE miqdar > 0", conn)
    conn.close()
    
    if df.empty:
        st.warning("Bazada satıla biləcək məhsul yoxdur. Əvvəlcə məhsul əlavə edin.")
    else:
        mehsul_listesi = df.apply(lambda r: f"{r['mehsul_adi']} ({r['kateqoriya']}) - Stok: {r['miqdar']} ədəd", axis=1).tolist()
        secilen_mehsul_str = st.selectbox("Məhsul Seçin:", mehsul_listesi)
        
        idx = mehsul_listesi.index(secilen_mehsul_str)
        mehsul_row = df.iloc[idx]
        
        satilacaq_miqdar = st.number_input("Satış Miqdarı:", min_value=1, max_value=int(mehsul_row['miqdar']), value=1)
        
        if st.button("Satışı Tamamla 💸"):
            conn = sqlite3.connect("magaza_sistemi.db")
            cursor = conn.cursor()
            
            # Stoku azalt
            yeni_stok = int(mehsul_row['miqdar']) - satilacaq_miqdar
            cursor.execute("UPDATE mehsullar SET miqdar = ? WHERE id = ?", (yeni_stok, int(mehsul_row['id'])))
            
            # Satışı qeyd et
            cursor.execute("""
                INSERT INTO satislar (mehsul_id, mehsul_adi, kateqoriya, miqdar, satis_qiymeti)
                VALUES (?, ?, ?, ?, ?)
            """, (int(mehsul_row['id']), mehsul_row['mehsul_adi'], mehsul_row['kateqoriya'], satilacaq_miqdar, mehsul_row['satis_qiymeti']))
            
            conn.commit()
            conn.close()
            st.success(f"Uğurlu Satış! {satilacaq_miqdar} ədəd {mehsul_row['mehsul_adi']} satıldı.")
            st.rerun()

# 2. MƏHSUL ƏLAVƏ ET
elif menyu == "📦 Məhsul Əlavə Et":
    st.subheader("Yeni Məhsul Girişi")
    
    conn = sqlite3.connect("magaza_sistemi.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT kateqoriya FROM mehsullar")
    movcud_kat = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    
    # Kateqoriya seçimi açılan siyahı ilə
    kat_secimleri = ["Mövcud olanlardan seç..."] + movcud_kat + ["+ Yeni Kateqoriya Yarat..."]
    secilen_kat = st.selectbox("Kateqoriya Seçin:", kat_secimleri)
    
    if secilen_kat == "+ Yeni Kateqoriya Yarat...":
        kateqoriya = st.text_input("Yeni Kateqoriyanın Adı (Məs: LDSP, DSP, Mexanizm):")
    elif secilen_kat == "Mövcud olanlardan seç...":
        kateqoriya = ""
    else:
        kateqoriya = secilen_kat
        
    mehsul_adi = st.text_input("Məhsulun Adı:")
    miqdar = st.number_input("Miqdarı (Stok):", min_value=1, value=10)
    alis_qiymeti = st.number_input("Alış Qiyməti (AZN):", min_value=0.0, value=0.0, step=0.5)
    satis_qiymeti = st.number_input("Satış Qiyməti (AZN):", min_value=0.0, value=0.0, step=0.5)
    
    if st.button("Məhsulu Bazaya Əlavə Et 💾"):
        if not kateqoriya or not mehsul_adi:
            st.error("Zəhmət olmasa Məhsulun Adını və Kateqoriyasını doldurun!")
        else:
            conn = sqlite3.connect("magaza_sistemi.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO mehsullar (mehsul_adi, kateqoriya, miqdar, alis_qiymeti, satis_qiymeti)
                VALUES (?, ?, ?, ?, ?)
            """, (mehsul_adi, kateqoriya, miqdar, alis_qiymeti, satis_qiymeti))
            conn.commit()
            conn.close()
            st.success(f"{mehsul_adi
