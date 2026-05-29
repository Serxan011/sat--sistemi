import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Baza qurulması (daha ətraflı sütunlarla)
def bazani_qur():
    conn = sqlite3.connect("magaza.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS mehsullar 
                 (id INTEGER PRIMARY KEY, ad TEXT, kat TEXT, alis REAL, satis REAL, sekil TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS satislar 
                 (id INTEGER PRIMARY KEY, mehsul TEXT, say INTEGER, toplam REAL, tarix DATE)""")
    conn.commit()
    conn.close()

bazani_qur()

st.title("⚡ NN Mağaza PRO")
menu = st.sidebar.radio("Menyu:", ["🛒 Kassa (Səbət)", "📦 Məhsul Girişi", "📈 Hesabat"])

if menu == "📦 Məhsul Girişi":
    ad = st.text_input("Məhsul adı:")
    alis = st.number_input("Alış (ƏDV-siz):")
    edv = st.selectbox("ƏDV faizi:", [0, 18])
    satis = st.number_input("Satış qiyməti:")
    # Maya dəyəri (ƏDV-li) avtomatik hesablanır
    maya = alis * (1 + edv/100)
    st.write(f"**Maya dəyəri (ƏDV daxil):** {maya:.2f} AZN")
    
    if st.button("Bazaya vur"):
        conn = sqlite3.connect("magaza.db")
        conn.execute("INSERT INTO mehsullar (ad, alis, satis) VALUES (?,?,?)", (ad, maya, satis))
        conn.commit()
        conn.close()
        st.success("Məhsul əlavə olundu!")

elif menu == "🛒 Kassa (Səbət)":
    conn = sqlite3.connect("magaza.db")
    df = pd.read_sql("SELECT * FROM mehsullar", conn)
    conn.close()
    
    if 'sebet' not in st.session_state: st.session_state.sebet = []
    
    secilen = st.selectbox("Məhsul seç:", df['ad'].tolist() if not df.empty else [])
    say = st.number_input("Say:", min_value=1, value=1)
    
    if st.button("Səbətə at"):
        row = df[df['ad'] == secilen].iloc[0]
        st.session_state.sebet.append({"ad": secilen, "say": say, "toplam": row['satis'] * say})
        
    st.write("### Səbətdəkilər:")
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
        st.success("Satış qeyd edildi!")

elif menu == "📈 Hesabat":
    conn = sqlite3.connect("magaza.db")
    st.write("### Günlük Satışlar")
    tarix = st.date_input("Tarix seç:")
    df_satis = pd.read_sql(f"SELECT * FROM satislar WHERE tarix = '{tarix}'", conn)
    st.write(df_satis)
    st.metric("Ümumi dövriyyə:", f"{df_satis['toplam'].sum():.2f} AZN")
    conn.close()
