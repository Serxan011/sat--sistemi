import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from streamlit_option_menu import option_menu

# =========================
# QOVLUQLAR
# =========================

if not os.path.exists("sekiller"):
    os.makedirs("sekiller")

# =========================
# DATABASE
# =========================

conn = sqlite3.connect("magaza.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS mehsullar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ad TEXT,
    kateqoriya TEXT,
    barkod TEXT,
    alis REAL,
    satis REAL,
    edv INTEGER,
    stok INTEGER,
    sekil TEXT,
    tarix TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS satislar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mehsul TEXT,
    qiymet REAL,
    say INTEGER,
    tarix TEXT
)
""")

conn.commit()

# =========================
# DIZAYN
# =========================

st.set_page_config(
    page_title="NN SMART KASSA",
    page_icon="🛒",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background-color: #0f172a;
    color: white;
}

.stButton>button {
    background: linear-gradient(90deg,#2563eb,#7c3aed);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 10px;
    font-weight: bold;
}

div[data-baseweb="input"] {
    border-radius: 12px;
}

.css-1d391kg {
    background-color: #111827;
}

h1,h2,h3 {
    color: white;
}

.card {
    background:#1e293b;
    padding:15px;
    border-radius:15px;
    margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================

with st.sidebar:
    secim = option_menu(
        "NN SMART KASSA",
        ["Məhsul Əlavə", "Kassa", "Hesabat"],
        icons=["box", "cart", "bar-chart"],
        menu_icon="shop",
        default_index=0
    )

# =========================
# MƏHSUL ƏLAVƏ
# =========================

if secim == "Məhsul Əlavə":

    st.title("📦 Yeni Məhsul")

    col1, col2 = st.columns(2)

    with col1:
        ad = st.text_input("Məhsul adı")
        kateqoriya = st.text_input("Kateqoriya")
        barkod = st.text_input("Barkod")

        alis = st.number_input("Alış qiyməti", 0.0)
        satis = st.number_input("Satış qiyməti", 0.0)

    with col2:
        edv = st.selectbox("ƏDV", [0, 18])
        stok = st.number_input("Stok sayı", 0)

        sekil = st.file_uploader(
            "Şəkil əlavə et",
            type=["png", "jpg", "jpeg"]
        )

    maya = alis + (alis * edv / 100)

    st.info(f"ƏDV daxil maya dəyəri: {maya:.2f} AZN")

    if st.button("Bazaya əlavə et"):

        sekil_yolu = ""

        if sekil:
            sekil_yolu = f"sekiller/{sekil.name}"

            with open(sekil_yolu, "wb") as f:
                f.write(sekil.getbuffer())

        c.execute("""
        INSERT INTO mehsullar
        (ad,kateqoriya,barkod,alis,satis,edv,stok,sekil,tarix)
        VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            ad,
            kateqoriya,
            barkod,
            alis,
            satis,
            edv,
            stok,
            sekil_yolu,
            datetime.now().strftime("%d-%m-%Y %H:%M")
        ))

        conn.commit()

        st.success("Məhsul əlavə edildi!")

# =========================
# KASSA
# =========================

elif secim == "Kassa":

    st.title("🛒 Kassa")

    df = pd.read_sql("SELECT * FROM mehsullar", conn)

    axtar = st.text_input("🔍 Məhsul axtar")

    if axtar:
        df = df[df["ad"].str.contains(axtar, case=False)]

    if "sebet" not in st.session_state:
        st.session_state.sebet = []

    for _, row in df.iterrows():

        col1, col2, col3 = st.columns([1,3,1])

        with col1:
            if row["sekil"] and os.path.exists(row["sekil"]):
                st.image(row["sekil"], width=100)

        with col2:
            st.markdown(f"""
            <div class="card">
            <h3>{row['ad']}</h3>
            <p>Kateqoriya: {row['kateqoriya']}</p>
            <p>Qiymət: {row['satis']} AZN</p>
            <p>Stok: {row['stok']}</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            if st.button("Səbətə at", key=row["id"]):
                st.session_state.sebet.append(row)

    st.divider()

    st.subheader("🧺 Səbət")

    toplam = 0

    for item in st.session_state.sebet:
        st.write(f"{item['ad']} - {item['satis']} AZN")
        toplam += item["satis"]

    st.success(f"Ümumi məbləğ: {toplam:.2f} AZN")

    if st.button("Satışı tamamla"):

        for item in st.session_state.sebet:

            c.execute("""
            INSERT INTO satislar
            (mehsul,qiymet,say,tarix)
            VALUES (?,?,?,?)
            """, (
                item["ad"],
                item["satis"],
                1,
                datetime.now().strftime("%d-%m-%Y %H:%M")
            ))

            c.execute("""
            UPDATE mehsullar
            SET stok = stok - 1
            WHERE id = ?
            """, (item["id"],))

        conn.commit()

        st.session_state.sebet = []

        st.success("Satış tamamlandı!")

# =========================
# HESABAT
# =========================

elif secim == "Hesabat":

    st.title("📊 Hesabat")

    satis_df = pd.read_sql("SELECT * FROM satislar", conn)

    st.dataframe(satis_df)

    umumi = satis_df["qiymet"].sum()

    st.metric("Ümumi Dövriyyə", f"{umumi:.2f} AZN")

    gunluk = satis_df[
        satis_df["tarix"].str.contains(
            datetime.now().strftime("%d-%m-%Y")
        )
    ]

    st.metric(
        "Bugünkü satış",
        f"{gunluk['qiymet'].sum():.2f} AZN"
    )

    ayliq = satis_df[
        satis_df["tarix"].str.contains(
            datetime.now().strftime("%m-%Y")
        )
    ]

    st.metric(
        "Aylıq satış",
        f"{ayliq['qiymet'].sum():.2f} AZN"
    )
