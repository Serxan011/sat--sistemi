import streamlit as str_app
import sqlite3
import pandas as pd
from datetime import datetime

# Səhifə nizamlamaları
str_app.set_page_config(page_title="Anbar və Satış Sistemi", page_icon="📦", layout="wide")

# Verilənlər bazası funksiyası
def bazani_qur():
    conn = sqlite3.connect("anbar_sistemi.db")
    cursor = conn.cursor()
    # Məhsullar cədvəli (seki_data sütunu əlavə edildi)
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

# 1. SATIŞ EKRANI (Barkod Aparatı Dəstəkli)
if menyu == "🛒 Satış Ekranı (Kassa)":
    str_app.subheader("🛒 Canlı Satış Paneli")
    
    # Barkod aparatı üçün sürətli axtarış qutusu
    axtarilan_barkod = str_app.text_input("🔍 Barkod Oxudun (Və ya Əllə Yazın):", key="kassa_barkod")
    
    conn = sqlite3.connect("anbar_sistemi.db")
    if axtarilan_barkod:
        mehsullar_df = pd.read_sql_query("SELECT id, barkod, ad, satis_qiymeti, maya_deyeri, stok_miqdari, seki_data FROM mehsullar WHERE barkod = ? AND stok_miqdari > 0", conn, params=(axtarilan_barkod,))
    else:
        mehsullar_df = pd.read_sql_query("SELECT id, barkod, ad, satis_qiymeti, maya_deyeri, stok_miqdari, seki_data FROM mehsullar WHERE stok_miqdari > 0", conn)
    conn.close()
    
    if mehsullar_df.empty:
        if axtarilan_barkod:
            str_app.error("🚨 Bu barkodla məhsul tapılmadı və ya stoku bitib!")
        else:
            str_app.warning("⚠️ Satış etmək üçün anbarda mal yoxdur! Zəhmət olmasa əvvəlcə məhsul əlavə edin.")
    else:
        mehsullar_df['seçim_adı'] = mehsullar_df['ad'] + " (" + mehsullar_df['satis_qiymeti'].astype(str) + " ₼) - Stok: " + mehsullar_df['stok_miqdari'].astype(str)
        
        with str_app.form("satis_formu"):
            secilen_mehsul_ad = str_app.selectbox("Məhsulu Seçin", mehsullar_df['seçim_adı'].tolist())
            satilacaq_say = str_app.number_input("Satış Miqdarı", min_value=1, step=1)
            
            # Şəkli göstərmək üçün sahə
            mehsul_setir = mehsullar_df[mehsullar_df['seçim_adı'] == secilen_mehsul_ad].iloc[0]
            if mehsul_setir['seki_data'] is not None:
                str_app.image(mehsul_setir['seki_data'], caption=f"{mehsul_setir['ad']} Şəkli", width=200)
                
            satis_tesdiq = str_app.form_submit_button("💳 Satışı Tamamla")
            
            if satis_tesdiq:
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
                    cursor.execute("UPDATE mehsullar SET stok_miqdari = stok_miqdari - ? WHERE id = ?", (satilacaq_say, m_id))
                    indiki_vaxt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute('''
                        INSERT INTO satislar (mehsul_id, miqdar, satis_qiymeti, maya_qiymeti, tarix)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (m_id, satilacaq_say, m_satis, m_maya, indiki_vaxt))
                    conn.commit()
                    conn.close()
                    
                    str_app.success(f"✔️ {satilacaq_say} ədəd '{m_ad}' uğurla satıldı! Ümumi Məbləğ: {satilacaq_say * m_satis:.2f} ₼")
                    str_app.balloons()

# 2. MƏHSUL ƏLAVƏ ET (Şəkil yükləməli)
elif menyu == "✨ Məhsul Əlavə Et":
    str_app.subheader("✨ Yeni Məhsul Qeydiyyatı")
    
    with str_app.form("mehsul_formu", clear_on_submit=True):
        col1, col2 = str_app.columns(2)
        with col1:
            ad = str_app.text_input("Məhsulun Adı *")
            barkod = str_app.text_input("Barkod (Və ya Kod)")
            kategoriya = str_app.text_input("Kateqoriya")
            # ŞƏKİL YÜKLƏMƏ QUTUSU
            yuklenen_seki = str_app.file_uploader("🖼️ Məhsulun Şəklini Seçin (JPG, PNG)", type=["jpg", "jpeg", "png"])
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
                # Şəkli bayt formatına çeviririk ki, bazaya yazılsın
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
                    str_app.success(f"✔️ '{ad}' şəkli ilə birgə uğurla stoka əlavə edildi!")
                except Exception as e:
                    str_app.error(f"🚨 Xəta! Bu barkod nömrəsi artıq sistemdə var.")

# 3. MƏHSUL SİYAHISI (Şəkillərlə Göstərmək üçün xüsusi dizayn)
elif menyu == "📊 Məhsul Siyahısı və Stok":
    str_app.subheader("📊 Stokda Olan Mallar və Qalıq Sayı")
    
    conn = sqlite3.connect("anbar_sistemi.db")
    cursor = conn.cursor()
    cursor.execute("SELECT barkod, ad, kategoriya, maya_deyeri, satis_qiymeti, stok_miqdari, edv_li, seki_data FROM mehsullar")
    mallar = cursor.fetchall()
    conn.close()
    
    if not mallar:
        str_app.info("Anbarda hələ ki mal yoxdur. Sol menyudan məhsul əlavə edin.")
    else:
        # Cədvəl görüntüsü üçün
        data = []
        for mal in mallar:
            data.append({
                "Barkod": mal[0],
                "Məhsul Adı": mal[1],
                "Kateqoriya": mal[2],
                "Maya (₼)": mal[3],
                "Satış (₼)": mal[4],
                "Stok Sayı": mal[5],
                "ƏDV": mal[6]
            })
        df = pd.DataFrame(data)
        str_app.dataframe(df, use_container_width=True)
        
        # Vizual Şəkilli Kataloq Görüntüsü (Aşağıda kart kimi açılır)
        str_app.markdown("### 🖼️ Məhsulların Şəkilli Kataloqu")
        for mal in mallar:
            col_img, col_txt = str_app.columns([1, 4])
            with col_img:
                if mal[7] is not None:
                    str_app.image(mal[7], width=120)
                else:
                    str_app.write("🖼️ Şəkil yoxdur")
            with col_txt:
                str_app.markdown(f"**{mal[1]}** | Kateqoriya: {mal[2]} | **Stokda qalan: {mal[5]} ədəd**")
                str_app.markdown(f"Qiymət: {mal[4]} ₼")
                str_app.markdown("---")

# 4. SATIŞ HESABATI
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
