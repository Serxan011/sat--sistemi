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

# Ana Başlıq
st.markdown("<h1 style='text-align: center; color: #00d2ff;'>⚡ NN Mağaza</h1>", unsafe_allow_html=True)

# Yan Menyuda Naviqasiya
menyu = st.sidebar.radio("Menyu:", ["🛒 Satış Ekranı", "📦 Məhsul Əlavə Et", "📊 Mövcud Stok", "📈 Satış Hesabatı"])

# 1. SATIŞ EKRANI (Ana Səhifə)
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
            
            # Cəmi Məbləğ Hesabı
            ceymi_mebleg = miktar * mehsul_row['satis_qiymeti']
            st.metric("Cəmi Məbləğ:", f"{ceymi_mebleg:.2f} AZN")
            
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

# 2. MƏHSUL ƏLAVƏ ET
elif menyu == "📦 Məhsul Əlavə Et":
    st.subheader("📦 Yeni Məhsul Əlavə Et")
    # ... (Bayaqkı kodla eyni qala bilər)
    st.info("Məhsul əlavə etmək üçün bu bölməni doldurun.")
    # (Bura bayaqkı məhsul əlavə etmə kodunu qoyun)

# 3. MÖVCUD STOK
elif menyu == "📊 Mövcud Stok":
    st.subheader("📊 Anbardakı Məhsullar")
    # ... (Bayaqkı kodla eyni)

# 4. SATIŞ HESABATI
elif menyu == "📈 Satış Hesabatı":
    st.subheader("📈 Satışlar və Qazanc")
    # ... (Bayaqkı kodla eyni)
