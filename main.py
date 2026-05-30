import streamlit as st
import sqlite3#
from supabase import create_client
url = "SƏNİN_SUPABASE_URL-İN"
key = "SƏNİN_SUPABASE_ANON_KEY-İN"
supabase = create_client(url, key)
import pandas as pd
from datetime import datetime
import os

# =========================================
# CONFIG
# =========================================

st.set_page_config(
    page_title="NN MARKET ULTRA PRO",
    page_icon="🛒",
    layout="wide"
)

# =========================================
# STYLE
# =========================================

st.markdown("""
<style>

html, body, [class*="css"] {
    background: #0b1120;
    color: white;
    font-family: sans-serif;
}

section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #1e293b;
}

.stButton>button {
    width: 100%;
    height: 50px;
    border-radius: 14px;
    border: none;
    background: linear-gradient(
        90deg,
        #2563eb,
        #7c3aed
    );
    color: white;
    font-size: 15px;
    font-weight: bold;
}

.stButton>button:hover {
    transform: scale(1.02);
}

.stTextInput input,
.stNumberInput input,
.stSelectbox div {
    border-radius: 12px;
}

.kart {
    background: #1e293b;
    padding: 18px;
    border-radius: 18px;
    margin-bottom: 15px;
    box-shadow: 0 0 20px rgba(0,0,0,0.3);
}

.stat {
    background: linear-gradient(
        135deg,
        #2563eb,
        #7c3aed
    );
    padding: 20px;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 15px;
}

img {
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# FOLDER
# =========================================

if not os.path.exists("sekiller"):
    os.makedirs("sekiller")

# =========================================
# DATABASE
# =========================================

conn = sqlite3.connect(
    "market.db",
    check_same_thread=False
)

c = conn.cursor()

# =========================================
# TABLES
# =========================================

c.execute("""
CREATE TABLE IF NOT EXISTS kateqoriyalar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ad TEXT UNIQUE
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS magazalar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ad TEXT UNIQUE
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS mehsullar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ad TEXT,
    kateqoriya TEXT,
    magaza TEXT,
    barkod TEXT UNIQUE,
    alis REAL,
    satis REAL,
    edv REAL,
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

# =========================================
# SIDEBAR
# =========================================

st.sidebar.title("🛒 NN MARKET")

menu = st.sidebar.radio(
    "Menyu",
    [
        "📦 Məhsul",
        "🛒 Kassa",
        "🏬 Anbar",
        "📊 Hesabat"
    ]
)

# =========================================
# PRODUCT
# =========================================

if menu == "📦 Məhsul":

    st.title("📦 Məhsul Əlavə")

    # ===============================
    # QUICK CATEGORY + STORE
    # ===============================

    colkat1, colkat2 = st.columns([5,1])

    with colkat1:

        kat_df = pd.read_sql(
            "SELECT * FROM kateqoriyalar",
            conn
        )

        kateqoriyalar = (
            kat_df["ad"].tolist()
            if not kat_df.empty
            else []
        )

        kateqoriya = st.selectbox(
            "Kateqoriya",
            kateqoriyalar
        )

    with colkat2:

        st.write("")

        if st.button("+ Kateqoriya"):

            st.session_state.kat_open = True

    if st.session_state.get("kat_open"):

        yeni_kat = st.text_input(
            "Yeni kateqoriya"
        )

        if st.button("Yadda saxla"):

            try:

                c.execute("""
                INSERT INTO kateqoriyalar (
                    ad
                )
                VALUES (?)
                """, (yeni_kat,))

                conn.commit()

                st.success(
                    "Kateqoriya əlavə edildi"
                )

            except:

                st.error(
                    "Kateqoriya artıq var"
                )

    # ===============================
    # STORE
    # ===============================

    colmag1, colmag2 = st.columns([5,1])

    with colmag1:

        mag_df = pd.read_sql(
            "SELECT * FROM magazalar",
            conn
        )

        magazalar = (
            mag_df["ad"].tolist()
            if not mag_df.empty
            else []
        )

        magaza = st.selectbox(
            "Təchizatçı / Mağaza",
            magazalar
        )

    with colmag2:

        st.write("")

        if st.button("+ Mağaza"):

            st.session_state.mag_open = True

    if st.session_state.get("mag_open"):

        yeni_mag = st.text_input(
            "Yeni mağaza"
        )

        if st.button("Mağazanı yadda saxla"):

            try:

                c.execute("""
                INSERT INTO magazalar (
                    ad
                )
                VALUES (?)
                """, (yeni_mag,))

                conn.commit()

                st.success(
                    "Mağaza əlavə edildi"
                )

            except:

                st.error(
                    "Mağaza artıq var"
                )

    # ===============================
    # PRODUCT FORM
    # ===============================

    col1, col2 = st.columns(2)

    with col1:

        ad = st.text_input(
            "Məhsul adı"
        )

        barkod = st.text_input(
            "Barkod"
        )

        alis = st.number_input(
            "Alış qiyməti",
            min_value=0.0
        )

        edv = st.selectbox(
            "ƏDV faizi",
            [0, 18]
        )

    with col2:

        satis = st.number_input(
            "Satış qiyməti",
            min_value=0.0
        )

        stok = st.number_input(
            "Stok",
            min_value=1
        )

        sekil = st.file_uploader(
            "Şəkil",
            type=["png","jpg","jpeg"]
        )

    # =================================
    # ƏDV HESABI
    # =================================

    if edv == 18:

        edv_miqdar = alis * 18 / 100

        st.info(
            f"ƏDV məbləği: {edv_miqdar:.2f} AZN"
        )

    else:

        st.info(
            "Bu məhsul ƏDV-sizdir"
        )

    # =================================
    # SAVE PRODUCT
    # =================================

    if st.button("Məhsulu əlavə et"):

        if barkod == "":

            st.error(
                "Barkod boş ola bilməz"
            )

        else:

            yoxla = pd.read_sql(
                f"""
                SELECT * FROM mehsullar
                WHERE barkod='{barkod}'
                """,
                conn
            )

            if not yoxla.empty:

                st.error(
                    "Bu barkod artıq mövcuddur"
                )

            else:

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
                    magaza,
                    barkod,
                    alis,
                    satis,
                    edv,
                    stok,
                    sekil,
                    tarix
                )
                VALUES (?,?,?,?,?,?,?,?,?,?)
                """, (
                    ad,
                    kateqoriya,
                    magaza,
                    barkod,
                    alis,
                    satis,
                    edv,
                    stok,
                    sekil_yolu,
                    datetime.now().strftime(
                        "%d-%m-%Y %H:%M"
                    )
                ))

                conn.commit()

                st.success(
                    "Məhsul əlavə edildi"
                )

# =========================================
# CASHIER
# =========================================

elif menu == "🛒 Kassa":

    st.title("🛒 Kassa")

    df = pd.read_sql(
        "SELECT * FROM mehsullar",
        conn
    )

    if "sebet" not in st.session_state:
        st.session_state.sebet = []

    # =================================
    # FAST BARCODE
    # =================================

    barkod = st.text_input(
        "📷 Barkod oxut"
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

        else:

            st.error(
                "Barkod tapılmadı"
            )

    # =================================
    # FAST SEARCH
    # =================================

    axtar = st.text_input(
        "⚡ Sürətli axtarış"
    )

    if axtar:

        df = df[
            df["ad"].str.contains(
                axtar,
                case=False
            )
        ]

    # =================================
    # PRODUCTS
    # =================================

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
            <div class="kart">
            <h3>{row['ad']}</h3>
            <p>Kateqoriya: {row['kateqoriya']}</p>
            <p>Mağaza: {row['magaza']}</p>
            <p>Barkod: {row['barkod']}</p>
            <p>Qiymət: {row['satis']} AZN</p>
            <p>Stok: {row['stok']}</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:

            say = st.number_input(
                "Say",
                min_value=1,
                value=1,
                key=f"say_{row['id']}"
            )

            if st.button(
                "Əlavə et",
                key=row["id"]
            ):

                if row["stok"] < say:

                    st.error(
                        "Stok çatmır"
                    )

                else:

                    item = {
                        "id": row["id"],
                        "ad": row["ad"],
                        "qiymet": row["satis"],
                        "say": say
                    }

                    st.session_state.sebet.append(
                        item
                    )

    # =================================
    # CART
    # =================================

    st.divider()

    st.subheader("🧺 Səbət")

    toplam = 0

    for item in st.session_state.sebet:

        cem = (
            item["qiymet"]
            *
            item["say"]
        )

        toplam += cem

        st.markdown(f"""
        <div class="kart">
        <h3>{item['ad']}</h3>
        <p>{item['say']} ədəd</p>
        <p>{cem:.2f} AZN</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat">
    <h2>Ümumi Məbləğ</h2>
    <h1>{toplam:.2f} AZN</h1>
    </div>
    """, unsafe_allow_html=True)

    # =================================
    # COMPLETE SALE
    # =================================

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
            "Satış tamamlandı"
        )

# =========================================
# WAREHOUSE
# =========================================

elif menu == "🏬 Anbar":

    st.title("🏬 Anbar")

    df = pd.read_sql(
        "SELECT * FROM mehsullar",
        conn
    )

    axtar = st.text_input(
        "⚡ Məhsul axtar"
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
        padding:18px;
        border-radius:18px;
        margin-bottom:15px;
        border-left:8px solid {reng};
        ">
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1,3])

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
                    width=120
                )

        with col2:

            st.markdown(f"""
            <h3>{row['ad']}</h3>
            <p>Kateqoriya: {row['kateqoriya']}</p>
            <p>Mağaza: {row['magaza']}</p>
            <p>Barkod: {row['barkod']}</p>
            <p>ƏDV: %{row['edv']}</p>
            <p>Stok: {row['stok']}</p>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# =========================================
# REPORT
# =========================================

elif menu == "📊 Hesabat":

    st.title("📊 Hesabat")

    satis_df = pd.read_sql(
        "SELECT * FROM satislar",
        conn
    )

    umumi = (
        satis_df["qiymet"]
        *
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
        gunluk["qiymet"]
        *
        gunluk["say"]
    ).sum()

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(f"""
        <div class="stat">
        <h2>Ümumi Dövriyyə</h2>
        <h1>{umumi:.2f} AZN</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="stat">
        <h2>Bugünkü Satış</h2>
        <h1>{gunluk_total:.2f} AZN</h1>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.dataframe(
        satis_df,
        use_container_width=True
    )
