"""
Dasbor Analisis Mobilisasi Kendaraan per Kategori (FG / MOL / PO Inventory / SPTA)

"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import base64

st.set_page_config(page_title="Analisis Mobilisasi Kendaraan PT.SMS", layout="wide", page_icon="🚚")
px.defaults.template = "plotly_white"

DATA_DIR = Path(__file__).parent / "data" / "processed"
ASSETS_DIR = Path(__file__).parent / "assets"

# =======================================================================
# GAMBAR LATAR (FOTO PABRIK)
# =======================================================================
@st.cache_data
def load_bg_image_b64():
    bg_path = ASSETS_DIR / "factory_bg.jpg"
    if bg_path.exists():
        return base64.b64encode(bg_path.read_bytes()).decode()
    return None

BG_B64 = load_bg_image_b64()
BG_URL = f'data:image/jpeg;base64,{BG_B64}' if BG_B64 else None

# =======================================================================
# GAYA VISUAL (CSS)
# =======================================================================
bg_app_css = ""
if BG_URL:
    bg_app_css = f"""
    [data-testid="stAppViewContainer"] {{
        background-image: linear-gradient(rgba(255,255,255,0.58), rgba(241,245,249,0.68)), url("{BG_URL}");
        background-size: cover;
        background-position: center top;
        background-attachment: fixed;
    }}
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
    """

_header_bg_image_part = f', url("{BG_URL}")' if BG_URL else ""
main_header_css = (
    ".main-header {"
    f"background: linear-gradient(135deg, rgba(3,105,161,0.85) 0%, rgba(14,165,233,0.78) 60%, rgba(56,189,248,0.7) 100%){_header_bg_image_part};"
    "background-size: cover; background-position: center 42%;"
    "padding: 30px 32px; border-radius: 18px; color: white; margin-bottom: 22px;"
    "box-shadow: 0 8px 24px rgba(3,105,161,0.25);"
    "}"
    ".main-header h1 { margin: 0; font-size: 1.7rem; font-weight: 800; text-shadow: 0 2px 6px rgba(0,0,0,0.35); }"
    ".main-header p { margin: 6px 0 0 0; opacity: 0.95; font-size: 0.98rem; text-shadow: 0 1px 4px rgba(0,0,0,0.3); }"
)

st.markdown("""
<style>
""" + bg_app_css + main_header_css + """

.stat-card {
    background: white; border-radius: 14px; padding: 16px 18px 12px 18px;
    box-shadow: 0 1px 4px rgba(15,23,42,0.08); border-left: 5px solid #0ea5e9;
    transition: transform .15s ease, box-shadow .15s ease; height: 100%;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(15,23,42,0.14); }
.stat-card .label { font-size: 0.82rem; color: #64748b; font-weight: 600; margin-bottom: 6px; }
.stat-card .value { font-size: 1.55rem; font-weight: 800; color: #0f172a; line-height: 1.1; }
.stat-card .sub { font-size: 0.76rem; color: #94a3b8; margin-top: 4px; }

.insight-box {
    background: #f0f9ff; border-left: 4px solid #0ea5e9; border-radius: 10px;
    padding: 12px 16px; margin: 8px 0 14px 0; font-size: 0.95rem; color: #0c4a6e;
}
.meaning-box {
    background: #f0fdf4; border-left: 4px solid #22c55e; border-radius: 10px;
    padding: 12px 16px; margin: 8px 0 14px 0; font-size: 0.95rem; color: #14532d;
}
.caveat-box {
    background: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 10px;
    padding: 12px 16px; margin: 8px 0 14px 0; font-size: 0.9rem; color: #78350f;
}
div[data-testid="stSidebar"] { background: #0f172a; }
div[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
div[data-testid="stSidebar"] .stRadio label { padding: 4px 2px; }
hr { margin: 8px 0 18px 0 !important; }

/* Halo putih di belakang teks yang mengambang langsung di atas foto, supaya tetap
   terbaca jelas tanpa perlu kotak solid (biar fotonya tetap kelihatan). */
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] * {
    text-shadow: 0 0 6px rgba(255,255,255,0.95), 0 0 12px rgba(255,255,255,0.85);
}
/* kecualikan teks di dalam kartu/box yang sudah punya background solid sendiri,
   supaya halo-nya tidak menumpuk aneh di situ */
.stat-card *, .insight-box, .meaning-box, .caveat-box, .main-header * {
    text-shadow: none !important;
}
.main-header h1, .main-header p {
    text-shadow: 0 2px 6px rgba(0,0,0,0.35) !important;
}
</style>
""", unsafe_allow_html=True)

def insight(text):
    st.markdown(f'<div class="insight-box"> <b>Apa yang dapat dilihat?</b><br>{text}</div>', unsafe_allow_html=True)

def meaning(text):
    st.markdown(f'<div class="meaning-box"> <b>Apa artinya?</b><br>{text}</div>', unsafe_allow_html=True)

def caveat(text):
    st.markdown(f'<div class="caveat-box"> <b>Batasan</b><br>{text}</div>', unsafe_allow_html=True)

def stat_card(label, value, sub="", color="#0ea5e9"):
    st.markdown(f"""
    <div class="stat-card" style="border-left-color:{color}">
        <div class="label">{label}</div>
        <div class="value">{value}</div>
        <div class="sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

# =======================================================================
# KAMUS KATEGORI & LOKASI
# =======================================================================
KATEGORI_INFO = {
    "FG": {"label": "FG — Finish Good", "ikon": "📦", "deskripsi": "Pengiriman gula jadi keluar pabrik", "warna": "#0ea5e9"},
    "MOL": {"label": "MOL — Molase", "ikon": "🧪", "deskripsi": "Pengiriman molase (tetes tebu) keluar pabrik", "warna": "#8b5cf6"},
    "PO INVENTORY": {"label": "PO Inventory", "ikon": "📋", "deskripsi": "Pergerakan barang inventori pabrik", "warna": "#f59e0b"},
    "SPTA": {"label": "SPTA — Tebu Masuk", "ikon": "🌾", "deskripsi": "Tebu masuk dari kebun/pemasok ke pabrik", "warna": "#22c55e"},
}
LOKASI_LABEL = {
    "POS2IN": "Pos Masuk (Tebu)", "POS2OUT": "Pos Keluar (Tebu)", "WB3": "Timbangan (WB3)",
    "POS1IN": "Pos Masuk (Gula/Molase)", "POS1OUT": "Pos Keluar (Gula/Molase)", "WB": "Timbangan (WB)",
    "QACHECK": "Cek Kualitas (QA)", "LOADING": "Muat Barang", "SEGEL": "Penyegelan",
}
def label_lokasi(k): return LOKASI_LABEL.get(k, k)

def label_step(s):
    if s.startswith("Aktivitas: "):
        if s == "Aktivitas: WB3":
            return "Menunggu di Timbangan (WB3)"
        return f"Proses {label_lokasi(s.replace('Aktivitas: ', ''))} Berlangsung"
    if s == "WB3 -> WB3":
        return "Menunggu di Timbangan (WB3)"
    return " → ".join(label_lokasi(p) for p in s.split(" -> "))

def fmt_id(n, d=0):
    if pd.isna(n): return "-"
    if d == 0: return f"{n:,.0f}".replace(",", ".")
    s = f"{n:,.{d}f}"; a, _, b = s.partition("."); return a.replace(",", ".") + "," + b

def fmt_jam(m):
    if pd.isna(m): return "-"
    j, mm = divmod(int(round(m)), 60)
    return f"{j} jam {mm} menit" if j > 0 else f"{mm} menit"

# =======================================================================
# MEMUAT DATA
# =======================================================================
@st.cache_data
def load_data():
    txn = pd.read_csv(DATA_DIR / "flow_transaction_level.csv", parse_dates=["first_time", "last_time", "tgl_trans"])
    txn["date"] = pd.to_datetime(txn["date"]).dt.date
    step = pd.read_csv(DATA_DIR / "flow_step_duration_long.csv", parse_dates=["from_time", "to_time"])
    return txn, step

txn_raw, step_raw = load_data()
MIN_DATE, MAX_DATE = txn_raw["date"].min(), txn_raw["date"].max()

# =======================================================================
# SIDEBAR — BRANDING, FILTER PERIODE, NAVIGASI
# =======================================================================
st.sidebar.markdown("## Mobilisasi Kendaraan PT.SMS")
st.sidebar.caption("Analisis waktu proses Kendaraan")
st.sidebar.markdown("---")

periode_pilihan = st.sidebar.radio("📅 Periode", ["7 Hari Terakhir", "30 Hari Terakhir", "Semua Data", "Pilih Tanggal Sendiri"], index=2)
if periode_pilihan == "7 Hari Terakhir":
    start_d = max(MIN_DATE, MAX_DATE - pd.Timedelta(days=6)); end_d = MAX_DATE
elif periode_pilihan == "30 Hari Terakhir":
    start_d = max(MIN_DATE, MAX_DATE - pd.Timedelta(days=29)); end_d = MAX_DATE
elif periode_pilihan == "Semua Data":
    start_d, end_d = MIN_DATE, MAX_DATE
else:
    dr = st.sidebar.date_input("Rentang tanggal", value=(MIN_DATE, MAX_DATE), min_value=MIN_DATE, max_value=MAX_DATE)
    start_d, end_d = (dr[0], dr[1]) if len(dr) == 2 else (MIN_DATE, MAX_DATE)

txn_all = txn_raw[(txn_raw["date"] >= start_d) & (txn_raw["date"] <= end_d)].copy()
step_all = step_raw[step_raw["trans_no"].isin(txn_all["trans_no"])].copy()

st.sidebar.markdown("---")
pilihan_view = st.sidebar.radio(
    "📍 Tampilkan",
    ["📊 Perbandingan Semua Kategori"] + [f"{KATEGORI_INFO[k]['ikon']} {KATEGORI_INFO[k]['label']}" for k in KATEGORI_INFO],
)
st.sidebar.markdown("---")
st.sidebar.caption(
    "ℹ️ Transaksi belum selesai (OPEN) dan waktu mobilisasi >24 jam (kemungkinan kesalahan "
    "sistem) dikecualikan dari seluruh statistik secara default."
)

# =======================================================================
# FUNGSI BANTU DATA PER KATEGORI
# =======================================================================
def get_kategori_data(kode_flow_value):
    df = txn_all[txn_all["kode_flow"] == kode_flow_value].copy()
    sf = step_all[step_all["trans_no"].isin(df["trans_no"])].copy()
    valid = df[~df["excluded_from_cycle_time"] & ~df["is_cycle_time_outlier_24h"]]
    ct = valid["cycle_time_minutes_for_stats"].dropna()
    return df, sf, valid, ct

def hitung_ringkasan(kode_flow_value):
    df, sf, valid, ct = get_kategori_data(kode_flow_value)
    if len(ct) == 0:
        return dict(kategori=kode_flow_value, n_transaksi=len(df), n_valid=0, mean=np.nan, median=np.nan,
                    minimum=np.nan, maksimum=np.nan, std=np.nan, se=np.nan, cv=np.nan)
    se = ct.std() / np.sqrt(len(ct)) if len(ct) > 1 else np.nan
    cv = ct.std() / ct.mean() * 100 if ct.mean() else np.nan
    return dict(kategori=kode_flow_value, n_transaksi=len(df), n_valid=len(ct), mean=ct.mean(), median=ct.median(),
                minimum=ct.min(), maksimum=ct.max(), std=ct.std(), se=se, cv=cv)

RINGKASAN_SEMUA = pd.DataFrame([hitung_ringkasan(k) for k in KATEGORI_INFO.keys()])
RINGKASAN_SEMUA["label"] = RINGKASAN_SEMUA["kategori"].map(lambda k: KATEGORI_INFO[k]["label"])
OVERALL_MEAN = RINGKASAN_SEMUA["mean"].mean()

# =======================================================================
# HALAMAN PERBANDINGAN
# =======================================================================
if pilihan_view == "📊 Perbandingan Semua Kategori":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Analisis Waktu Mobilisasi Kendaraan PT.SMS</h1>
        <p>FG (Finish Good) · MOL (Molase) · PO Inventory · SPTA (Tebu Masuk)</p>
    </div>
    """, unsafe_allow_html=True)

    ada_data = RINGKASAN_SEMUA["n_valid"].sum() > 0
    if not ada_data:
        st.warning("Tidak ada data pada periode yang dipilih. Coba perluas rentang tanggal di sidebar.")
    else:
        cols = st.columns(4)
        for i, k in enumerate(KATEGORI_INFO.keys()):
            row = RINGKASAN_SEMUA[RINGKASAN_SEMUA["kategori"] == k].iloc[0]
            with cols[i]:
                stat_card(
                    f"{KATEGORI_INFO[k]['ikon']} {KATEGORI_INFO[k]['label']}",
                    fmt_jam(row["mean"]) if pd.notna(row["mean"]) else "Tidak ada data",
                    f"n = {fmt_id(row['n_valid'])} transaksi",
                    KATEGORI_INFO[k]["warna"],
                )

        st.markdown("<br>", unsafe_allow_html=True)

        tabel = RINGKASAN_SEMUA[["label", "n_transaksi", "n_valid", "mean", "median", "minimum", "maksimum", "std", "se"]].copy()
        tabel.columns = ["Kategori", "Total Transaksi", "n (valid)", "Rata-rata (menit)", "Median (menit)",
                          "Tercepat (menit)", "Terlama (menit)", "Std Dev (menit)", "Standard Error (menit)"]
        for c in tabel.columns[3:]:
            tabel[c] = tabel[c].round(1)
        with st.expander("Lihat tabel lengkap", expanded=False):
            st.dataframe(tabel, width="stretch", hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                RINGKASAN_SEMUA, x="label", y="mean", error_y="se",
                color="label", color_discrete_map={KATEGORI_INFO[k]["label"]: KATEGORI_INFO[k]["warna"] for k in KATEGORI_INFO},
                labels={"mean": "Rata-rata Waktu Mobilisasi (menit)", "label": ""},
                title="Rata-rata Waktu Mobilisasi per Kategori",
            )
            fig.update_layout(showlegend=False, title_font_size=14)
            st.plotly_chart(fig, width="stretch")
        with col2:
            box_data = []
            for k in KATEGORI_INFO:
                _, _, _, ct = get_kategori_data(k)
                if len(ct):
                    box_data.append(pd.DataFrame({"kategori": KATEGORI_INFO[k]["label"], "menit": ct}))
            if box_data:
                box_df = pd.concat(box_data, ignore_index=True)
                fig = px.box(
                    box_df, x="kategori", y="menit", color="kategori",
                    color_discrete_map={KATEGORI_INFO[k]["label"]: KATEGORI_INFO[k]["warna"] for k in KATEGORI_INFO},
                    labels={"menit": "Waktu Mobilisasi (menit)", "kategori": ""},
                    title="Distribusi Waktu Mobilisasi per Kategori",
                )
                fig.update_layout(showlegend=False, title_font_size=14)
                st.plotly_chart(fig, width="stretch")

        # --- RADAR CHART: profil relatif tiap kategori ---
        st.markdown("### 🕸️ Profil Relatif Setiap Kategori")
        valid_rows = RINGKASAN_SEMUA.dropna(subset=["mean"])
        if len(valid_rows) >= 2:
            max_mean = valid_rows["mean"].max()
            max_n = valid_rows["n_valid"].max()
            radar_fig = go.Figure()
            for _, row in valid_rows.iterrows():
                kecepatan = 100 * (1 - row["mean"] / max_mean) if max_mean else 0
                konsistensi = max(0, 100 - min(row["cv"], 100)) if pd.notna(row["cv"]) else 0
                kepercayaan_data = 100 * np.log1p(row["n_valid"]) / np.log1p(max_n) if max_n else 0
                radar_fig.add_trace(go.Scatterpolar(
                    r=[kecepatan, konsistensi, kepercayaan_data, kecepatan],
                    theta=["Kecepatan", "Konsistensi", "Kepercayaan Data (n)", "Kecepatan"],
                    fill="toself", name=row["label"],
                    line_color=KATEGORI_INFO[row["kategori"]]["warna"],
                ))
            radar_fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False)),
                showlegend=True, height=430, margin=dict(t=20, b=20),
            )
            st.plotly_chart(radar_fig, width="stretch")
            st.caption(
                "Kecepatan = semakin jauh ke luar, semakin cepat rata-ratanya dibanding kategori lain. "
                "Konsistensi = semakin jauh ke luar, semakin stabil/tidak berubah-ubah waktunya. "
                "Kepercayaan Data = semakin jauh ke luar, semakin banyak sampel data yang mendukung angkanya "
                "(skala logaritmik, karena SPTA punya ribuan transaksi vs MOL puluhan)."
            )
        else:
            st.info("Data tidak cukup untuk membuat profil perbandingan pada periode ini.")

        tercepat_row = valid_rows.loc[valid_rows["mean"].idxmin()] if len(valid_rows) else None
        terlama_row = valid_rows.loc[valid_rows["mean"].idxmax()] if len(valid_rows) else None
        if tercepat_row is not None:
            insight(
                f"{tercepat_row['label']} memiliki rata-rata waktu mobilisasi tercepat "
                f"({fmt_jam(tercepat_row['mean'])}, n={fmt_id(tercepat_row['n_valid'])}). "
                f"{terlama_row['label']} memiliki rata-rata paling lama "
                f"({fmt_jam(terlama_row['mean'])}, n={fmt_id(terlama_row['n_valid'])})."
            )
            paling_konsisten = valid_rows.loc[valid_rows["cv"].idxmin()]
            paling_variatif = valid_rows.loc[valid_rows["cv"].idxmax()]
            meaning(
                f"{paling_konsisten['label']} paling konsisten waktunya (variasi {paling_konsisten['cv']:.0f}% dari rata-rata), "
                f"sedangkan {paling_variatif['label']} paling tidak konsisten (variasi {paling_variatif['cv']:.0f}%)."
            )
        caveat(
            "Jumlah sampel (n) sangat berbeda antar kategori. Semakin kecil n, semakin lebar Standard Error-nya, "
            "artinya rata-rata kategori dengan n kecil jauh lebih tidak pasti. Jangan membandingkan kategori kecil "
            "dan besar dengan tingkat percaya diri yang sama."
        )

# =======================================================================
# HALAMAN PER KATEGORI
# =======================================================================
else:
    kode_flow_terpilih = [k for k, v in KATEGORI_INFO.items() if f"{v['ikon']} {v['label']}" == pilihan_view][0]
    info = KATEGORI_INFO[kode_flow_terpilih]
    df, sf, valid, ct = get_kategori_data(kode_flow_terpilih)

    kategori_bg_style = (
        f"background: linear-gradient(135deg, {info['warna']}d9 0%, {info['warna']}b3 100%), url('{BG_URL}'); "
        f"background-size: cover; background-position: center 42%;"
        if BG_URL else
        f"background: linear-gradient(135deg, {info['warna']}cc 0%, {info['warna']} 100%);"
    )
    st.markdown(f"""
    <div class="main-header" style="{kategori_bg_style}">
        <h1>{info['ikon']} Analisis Mobilisasi — {info['label']}</h1>
        <p>{info['deskripsi']}</p>
    </div>
    """, unsafe_allow_html=True)

    if len(df) == 0:
        st.warning("Tidak ada data kategori ini pada periode yang dipilih. Coba perluas rentang tanggal di sidebar.")
        st.stop()

    # --- KARTU RINGKASAN ---
    n_open = (df["status_trans"] == "OPEN").sum()
    cols = st.columns(6)
    with cols[0]: stat_card("Jumlah Transaksi", fmt_id(len(df)), color=info["warna"])
    with cols[1]: stat_card("Jumlah Kendaraan", fmt_id(df["no_mobil"].nunique()), color=info["warna"])
    with cols[2]: stat_card("Rata-rata Waktu", fmt_jam(ct.mean()) if len(ct) else "-", color=info["warna"])
    with cols[3]: stat_card("Median Waktu", fmt_jam(ct.median()) if len(ct) else "-", color=info["warna"])
    with cols[4]: stat_card("Tercepat", fmt_jam(ct.min()) if len(ct) else "-", color=info["warna"])
    with cols[5]: stat_card("Terlama", fmt_jam(ct.max()) if len(ct) else "-", color=info["warna"])

    st.caption(
        f"Dihitung dari {len(ct)} dari {len(df)} transaksi (status selesai, bukan outlier ekstrem). "
        f"{n_open} transaksi masih berstatus OPEN (belum selesai)."
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # --- GAUGE: posisi relatif thd rata2 semua kategori ---
    if len(ct) and pd.notna(OVERALL_MEAN) and OVERALL_MEAN > 0:
        col_gauge, col_text = st.columns([1, 1.4])
        with col_gauge:
            rasio = ct.mean() / OVERALL_MEAN
            gauge_max = max(2 * OVERALL_MEAN, ct.mean() * 1.2)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=ct.mean(),
                number={"suffix": " menit", "font": {"size": 26}},
                title={"text": "Rata-rata vs Semua Kategori", "font": {"size": 13}},
                gauge={
                    "axis": {"range": [0, gauge_max]},
                    "bar": {"color": info["warna"]},
                    "steps": [
                        {"range": [0, OVERALL_MEAN * 0.85], "color": "#dcfce7"},
                        {"range": [OVERALL_MEAN * 0.85, OVERALL_MEAN * 1.15], "color": "#fef9c3"},
                        {"range": [OVERALL_MEAN * 1.15, gauge_max], "color": "#fee2e2"},
                    ],
                    "threshold": {"line": {"color": "#0f172a", "width": 3}, "thickness": 0.8, "value": OVERALL_MEAN},
                },
            ))
            fig.update_layout(height=260, margin=dict(t=40, b=10, l=20, r=20))
            st.plotly_chart(fig, width="stretch")
        with col_text:
            st.markdown("<br>", unsafe_allow_html=True)
            if rasio < 0.85:
                meaning(f"Kategori ini {(1-rasio)*100:.0f}% lebih cepat dari rata-rata seluruh kategori (garis hitam di gauge = rata-rata keseluruhan).")
            elif rasio > 1.15:
                meaning(f"Kategori ini {(rasio-1)*100:.0f}% lebih lama dari rata-rata seluruh kategori (garis hitam di gauge = rata-rata keseluruhan).")
            else:
                meaning("Kategori ini waktunya mendekati rata-rata seluruh kategori (mendekati garis hitam di gauge).")

    if len(ct) > 1 and len(ct) < 200:
        se = ct.std() / np.sqrt(len(ct))
        caveat(f"Sampel kategori ini relatif kecil (n={len(ct)}), margin ketidakpastian rata-rata ±{1.96*se:.1f} menit (95% confidence).")

    st.markdown("---")

    # --- ALUR PROSES ---
    st.markdown("### Alur Proses Mobilisasi")
    if df["flow_signature"].notna().any():
        signature = df["flow_signature"].mode().iloc[0]
        urutan_kode = signature.split(" -> ") if " -> " in signature else signature.split("->")
        urutan = [label_lokasi(u) for u in urutan_kode]
        fig = go.Figure(go.Funnel(
            y=[f"{i+1}. {u}" for i, u in enumerate(urutan)],
            x=[len(df)] * len(urutan),
            textinfo="label",
            marker={"color": info["warna"]},
        ))
        fig.update_layout(height=max(300, 60 * len(urutan)), margin=dict(t=10, b=10), showlegend=False)
        st.plotly_chart(fig, width="stretch")
        n_signature_unik = df["flow_signature"].nunique()
        if n_signature_unik == 1:
            insight(f"Seluruh {fmt_id(len(df))} transaksi {info['label']} melewati jalur yang sama persis.")
        else:
            insight(f"Kategori ini punya {n_signature_unik} variasi jalur berbeda. Jalur di atas adalah yang paling umum.")

    st.markdown("---")

    # --- DISTRIBUSI WAKTU ---
    st.markdown("### Distribusi Waktu Mobilisasi")
    if len(ct) >= 2:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(ct, nbins=min(30, max(5, len(ct)//3)), labels={"value": "Waktu Mobilisasi (menit)"},
                                title="Sebaran Waktu Mobilisasi", color_discrete_sequence=[info["warna"]])
            fig.update_layout(showlegend=False, yaxis_title="Jumlah Transaksi", title_font_size=14)
            st.plotly_chart(fig, width="stretch")
        with col2:
            fig = px.box(ct, labels={"value": "Waktu Mobilisasi (menit)"}, title="Boxplot Waktu Mobilisasi",
                         points="outliers", color_discrete_sequence=[info["warna"]])
            fig.update_layout(title_font_size=14)
            st.plotly_chart(fig, width="stretch")

        insight(f"Sebagian besar transaksi selesai dalam rentang {fmt_jam(ct.quantile(0.25))} sampai {fmt_jam(ct.quantile(0.75))} (50% data tengah).")
        if ct.mean() > ct.median() * 1.15:
            meaning("Distribusi miring ke kanan (long-tail) rata-rata ditarik ke atas oleh sejumlah transaksi yang jauh lebih lama dari kebanyakan.")
    else:
        st.info("Data tidak cukup untuk membuat grafik distribusi (minimal 2 transaksi valid).")

    st.markdown("---")

    # --- WAKTU PER TAHAPAN ---
    st.markdown("### Waktu Rata-rata per Tahapan")
    if len(sf):
        step_stats = sf.groupby(["step_label", "step_type"])["duration_minutes"].agg(
            jumlah="count", rata_rata="mean", median="median", minimum="min", maksimum="max", std_dev="std"
        ).reset_index().round(1)
        step_stats["tahapan"] = step_stats["step_label"].apply(label_step)
        step_stats = step_stats.sort_values("rata_rata", ascending=True)

        fig = px.bar(
            step_stats, x="rata_rata", y="tahapan", orientation="h", color="step_type",
            color_discrete_map={"TRANSIT": "#94a3b8", "AKTIVITAS": info["warna"]},
            labels={"rata_rata": "Rata-rata Waktu (menit)", "tahapan": "", "step_type": "Jenis"},
            title="Rata-rata Durasi per Tahapan (TRANSIT = berpindah/menunggu, AKTIVITAS = proses berlangsung)",
        )
        fig.update_layout(title_font_size=13)
        st.plotly_chart(fig, width="stretch")

        top_var = step_stats.loc[step_stats["std_dev"].idxmax()]
        top_avg = step_stats.loc[step_stats["rata_rata"].idxmax()]
        insight(
            f"{top_avg['tahapan']} memiliki rata-rata waktu tertinggi ({top_avg['rata_rata']:.1f} menit). "
            f"{top_var['tahapan']} memiliki variasi waktu paling besar (std dev {top_var['std_dev']:.1f} menit)."
        )
        caveat("Ini adalah tahapan dengan durasi/variasi tertinggi, bukan bukti penyebab keterlambatan. Perlu divalidasi dengan kondisi operasional aktual di lapangan.")

        with st.expander("📋 Lihat tabel statistik lengkap per tahapan"):
            tampil = step_stats[["tahapan", "step_type", "jumlah", "rata_rata", "median", "minimum", "maksimum", "std_dev"]]
            tampil.columns = ["Tahapan", "Jenis", "Jumlah Data", "Rata-rata", "Median", "Minimum", "Maksimum", "Std Dev"]
            st.dataframe(tampil, width="stretch", hide_index=True)
    else:
        st.info("Data tahapan tidak tersedia untuk kategori ini.")

    st.markdown("---")

    # --- TRANSAKSI TERCEPAT & TERLAMA ---
    st.markdown("### Transaksi Tercepat & Terlama")
    if len(ct):
        col1, col2 = st.columns(2)
        tercepat = valid.loc[ct.idxmin()]
        terlama = valid.loc[ct.idxmax()]
        with col1:
            st.success(f"Tercepat: {fmt_jam(tercepat['cycle_time_minutes_for_stats'])}")
            st.write(f"Transaksi: `{tercepat['trans_no']}`  \nKendaraan: `{tercepat['no_mobil']}`  \nTanggal: {tercepat['date']}")
        with col2:
            st.error(f"Terlama: {fmt_jam(terlama['cycle_time_minutes_for_stats'])}")
            st.write(f"Transaksi: `{terlama['trans_no']}`  \nKendaraan: `{terlama['no_mobil']}`  \nTanggal: {terlama['date']}")
            st.caption("Perlu validasi operasional.")
    else:
        st.info("Tidak ada transaksi valid untuk ditampilkan.")

    st.markdown("---")
    st.caption(f"Analisis berdasarkan {len(df)} transaksi kategori {info['label']} ({len(ct)} valid untuk statistik waktu).")
