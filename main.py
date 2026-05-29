import streamlit as str_app
import sqlite3
import pandas as pd
from datetime import datetime

# Səhifə nizamlamaları
str_app.set_page_config(page_title="Anbar və Satış Sistemi", page_icon="📦", layout="wide")

# Verilənlər bazası funksiyası (Cədvəlləri qururuq)
def bazani_qur():
    conn = sqlite3.connect("anbar_sistemi.db")
    cursor = conn.cursor()
    # Məhsullar cədvəli
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mehsullar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barkod TEXT UNIQUE,
            ad TEXT NOT NULL,
            kategoriya TEXT,
            maya_deyeri REAL DEFAULT 0.0,
            satis_qiymeti REAL NOT NULL,
            stok_miqdari INTEGER DEFAULT 0,
            edv_li TEXT
        )
    ''')
    # Satışlar cədvəli
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS satislar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mehsul_id INTEGER,
            miqdar INTEGER,
            satis_qiymeti REAL,
            maya_qiymeti REAL,
            tarix TEXT,
            FOREIGN KEY (mehsul_id) REFERENCES mehsullar(id)
        )
    ''')
    conn.commit()
    conn.close()

bazani_qur()

str_app.title("📦 Satış və Geniş Tutumlu Anbar Sistemi")
str_app.markdown("---")

# Sol menyu
menyu = str_app.sidebar.selectbox("Bölmə Seçin", ["🛒 Satış Ekranı (Kassa)", "✨ Məhsul Əlavə Et", "📊 Məhsul Siyahısı və Stok", "📈 Satış Hesabatı (Qazanc)"])

# 1. SATIŞ EKRANI
if menyu == "🛒 Satış Ekranı (Kassa)":
    str_app.subheader("🛒 Canlı Satış Paneli")
    
    conn = sqlite3.connect("anbar_sistemi.db")
    mehsullar_df = pd.read_sql_query("SELECT id, barkod, ad, satis_qiymeti, maya_deyeri, stok_miqdari FROM mehsullar WHERE stok_miqdari > 0", conn)
    conn.close()
    
    if mehsullar_df.empty:
        str_app.warning("⚠️ Satış etmək üçün anbarda mal yoxdur! Zəhmət olmasa əvvəlcə məhsul əlavə edin.")
    else:
        # Seçim üçün siyahı hazırlayırıq
        mehsullar_df['seçim_adı'] = mehsullar_df['ad'] + " (" + mehsullar_df['satis_qiymeti'].astype(str) + " ₼) - Stok: " + mehsullar_df['stok_miqdari'].astype(str)
        
        with str_app.form("satis_formu"):
            secilen_mehsul_ad = str_app.selectbox("Məhsulu Seçin", mehsullar_df['seçim_adı'].tolist())
            satilacaq_say = str_app.number_input("Satış Miqdarı", min_value=1, step=1)
            
            satis_tesdiq = str_app.form_submit_button("💳 Satışı Tamamla")
            
            if satis_tesdiq:
                # Seçilən məhsulun məlumatlarını ayırırıq
                mehsul_setir = mehsullar_df[mehsullar_df['seçim_adı'] == secilen_mehsul_ad].iloc[0]
                m_id = int(mehsul_setir['id'])
                m_ad = mehsul_setir['ad']
                m_stok = int(mehsul_setir['stok_miqdari'])
                m_satis = float(mehsul_setir['satis_qiymeti'])
                m_maya = float(mehsul_setir['maya_deyeri'])
                
                if satilacaq_say > m_stok:
                    str_app.error(f"🚨 Xəta! Anbarda yetəri qədər mal yoxdur. Maksimum satıla bilən: {m_stok} ədəd.")
                else:
                    conn = sqlite3.connect("anbar_sistemi.db")
                    cursor = conn.cursor()
                    
                    # 1. Stokdan çıxırıq
                    cursor.execute("UPDATE mehsullar SET stok_miqdari = stok_miqdari - ? WHERE id = ?", (satilacaq_say, m_id))
                    
                    # 2. Satış tarixinə yazırıq
                    indiki_vaxt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute('''
                        INSERT INTO satislar (mehsul_id, miqdar, satis_qiymeti, maya_qiymeti, tarix)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (m_id, satilacaq_say, m_satis, m_maya, indiki_vaxt))
                    
                    conn.commit()
                    conn.close()
                    
                    str_app.success(f"✔️ {satilacaq_say} ədəd '{m_ad}' uğurla satıldı! Ümumi Məbləğ: {satilacaq_say * m_satis:.2f} ₼")
                    str_app.balloons()

# 2. MƏHSUL ƏLAVƏ ET
elif menyu == "✨ Məhsul Əlavə Et":
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
                str_app.error("🚨 Məhsul adı və Satış qiyməti boş qala bilməz!")
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
                    str_app.success(f"✔️ '{ad}' uğurla stoka əlavə edildi!")
                except:
                    str_app.error("🚨 Xəta! Bu barkod nömrəsi artıq sistemdə var.")

# 3. MƏHSUL SİYAHISI
elif menyu == "📊 Məhsul Siyahısı və Stok":
    str_app.subheader("📊 Stokda Olan Mallar və Qalıq Sayı")
    
    conn = sqlite3.connect("anbar_sistemi.db")
    df = pd.read_sql_query("SELECT barkod As [Barkod], ad As [Məhsul Adı], kategoriya As [Kateqoriya], maya_deyeri As [Maya (₼)], satis_qiymeti As [Satış (₼)], stok_miqdari As [Stokda Qalan Say], edv_li As [ƏDV] FROM mehsullar", conn)
    conn.close()
    
    if not df.empty:
        str_app.dataframe(df, use_container_width=True)
    else:
        str_app.info("Anbarda hələ ki mal yoxdur. Sol menyudan məhsul əlavə edin.")

# 4. SATIŞ HESABATI (QAZANC)
elif menyu == "📈 Satış Hesabatı (Qazanc)":
    str_app.subheader("📈 Satış və Xalis Qazanc Hesabatı")
    
    conn = sqlite3.connect("anbar_sistemi.db")
    query = '''
        SELECT s.tarix As [Tarix], m.ad As [Məhsul Adı], s.miqdar As [Miqdar], 
               s.satis_qiymeti As [Satış Qiyməti (₼)], s.maya_qiymeti As [Maya Qiyməti (₼)],
               (s.miqdar * s.satis_qiymeti) As [Ümumi Ciro (₼)],
               ((s.miqdar * s.satis_qiymeti) - (s.miqdar * s.maya_qiymeti)) As [Xalis Qazanc (₼)]
        FROM satislar s
        JOIN mehsullar m ON s.mehsul_id = m.id
        ORDER BY s.tarix DESC
    '''
    df_satis = pd.read_sql_query(query, conn)
    conn.close()
    
    if df_satis.empty:
        str_app.info("Hələ ki heç bir satış edilməyib.")
    else:
        toplam_ciro = df_satis['Ümumi Ciro (₼)'].sum()
        toplam_qazanc = df_satis['Xalis Qazanc (₼)'].sum()
        
        col1, col2 = str_app.columns(2)
        col1.metric("💰 Ümumi Dövriyyə (Ciro)", f"{toplam_ciro:.2f} ₼")
        col2.metric("📈 Toplam Xalis Qazanc", f"{toplam_qazanc:.2f} ₼")
        
        str_app.markdown("---")
        str_app.dataframe(df_satis, use_container_width=True)
