import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="NN Mağaza", layout="wide")

# Verilənlər bazası və şəkil qovluğu
if not os.path.exists("sekiller"): os.makedirs("sekiller")
conn = sqlite3.connect("magaza.db")
conn.execute("CREATE TABLE IF NOT EXISTS mehsullar (id INTEGER PRIMARY KEY, ad TEXT, kat TEXT, miqdar INTEGER, satis REAL, sekil_yolu TEXT)")
conn.close()

st.title("⚡ NN Mağaza İdeal Kassa")

menu = st.sidebar.radio("Menyu:", ["🛒 Kassa", "📦 Məhsul Əlavə", "📊 Stok"])

if menu == "🛒 Kassa":
    conn = sqlite3.connect("magaza.db")
    df = pd.read_sql("SELECT * FROM mehsullar", conn)
    conn.close()
    
    if 'sebet' not in st.session_state: st.session_state.sebet = []
    
    col1, col2 = st.columns([1, 2])
    with col1:
        secilen = st.selectbox("Məhsul seç:", df['ad'].tolist())
        miktar = st.number_input("Say:", min_value=1, value=1)
        if st.button("Səbətə at"):
            row = df[df['ad'] == secilen].iloc[0]
            st.session_state.sebet.append({"ad": secilen, "say": miktar, "toplam": row['satis'] * miktar})
            
    with col2:
        st.write("### Səbət")
        for i, item in enumerate(st.session_state.sebet):
            c1, c2 = st.columns([3, 1])
            c1.write(f"{item['ad']} x {item['say']} = {item['toplam']} AZN")
            if c2.button("Sil", key=i):
                st.session_state.sebet.pop(i)
                st.rerun()
        if st.button("Satışı Tamamla"):
            st.session_state.sebet = []
            st.success("Satış tamamlandı!")

elif menu == "📦 Məhsul Əlavə":
    ad = st.text_input("Məhsulun adı:")
    kat = st.text_input("Kateqoriya:")
    miqdar = st.number_input("Miqdar:")
    satis = st.number_input("Satış qiyməti:")
    edv = st.selectbox("ƏDV %", [0, 18])
    qiymet_edvli = satis * (1 + edv/100)
    
    # Şəkil yükləmə
    uploaded_file = st.file_uploader("Məhsul şəkli seç:", type=['jpg', 'png'])
    
    if st.button("Bazaya vur"):
        yol = ""
        if uploaded_file:
            yol = f"sekiller/{uploaded_file.name}"
            with open(yol, "wb") as f: f.write(uploaded_file.getbuffer())
        
        conn = sqlite3.connect("magaza.db")
        conn.execute("INSERT INTO mehsullar (ad, kat, miqdar, satis, sekil_yolu) VALUES (?,?,?,?,?)", 
                     (ad, kat, miqdar, qiymet_edvli, yol))
        conn.commit()
        conn.close()
        st.success("Məhsul əlavə edildi!")

elif menu == "📊 Stok":
    conn = sqlite3.connect("magaza.db")
    df = pd.read_sql("SELECT * FROM mehsullar", conn)
    for i, row in df.iterrows():
        c1, c2 = st.columns([1, 3])
        if os.path.exists(str(row['sekil_yolu'])):
            c1.image(row['sekil_yolu'], width=100)
        c2.write(f"**{row['ad']}** | {row['kat']} | {row['satis']} AZN | Stok: {row['miqdar']}")
    conn.close()
