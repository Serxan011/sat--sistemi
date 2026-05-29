import streamlit as st
import sqlite3

# 1. Baza qurulması
def bazani_qur():
    conn = sqlite3.connect("magaza.db")
    c = conn.cursor()
    # Bütün köhnəni silib, təzə və təmiz cədvəl yaradırıq
    c.execute("DROP TABLE IF EXISTS mehsullar")
    c.execute("CREATE TABLE mehsullar (id INTEGER PRIMARY KEY, ad TEXT, qiymet REAL)")
    conn.commit()
    conn.close()

# Proqram işə düşəndə bazanı qurur
bazani_qur()

st.title("NN Mağaza - Sadə Kassa")

# 2. Məhsul Əlavə Etmə
ad = st.text_input("Məhsulun adı:")
qiymet = st.number_input("Qiyməti:")

if st.button("Əlavə Et"):
    conn = sqlite3.connect("magaza.db")
    c = conn.cursor()
    c.execute("INSERT INTO mehsullar (ad, qiymet) VALUES (?,?)", (ad, qiymet))
    conn.commit()
    conn.close()
    st.success("Əlavə edildi!")

# 3. Məhsulları göstər
conn = sqlite3.connect("magaza.db")
import pandas as pd
df = pd.read_sql("SELECT * FROM mehsullar", conn)
st.write(df)
conn.close()
