import streamlit as str_app
import sqlite3
import pandas as pd

# Səhifə nizamlamaları
str_app.set_page_config(page_title="Anbar və Satış Sistemi", page_icon="📦", layout="wide")

# Verilənlər bazası funksiyası
def bazani_qur():
    conn = sqlite3.connect("anbar_sistemi.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mehsullar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barkod TEXT UNIQUE,
            ad TEXT NOT NULL,
            kategoriya TEXT,
            maya_deyeri REAL,
            satis_qiymeti REAL,
            stok_miqdari INTEGER DEFAULT 0,
            edv_li TEXT
        )
    ''')
    conn.commit()
    conn.close()

bazani_qur()

str_app.title("📦 Satış və Geniş Tutumlu Anbar Sistemi")
str_app.markdown("---")

# Sol menyu
menyu = str_app.sidebar.selectbox("Bölmə Seçin", ["Məhsul Əlavə Et", "Məhsul Siyahısı və Stok"])

if menyu == "Məhsul Əlavə Et":
    str_app.subheader("✨ Yeni Məhsul Qeydiyyatı")
    
    with str_app.form("mehsul_formu", clear_on_submit=True):
        col1, col2 = str_app.columns(2)
        with col1:
            ad = str_app.text_input("Məhsulun Adı *")
            barkod = str_app.text_input("Barkod (Və ya Kod)")
            kategoriya = str_app.text_input("Kateqoriya")
        with col2:
            maya = str_app.number_input("Maya Dəyəri (₼)", min_value=0.0, step=0.1)
            satis = str_app.number_input("Satış Qiyməti (₼)", min_value=0.0, step=0.1)
            stok = str_app.number_input("Anbar Stok Sayı *", min_value=0, step=1)
            edv = str_app.selectbox("ƏDV Statusu", ["ƏDV-siz", "ƏDV-li (18%)"])
            
        submit = str_app.form_submit_button("💾 Məhsulu Sistemə Daxil Et")
        
        if submit:
            if not ad or not satis:
                str_app.error("🚨 Məhsul adı və Satış qiyməti boş qala bilmez!")
            else:
                try:
                    conn = sqlite3.connect("anbar_sistemi.db")
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO mehsullar (barkod, ad, kategoriya, maya_deyeri, satis_qiymeti, stok_miqdari, edv_li)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (barkod, ad, kategoriya, float(maya), float(satis), int(stok), edv))
                    conn.commit()
                    conn.close()
                    str_app.success(f"✔️ '{ad}' uğurla stoka əlavə edildi! Anbarda qalan: {stok} ədəd.")
                except:
                    str_app.error("🚨 Xəta! Bu barkod nömrəsi artıq sistemdə var.")

elif menyu == "Məhsul Siyahısı və Stok":
    str_app.subheader("📊 Stokda Olan Mallar və Qalıq Sayı")
    
    conn = sqlite3.connect("anbar_sistemi.db")
    df = pd.read_sql_query("SELECT barkod As [Barkod], ad As [Məhsul Adı], kategoriya As [Kateqoriya], maya_deyeri As [Maya (₼)], satis_qiymeti As [Satış (₼)], stok_miqdari As [Stokda Qalan Say], edv_li As [ƏDV] FROM mehsullar", conn)
    conn.close()
    
    if not df.empty:
        str_app.dataframe(df, use_container_width=True)
    else:
        str_app.info("Anbarda hələ ki mal yoxdur. Sol menyudan məhsul əlavə edin.")
