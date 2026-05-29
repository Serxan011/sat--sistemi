import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="NN Mağaza İdeal", layout="wide")

# Bazanın qurulması (Genişləndirilmiş)
def bazani_qur():
    conn = sqlite3.connect("magaza.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS mehsullar 
                 (id INTEGER PRIMARY KEY, ad TEXT, kat TEXT, miqdar INTEGER, 
                  alis_qiymet REAL, satis_qiymet REAL, edv_faiz INTEGER, sekil TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS satislar 
                 (id INTEGER PRIMARY KEY, mehsul TEXT, say INTEGER, toplam REAL, tarix DATE)""")
    conn.commit()
    conn.close()

bazani_qur()

st.title("⚡ NN Mağaza İdeal Kassa")

menu = st.sidebar.radio("Bölmələr:", ["🛒 Kassa", "📦 Məhsul Girişi", "📊 Stok və Hesabat"])

if menu == "🛒 Kassa":
    st.subheader("Satış Ekranı")
    conn = sqlite3.connect("magaza.db")
    df = pd.read_sql("SELECT * FROM mehsullar", conn)
    conn.close()
    
    axtar = st.text_input("🔍 Məhsul adı və ya Kateqoriya axtar:")
    if axtar: df = df[df['ad'].str.contains(axtar, case=False) | df['kat'].str.contains(axtar, case=False)]
    
    if 'sebet' not in st.session_state: st.session_state.sebet = []
    
    col1, col2 = st.columns([1, 1])
    with col1:
        secilen = st.selectbox("Məhsul seç:", df['ad'].tolist())
        miktar = st.number_input("Say:", min_value=1, value=1)
        if st.button("Səbətə əlavə et"):
            row = df[df['ad'] == secilen].iloc[0]
            st.session_state.sebet.append({"ad": secilen, "say": miktar, "toplam": row['satis_qiymet'] * miktar})
            
    with col2:
        st.write("### Səbət")
        if st.session_state.sebet:
            sebet_df = pd.DataFrame(st.session_state.sebet)
            st.write(sebet_df)
            if st.button("Satışı Tamamla"):
                conn = sqlite3.connect("magaza.db")
                for _, item in sebet_df.iterrows():
                    conn.execute("INSERT INTO satislar (mehsul, say, toplam, tarix) VALUES (?,?,?,?)", 
                                 (item['ad'], item['say'], item['toplam'], datetime.now().date()))
                conn.commit()
                conn.close()
                st.session_state.sebet = []
                st.success("Satış uğurla qeyd edildi!")

elif menu == "📦 Məhsul Girişi":
    ad = st.text_input("Məhsulun adı:")
    kat = st.text_input("Kateqoriya:")
    alis = st.number_input("Alış qiyməti (ƏDV-siz):")
    edv = st.selectbox("ƏDV %", [0, 18])
    satis = st.number_input("Satış qiyməti:")
    miqdar = st.number_input("Stok miqdarı:")
    
    # Maya dəyəri hesabı (avtomatik)
    maya = alis * (1 + edv/100)
    st.write(f"### Maya dəyəri (ƏDV daxil): {maya:.2f} AZN")
    
    sekil = st.file_uploader("Şəkil yüklə:", type=['jpg', 'png'])
    
    if st.button("Bazaya vur"):
        conn = sqlite3.connect("magaza.db")
        conn.execute("INSERT INTO mehsullar (ad, kat, miqdar, alis_qiymet, satis_qiymet, edv_faiz) VALUES (?,?,?,?,?,?)", 
                     (ad, kat, miqdar, maya, satis, edv))
        conn.commit()
        conn.close()
        st.success("Məhsul əlavə edildi!")

elif menu == "📊 Stok və Hesabat":
    conn = sqlite3.connect("magaza.db")
    df_stok = pd.read_sql("SELECT * FROM mehsullar", conn)
    df_satis = pd.read_sql("SELECT * FROM satislar", conn)
    conn.close()
    
    st.write("### Stok vəziyyəti")
    st.dataframe(df_stok)
    
    st.write("### Satış Hesabatı (Günlük/Aylıq)")
    tarix_filtri = st.date_input("Tarix seçin:")
    hesabat = df_satis[df_satis['tarix'] == str(tarix_filtri)]
    st.dataframe(hesabat)
    st.metric("Bu tarix üçün ümumi dövriyyə:", f"{hesabat['toplam'].sum():.2f} AZN")
