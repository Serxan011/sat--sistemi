import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="NN SMART POS",
    page_icon="🛒",
    layout="wide"
)

# =========================
# STYLE
# =========================

st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #0f172a;
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

.stButton>button {
    width: 100%;
    height: 48px;
    border-radius: 14px;
    border: none;
    background: linear-gradient(90deg,#2563eb,#7c3aed);
    color: white;
    font-size: 16px;
    font-weight: bold;
}

.stTextInput input {
    border-radius: 12px;
}

.card {
    background: #1e293b;
    padding: 15px;
    border-radius: 16px;
    margin-bottom: 15px;
}

.statcard {
    background: linear-gradient(135deg,#2563eb,#7c3aed);
    padding: 20px;
    border-radius: 18px;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# =========================
# FOLDER
# =========================

if not os.path.exists("sekiller"):
    os.makedirs("sekiller")

# =========================
# DATABASE
# =========================

conn = sqlite3.connect(
    "database.db",
    check_same_thread=False
)

c = conn.cursor()

# =========================
# TABLES
# =========================

c.execute("""
CREATE TABLE IF NOT EXISTS mehsullar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ad TEXT,
    kateqoriya TEXT,
    barkod TEXT,
    alis REAL,
    satis REAL,
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
# SIDEBAR
# =========================

st.sidebar.title("🛒 NN SMART POS")

menu = st.sidebar.radio(
    "Menyu",
    [
        "📦 Məhsul Əlavə",
        "🛒 Kassa",
        "🏬 Anbar",
        "📊 Hesabat"
    ]
)

# =========================
# PRODUCT ADD
# =========================

if menu == "📦 Məhsul Əlavə":

    st.title("📦 Məhsul Əlavə")

    col1, col2 = st.columns(2)

    with col1:

        ad = st.text_input("Məhsul adı")

        kateqoriya = st.text_input(
            "Kateqoriya"
        )

        barkod = st.text_input(
            "Barkod"
        )

        alis = st.number_input(
            "Alış qiyməti",
            min_value=0.0
        )

    with col2:

        satis = st.number_input(
            "Satış qiyməti",
            min_value=0.0
        )

        stok = st.number_input(
            "Stok",
            min_value=0
        )

        sekil = st.file_uploader(
            "Şəkil",
            type=["png","jpg","jpeg"]
        )

    if st.button("Məhsulu əlavə et"):

        sekil_yolu = ""

        if sekil:

            sekil_yolu = (
                f"sekiller/{sekil.name}"
            )

            with open(
                sekil_yolu,
                "wb"
            ) as f:

                f.write(
                    sekil.getbuffer()
                )

        c.execute("""
        INSERT INTO mehsullar (
            ad,
            kateqoriya,
            barkod,
            alis,
            satis,
            stok,
            sekil,
            tarix
        )
        VALUES (?,?,?,?,?,?,?,?)
        """, (
            ad,
            kateqoriya,
            barkod,
            alis,
            satis,
            stok,
            sekil_yolu,
            datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            )
        ))

        conn.commit()

        st.success(
            "Məhsul əlavə edildi!"
        )

# =========================
# CASHIER
# =========================

elif menu == "🛒 Kassa":

    st.title("🛒 Kassa")

    df = pd.read_sql(
        "SELECT * FROM mehsullar",
        conn
    )

    if "sebet" not in st.session_state:
        st.session_state.sebet = []

    barkod = st.text_input(
        "📷 Barkod ilə satış"
    )

    if barkod:

        barkod_df = df[
            df["barkod"] == barkod
        ]

        if not barkod_df.empty:

            row = barkod_df.iloc[0]

            item = {
                "id": row["id"],
                "ad": row["ad"],
                "qiymet": row["satis"],
                "say": 1
            }

            st.session_state.sebet.append(
                item
            )

            st.success(
                f"{row['ad']} əlavə edildi"
            )

    axtar = st.text_input(
        "🔍 Məhsul axtar"
    )

    if axtar:

        df = df[
            df["ad"].str.contains(
                axtar,
                case=False
            )
        ]

    for _, row in df.iterrows():

        col1, col2, col3 = st.columns(
            [1,3,1]
        )

        with col1:

            if (
                row["sekil"]
                and
                os.path.exists(
                    row["sekil"]
                )
            ):

                st.image(
                    row["sekil"],
                    width=100
                )

        with col2:

            st.markdown(f"""
            <div class="card">
            <h3>{row['ad']}</h3>
            <p>Kateqoriya:
            {row['kateqoriya']}</p>
            <p>Barkod:
            {row['barkod']}</p>
            <p>Qiymət:
            {row['satis']} AZN</p>
            <p>Stok:
            {row['stok']}</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:

            say = st.number_input(
                f"Say {row['id']}",
                min_value=1,
                value=1,
                key=f"say_{row['id']}"
            )

            if st.button(
                "Səbətə at",
                key=row["id"]
            ):

                item = {
                    "id": row["id"],
                    "ad": row["ad"],
                    "qiymet": row["satis"],
                    "say": say
                }

                st.session_state.sebet.append(
                    item
                )

    st.divider()

    st.subheader("🧺 Səbət")

    toplam = 0

    for item in st.session_state.sebet:

        cem = (
            item["qiymet"]
            *
            item["say"]
        )

        st.markdown(f"""
        <div class="card">
        {item['ad']}
        <br>
        {item['say']} ədəd
        <br>
        {cem:.2f} AZN
        </div>
        """, unsafe_allow_html=True)

        toplam += cem

    st.markdown(f"""
    <div class="statcard">
    <h2>Ümumi</h2>
    <h1>{toplam:.2f} AZN</h1>
    </div>
    """, unsafe_allow_html=True)

    if st.button("💰 Satışı tamamla"):

        for item in st.session_state.sebet:

            c.execute("""
            INSERT INTO satislar (
                mehsul,
                qiymet,
                say,
                tarix
            )
            VALUES (?,?,?,?)
            """, (
                item["ad"],
                item["qiymet"],
                item["say"],
                datetime.now().strftime(
                    "%d-%m-%Y %H:%M"
                )
            ))

            c.execute("""
            UPDATE mehsullar
            SET stok = stok - ?
            WHERE id = ?
            """, (
                item["say"],
                item["id"]
            ))

        conn.commit()

        st.session_state.sebet = []

        st.success(
            "Satış tamamlandı!"
        )

# =========================
# WAREHOUSE
# =========================

elif menu == "🏬 Anbar":

    st.title("🏬 Anbar")

    df = pd.read_sql(
        "SELECT * FROM mehsullar",
        conn
    )

    axtar = st.text_input(
        "🔍 Məhsul axtar"
    )

    if axtar:

        df = df[
            df["ad"].str.contains(
                axtar,
                case=False
            )
        ]

    for _, row in df.iterrows():

        reng = "#22c55e"

        if row["stok"] <= 5:
            reng = "#ef4444"

        st.markdown(f"""
        <div style="
        background:#1e293b;
        padding:20px;
        border-radius:18px;
        margin-bottom:15px;
        border-left:8px solid {reng};
        ">
        <h3>{row['ad']}</h3>
        <p>Kateqoriya:
        {row['kateqoriya']}</p>
        <p>Barkod:
        {row['barkod']}</p>
        <p>Stok:
        {row['stok']}</p>
        </div>
        """, unsafe_allow_html=True)

# =========================
# REPORTS
# =========================

elif menu == "📊 Hesabat":

    st.title("📊 Hesabat")

    satis_df = pd.read_sql(
        "SELECT * FROM satislar",
        conn
    )

    umumi = (
        satis_df["qiymet"] *
        satis_df["say"]
    ).sum()

    bugun = datetime.now().strftime(
        "%d-%m-%Y"
    )

    gunluk = satis_df[
        satis_df["tarix"].str.contains(
            bugun
        )
    ]

    gunluk_total = (
        gunluk["qiymet"] *
        gunluk["say"]
    ).sum()

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(f"""
        <div class="statcard">
        <h2>Ümumi Dövriyyə</h2>
        <h1>{umumi:.2f} AZN</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="statcard">
        <h2>Bugünkü Satış</h2>
        <h1>{gunluk_total:.2f} AZN</h1>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.dataframe(
        satis_df,
        use_container_width=True
    )
