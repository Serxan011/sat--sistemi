import streamlit as str_app
import sqlite3
import pandas as pd
from datetime import datetime

# Səhifə nizamlamaları
str_app.set_page_config(page_title="ProAnbar v2.0", page_icon="⚡", layout="wide")

# MÜASİR CSS DİZAYN KODLARI (Gözəl görünüş üçün)
str_app.markdown("""
    <style>
    /* Səhifənin fon rəngi və ümumi yazı stilləri */
    .stApp {
        background-color: #0f111a;
        color: #e3e6ed;
    }
    
    /* Sol menyunun (Sidebar) dizaynı */
    section[data-testid="stSidebar"] {
        background-color: #161925 !important;
        border-right: 1px solid #23283d;
    }
    
    /* Başlıq dizaynı */
    .main-title {
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #00f2fe;
        text-shadow: 0px 0px 10px rgba(0, 242, 254, 0.3);
        margin-bottom: 20px;
    }
    
    /* Bloklar və Kartlar */
    div[data-testid="stForm"] {
        background-color: #161925 !important;
        border: 1px solid #23283d !important;
        border-radius: 12px !important;
        padding: 25px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }
    
    /* Düymələrin tam dəyişdirilməsi (Premium Gradient) */
    .stButton>button {
        background: linear-gradient(135deg, #0072ff 0%, #00dfa2 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(0, 114, 255, 0.3) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 223, 162, 0.5) !important;
    }
    
    /* Giriş xanaları (Inputs) */
    input, select, textarea {
        background-color: #1f2336 !important;
        color: white !important;
        border: 1px solid #23283d !important;
        border-radius: 6px !important;
    }
    
    /* Kataloq kartları */
    .product-card {
        background-color: #161925;
        border: 1px solid #23283d;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

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
            maya_deyeri REAL DEFAULT 0.0,
            satis_qiymeti REAL NOT NULL,
            stok_miqdari INTEGER DEFAULT 0,
            edv_li TEXT,
            seki_data BLOB
        )
    ''')
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

# Müasir Başlıq
str_app.markdown('<p class="main-title">⚡ PRO-ANBAR // Satış və Sürətli Kassa Sistemi</p>', unsafe_allow_html=True)

# Sol menyu
menyu = str_app.sidebar.selectbox("🧭 Naviqasiya", ["🛒 Sürətli Kassa (Satış)", "✨ Yeni Məhsul Daxil Et", "📊 Aktiv Stok Siyahısı", "📈 Maliyyə Hesabatı"])

# 1. SÜRƏTLİ KASSA
if menyu == "🛒 Sürətli Kassa (Satış)":
    str_app.subheader("🛒 Satış Paneli")
    
    axtarilan_barkod = str_app.text_input("🔍 Barkod aparatını bura vurun və ya kod yazın:", key="kassa_barkod")
    
    conn = sqlite3.connect("anbar_sistemi.db")
    if axtarilan_barkod:
        mehsullar_df = pd.read_sql_query("SELECT id, barkod, ad, satis_qiymeti, maya_deyeri, stok_miqdari, seki_data FROM mehsullar WHERE barkod = ? AND stok_miqdari > 0", conn)
    else:
        mehsullar_df = pd.read_sql_query("SELECT id, barkod, ad, satis_qiymeti, maya_deyeri, stok_miqdari, seki_data FROM mehsullar WHERE stok_miqdari > 0", conn)
    conn.close()
    
    if mehsullar_df.empty:
        if axtarilan_barkod:
            str_app.error("🚨 Bu barkodla məhsul tapılmadı və ya stoku tamamilə bitib!")
        else:
            str_app.warning("⚠️ Satış üçün anbarda məhsul yoxdur. Əvvəlcə məhsul əlavə edin.")
    else:
        mehsullar_df['seçim_adı'] = mehsullar_df['ad'] + " — " + mehsullar_df['satis_qiymeti'].astype(str) + " ₼ (Stok: " + mehsullar_df['stok_miqdari'].astype(str) + ")"
        
        with str_app.form("satis_formu"):
            secilen_mehsul_ad = str_app.selectbox("Satılacaq Məhsul:", mehsullar_df['seçim_adı'].tolist())
            satilacaq_say = str_app.number_input("Miqdar", min_value=1, step=1)
            
            mehsul_setir = mehsullar_df[mehsullar_df['seçim_adı'] == secilen_mehsul_ad].iloc[0]
            if mehsul_setir['seki_data'] is not None:
                str_app.image(mehsul_setir['seki_data'], caption="Məhsulun Görüntüsü", width=180)
                
            satis_tesdiq = str_app.form_submit_button("💳 Satışı Tamamla Və Çek Çıxart")
            
            if satis_tesdiq:
                m_id = int(mehsul_setir['id'])
                m_ad = mehsul_setir['ad']
                m_stok = int(mehsul_setir['stok_miqdari'])
                m_satis = float(mehsul_setir['satis_qiymeti'])
                m_maya = float(mehsul_setir['maya_deyeri'])
                
                if satilacaq_say > m_stok:
                    str_app.error(f"🚨 Anbarda yetərli say yoxdur! Maksimum qalıq: {m_stok}")
                else:
                    conn = sqlite3.connect("anbar_sistemi.db")
                    cursor = conn.cursor()
                    cursor.execute("UPDATE mehsullar SET stok_miqdari = stok_miqdari - ? WHERE id = ?", (satilacaq_say, m_id))
                    indiki_vaxt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute('''
                        INSERT INTO satislar (mehsul_id, miqdar, satis_qiymeti, maya_qiymeti, tarix)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (m_id, satilacaq_say, m_satis, m_maya, indiki_vaxt))
                    conn.commit()
                    conn.close()
                    
                    str_app.success(f"✔️ Satış Tamamlandı! {satilacaq_say} ədəd {m_ad}. Ümumi: {satilacaq_say * m_satis:.2f} ₼")
                    str_app.balloons()

# 2. MƏHSUL ƏLAVƏ ET
elif menyu == "✨ Yeni Məhsul Daxil Et":
    str_app.subheader("✨ Sürətli Qeydiyyat Paneli")
    
    with str_app.form("mehsul_formu", clear_on_submit=True):
        col1, col2 = str_app.columns(2)
        with col1:
            ad = str_app.text_input("Məhsulun Peşəkar Adı *")
            barkod = str_app.text_input("Barkod / Artikul Kodu")
            kategoriya = str_app.text_input("Malın Kateqoriyası")
            yuklenen_seki = str_app.file_uploader("🖼️ Məhsulun Şəklini Yüklə", type=["jpg", "jpeg", "png"])
        with col2:
            maya = str_app.number_input("Maya Qiyməti (₼)", min_value=0.0, step=0.1)
            satis = str_app.number_input("Satış Qiyməti (₼)", min_value=0.0, step=0.1)
            stok = str_app.number_input("Başlanğıc Stok Sayı *", min_value=0, step=1)
            edv = str_app.selectbox("Vergi (ƏDV)", ["ƏDV-siz", "ƏDV-li (18%)"])
            
        submit = str_app.form_submit_button("💾 Məhsulu Bazaya Yaz")
        
        if submit:
            if not ad or not satis:
                str_app.error("🚨 Vacib xanaları doldurun!")
            else:
                seki_bytes = None
                if yuklenen_seki is not None:
                    seki_bytes = yuklenen_seki.read()
                    
                try:
                    conn = sqlite3.connect("anbar_sistemi.db")
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO mehsullar (barkod, ad, kategoriya, maya_deyeri, satis_qiymeti, stok_miqdari, edv_li, seki_data)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (barkod, ad, kategoriya, float(maya), float(satis), int(stok), edv, seki_bytes))
                    conn.commit()
                    conn.close()
                    str_app.success(f"✔️ '{ad}' uğurla sistemə daxil edildi!")
                except:
                    str_app.error("🚨 Bu barkod kodu artıq istifadə edilib!")

# 3. AKTİV STOK SİYAHISI
elif menyu == "📊 Aktiv Stok Siyahısı":
    str_app.subheader("📊 Stok Vəziyyəti")
    
    conn = sqlite3.connect("anbar_sistemi.db")
    cursor = conn.cursor()
    cursor.execute("SELECT barkod, ad, kategoriya, maya_deyeri, satis_qiymeti, stok_miqdari, edv_li, seki_data FROM mehsullar")
    mallar = cursor.fetchall()
    conn.close()
    
    if not mallar:
        str_app.info("Anbarda mal tapılmadı.")
    else:
        data = []
        for mal in mallar:
            data.append({
                "Barkod": mal[0],
                "Məhsul Adı": mal[1],
                "Kateqoriya": mal[2],
                "Maya (₼)": mal[3],
                "Satış (₼)": mal[4],
                "Stok Sayı": mal[5],
                "ƏDV Statusu": mal[6]
            })
        df = pd.DataFrame(data)
        str_app.dataframe(df, use_container_width=True)
        
        str_app.markdown("### 🖼️ Vizual Kataloq")
        for mal in mallar:
            str_app.markdown(f"""
            <div class="product-card">
                <table style="width:100%; border:none;">
                    <tr>
                        <td style="width:80%;">
                            <h4 style="color:#00f2fe; margin:0;">{mal[1]}</h4>
                            <p style="margin:5px 0; color:#a2a8b9;">Kateqoriya: {mal[2]} | Barkod: {mal[0]}</p>
                            <b style="color:#00dfa2;">Satış: {mal[4]} ₼</b> | <span style="color:#ff4b4b;">Stok: {mal[5]} ədəd</span>
                        </td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

# 4. MALİYYƏ HESABATI
elif menyu == "📈 Maliyyə Hesabatı":
    str_app.subheader("📈 Qazanc və Dövriyyə")
    
    conn = sqlite3.connect("anbar_sistemi.db")
    query = '''
        SELECT s.tarix As [Tarix], m.ad As [Məhsul Adı], s.miqdar As [Miqdar], 
               s.satis_qiymeti As [Satış Qiyməti],
               (s.miqdar * s.satis_qiymeti) As [Ümumi Ciro],
               ((s.miqdar * s.satis_qiymeti) - (s.miqdar * s.maya_qiymeti)) As [Xalis Mənfəət]
        FROM satislar s
        JOIN mehsullar m ON s.mehsul_id = m.id
        ORDER BY s.tarix DESC
    '''
    df_satis = pd.read_sql_query(query, conn)
    conn.close()
    
    if df_satis.empty:
        str_app.info("Satış hesabatı boşdur.")
    else:
        toplam_ciro = df_satis['Ümumi Ciro'].sum()
        toplam_qazanc = df_satis['Xalis Mənfəət'].sum()
        
        col1, col2 = str_app.columns(2)
        col1.metric("💰 Ümumi Ciro", f"{toplam_ciro:.2f} ₼")
        col2.metric("🔥 Xalis Mənfəət (Xalis Qazanc)", f"{toplam_qazanc:.2f} ₼")
        
        str_app.markdown("---")
        str_app.dataframe(df_satis, use_container_width=True)
