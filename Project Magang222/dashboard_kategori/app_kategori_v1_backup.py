"""
Dasbor Analisis Mobilisasi Kendaraan per Kategori (FG / MOL / PO Inventory / SPTA)
Jalankan dengan: streamlit run app_kategori.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Analisis Mobilisasi per Kategori", layout="wide", page_icon="🚚")

DATA_DIR = Path(__file__).parent / "data" / "processed"

# =======================================================================
# GAYA VISUAL
# =======================================================================
st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 1.9rem; font-weight: 700; color: #0f172a !important; }
[data-testid="stMetricLabel"] { font-size: 0.9rem; color: #4b5563 !important; white-space: normal !important; }
div[data-testid="stMetric"] {
    background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 10px;
    padding: 14px 16px 10px 16px;
}
.insight-box {
    background: #f0f9ff; border-left: 4px solid #0ea5e9; border-radius: 6px;
    padding: 10px 14px; margin: 6px 0 14px 0; font-size: 0.95rem; color: #0c4a6e;
}
.meaning-box {
    background: #f0fdf4; border-left: 4px solid #22c55e; border-radius: 6px;
    padding: 10px 14px; margin: 6px 0 14px 0; font-size: 0.95rem; color: #14532d;
}
.caveat-box {
    background: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 6px;
    padding: 10px 14px; margin: 6px 0 14px 0; font-size: 0.9rem; color: #78350f;
}
</style>
""", unsafe_allow_html=True)

def insight(text):
    st.markdown(f'<div class="insight-box">🔎 <b>Apa yang dapat dilihat?</b><br>{text}</div>', unsafe_allow_html=True)

def meaning(text):
    st.markdown(f'<div class="meaning-box">💡 <b>Apa artinya?</b><br>{text}</div>', unsafe_allow_html=True)

def caveat(text):
    st.markdown(f'<div class="caveat-box">⚠️ <b>Batasan</b><br>{text}</div>', unsafe_allow_html=True)

# =======================================================================
# KAMUS KATEGORI & LOKASI
# =======================================================================
KATEGORI_INFO = {
    "FG": {"label": "FG — Finish Good", "deskripsi": "Pengiriman gula jadi keluar pabrik", "warna": "#0ea5e9"},
    "MOL": {"label": "MOL — Molase", "deskripsi": "Pengiriman molase (tetes tebu) keluar pabrik", "warna": "#8b5cf6"},
    "PO INVENTORY": {"label": "PO Inventory", "deskripsi": "Pergerakan barang inventori pabrik", "warna": "#f59e0b"},
    "SPTA": {"label": "SPTA — Tebu Masuk", "deskripsi": "Tebu masuk dari kebun/pemasok ke pabrik", "warna": "#22c55e"},
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

txn_all, step_all = load_data()

def get_kategori_data(kode_flow_value):
    """Ambil data transaksi & step utk 1 kategori kode_flow, plus statistik dasar."""
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

# =======================================================================
# SIDEBAR
# =======================================================================
st.sidebar.title("🚚 Pilih Tampilan")
pilihan_view = st.sidebar.radio(
    "Tampilkan",
    ["📊 Perbandingan Semua Kategori"] + [f"{KATEGORI_INFO[k]['label']}" for k in KATEGORI_INFO],
)
st.sidebar.markdown("---")
st.sidebar.caption(
    "ℹ️ Transaksi dengan status belum selesai (OPEN) dan waktu mobilisasi >24 jam (kemungkinan "
    "kesalahan sistem) dikecualikan dari seluruh statistik secara default."
)

# =======================================================================
# HALAMAN PERBANDINGAN
# =======================================================================
if pilihan_view == "📊 Perbandingan Semua Kategori":
    st.title("📊 Perbandingan Waktu Mobilisasi Antar Kategori")
    st.caption("FG (Finish Good) · MOL (Molase) · PO Inventory · SPTA (Tebu Masuk)")

    tabel = RINGKASAN_SEMUA[["label", "n_transaksi", "n_valid", "mean", "median", "minimum", "maksimum", "std", "se"]].copy()
    tabel.columns = ["Kategori", "Total Transaksi", "n (valid)", "Rata-rata (menit)", "Median (menit)",
                      "Tercepat (menit)", "Terlama (menit)", "Std Dev (menit)", "Standard Error (menit)"]
    for c in tabel.columns[3:]:
        tabel[c] = tabel[c].round(1)
    st.dataframe(tabel, width="stretch", hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            RINGKASAN_SEMUA, x="label", y="mean", error_y="se",
            color="label", color_discrete_map={KATEGORI_INFO[k]["label"]: KATEGORI_INFO[k]["warna"] for k in KATEGORI_INFO},
            labels={"mean": "Rata-rata Waktu Mobilisasi (menit)", "label": ""},
            title="Rata-rata Waktu Mobilisasi per Kategori (bar error = standard error)",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")
    with col2:
        box_data = []
        for k in KATEGORI_INFO:
            _, _, _, ct = get_kategori_data(k)
            box_data.append(pd.DataFrame({"kategori": KATEGORI_INFO[k]["label"], "menit": ct}))
        box_df = pd.concat(box_data, ignore_index=True)
        fig = px.box(
            box_df, x="kategori", y="menit", color="kategori",
            color_discrete_map={KATEGORI_INFO[k]["label"]: KATEGORI_INFO[k]["warna"] for k in KATEGORI_INFO},
            labels={"menit": "Waktu Mobilisasi (menit)", "kategori": ""},
            title="Distribusi Waktu Mobilisasi per Kategori",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

    tercepat_row = RINGKASAN_SEMUA.loc[RINGKASAN_SEMUA["mean"].idxmin()]
    terlama_row = RINGKASAN_SEMUA.loc[RINGKASAN_SEMUA["mean"].idxmax()]
    paling_konsisten = RINGKASAN_SEMUA.loc[RINGKASAN_SEMUA["cv"].idxmin()]
    paling_variatif = RINGKASAN_SEMUA.loc[RINGKASAN_SEMUA["cv"].idxmax()]

    insight(
        f"**{tercepat_row['label']}** memiliki rata-rata waktu mobilisasi tercepat "
        f"({fmt_jam(tercepat_row['mean'])}, n={fmt_id(tercepat_row['n_valid'])}). "
        f"**{terlama_row['label']}** memiliki rata-rata paling lama "
        f"({fmt_jam(terlama_row['mean'])}, n={fmt_id(terlama_row['n_valid'])})."
    )
    meaning(
        f"**{paling_konsisten['label']}** paling konsisten waktunya (variasi {paling_konsisten['cv']:.0f}% dari rata-rata), "
        f"sedangkan **{paling_variatif['label']}** paling tidak konsisten (variasi {paling_variatif['cv']:.0f}%). "
        f"Kategori yang tidak konsisten lebih sulit diprediksi durasinya walau rata-ratanya terlihat wajar."
    )
    caveat(
        "Jumlah sampel (n) sangat berbeda antar kategori — SPTA punya ribuan transaksi sementara MOL/FG/PO Inventory "
        "hanya puluhan hingga ratusan. **Semakin kecil n, semakin lebar 'Standard Error'-nya** (lihat tabel), artinya "
        "rata-rata kategori dengan n kecil jauh lebih tidak pasti dan bisa berubah signifikan dengan data baru. "
        "Jangan membandingkan kategori kecil dan besar dengan tingkat percaya diri yang sama."
    )

# =======================================================================
# HALAMAN PER KATEGORI
# =======================================================================
else:
    kode_flow_terpilih = [k for k, v in KATEGORI_INFO.items() if v["label"] == pilihan_view][0]
    info = KATEGORI_INFO[kode_flow_terpilih]
    df, sf, valid, ct = get_kategori_data(kode_flow_terpilih)

    st.title(f"{'📦' if kode_flow_terpilih=='FG' else '🧪' if kode_flow_terpilih=='MOL' else '📋' if kode_flow_terpilih=='PO INVENTORY' else '🌾'} Analisis Mobilisasi — {info['label']}")
    st.caption(info["deskripsi"])

    # --- RINGKASAN ---
    st.markdown("### 📝 Ringkasan")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Jumlah Transaksi", fmt_id(len(df)))
    c2.metric("Jumlah Kendaraan", fmt_id(df["no_mobil"].nunique()))
    c3.metric("Rata-rata Waktu", fmt_jam(ct.mean()) if len(ct) else "-")
    c4.metric("Median Waktu", fmt_jam(ct.median()) if len(ct) else "-")
    c5.metric("Tercepat", fmt_jam(ct.min()) if len(ct) else "-")
    c6.metric("Terlama", fmt_jam(ct.max()) if len(ct) else "-")

    n_open = (df["status_trans"] == "OPEN").sum()
    st.caption(
        f"Dihitung dari {len(ct)} dari {len(df)} transaksi (status selesai, bukan outlier ekstrem). "
        f"{n_open} transaksi masih berstatus OPEN (belum selesai) saat data diambil."
    )

    if len(ct) > 1:
        se = ct.std() / np.sqrt(len(ct))
        insight(
            f"Waktu mobilisasi {info['label']} bervariasi dari {fmt_jam(ct.min())} sampai {fmt_jam(ct.max())}. "
            f"Rata-rata {fmt_jam(ct.mean())} (median {fmt_jam(ct.median())})."
        )
        if len(ct) < 200:
            caveat(
                f"Sampel kategori ini relatif kecil (n={len(ct)}), margin ketidakpastian rata-rata "
                f"±{1.96*se:.1f} menit (95% confidence). Hasil bisa berubah cukup besar dengan tambahan data baru."
            )

    st.markdown("---")

    # --- ALUR PROSES (dinamis dari flow_signature) ---
    st.markdown("### 🗺️ Alur Proses Mobilisasi")
    if len(df) and df["flow_signature"].notna().any():
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
            insight(f"Seluruh {fmt_id(len(df))} transaksi {info['label']} melewati jalur yang **sama persis** — tidak ada variasi jalur pada kategori ini.")
        else:
            insight(f"Kategori ini punya {n_signature_unik} variasi jalur berbeda. Jalur di atas adalah yang paling umum.")
    else:
        st.info("Data jalur tidak tersedia untuk kategori ini.")

    st.markdown("---")

    # --- DISTRIBUSI WAKTU ---
    st.markdown("### 📊 Distribusi Waktu Mobilisasi")
    if len(ct) >= 2:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(ct, nbins=min(30, max(5, len(ct)//3)), labels={"value": "Waktu Mobilisasi (menit)"},
                                title=f"Sebaran Waktu Mobilisasi {info['label']}", color_discrete_sequence=[info["warna"]])
            fig.update_layout(showlegend=False, yaxis_title="Jumlah Transaksi")
            st.plotly_chart(fig, width="stretch")
        with col2:
            fig = px.box(ct, labels={"value": "Waktu Mobilisasi (menit)"}, title=f"Boxplot Waktu Mobilisasi {info['label']}",
                         points="outliers", color_discrete_sequence=[info["warna"]])
            st.plotly_chart(fig, width="stretch")

        insight(
            f"Sebagian besar transaksi selesai dalam rentang {fmt_jam(ct.quantile(0.25))} sampai "
            f"{fmt_jam(ct.quantile(0.75))} (50% data tengah)."
        )
        if ct.mean() > ct.median() * 1.15:
            meaning("Distribusi miring ke kanan (long-tail) — rata-rata ditarik ke atas oleh sejumlah transaksi yang jauh lebih lama dari kebanyakan.")
    else:
        st.info("Data tidak cukup untuk membuat grafik distribusi (minimal 2 transaksi valid).")

    st.markdown("---")

    # --- WAKTU PER TAHAPAN ---
    st.markdown("### ⏱️ Waktu Rata-rata per Tahapan")
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
        st.plotly_chart(fig, width="stretch")

        top_var = step_stats.loc[step_stats["std_dev"].idxmax()]
        top_avg = step_stats.loc[step_stats["rata_rata"].idxmax()]
        insight(
            f"**{top_avg['tahapan']}** memiliki rata-rata waktu tertinggi ({top_avg['rata_rata']:.1f} menit). "
            f"**{top_var['tahapan']}** memiliki variasi waktu paling besar (std dev {top_var['std_dev']:.1f} menit)."
        )
        caveat(
            "Ini adalah tahapan dengan durasi/variasi tertinggi, bukan bukti penyebab keterlambatan. "
            "Perlu divalidasi dengan kondisi operasional aktual di lapangan."
        )

        with st.expander("Lihat tabel statistik lengkap per tahapan"):
            tampil = step_stats[["tahapan", "step_type", "jumlah", "rata_rata", "median", "minimum", "maksimum", "std_dev"]]
            tampil.columns = ["Tahapan", "Jenis", "Jumlah Data", "Rata-rata", "Median", "Minimum", "Maksimum", "Std Dev"]
            st.dataframe(tampil, width="stretch", hide_index=True)
    else:
        st.info("Data tahapan tidak tersedia untuk kategori ini.")

    st.markdown("---")

    # --- TRANSAKSI TERCEPAT & TERLAMA ---
    st.markdown("### 🏁 Transaksi Tercepat & Terlama")
    if len(ct):
        col1, col2 = st.columns(2)
        tercepat = valid.loc[ct.idxmin()]
        terlama = valid.loc[ct.idxmax()]
        with col1:
            st.success(f"**Tercepat: {fmt_jam(tercepat['cycle_time_minutes_for_stats'])}**")
            st.write(f"Transaksi: `{tercepat['trans_no']}`  \nKendaraan: `{tercepat['no_mobil']}`  \nTanggal: {tercepat['date']}")
        with col2:
            st.error(f"**Terlama: {fmt_jam(terlama['cycle_time_minutes_for_stats'])}**")
            st.write(f"Transaksi: `{terlama['trans_no']}`  \nKendaraan: `{terlama['no_mobil']}`  \nTanggal: {terlama['date']}")
            st.caption("Perlu validasi operasional — apakah ini kejadian nyata atau ada kesalahan pencatatan waktu.")
    else:
        st.info("Tidak ada transaksi valid untuk ditampilkan.")

    st.markdown("---")
    st.caption(
        f"Analisis berdasarkan {len(df)} transaksi kategori {info['label']} "
        f"({len(ct)} di antaranya valid untuk statistik waktu mobilisasi)."
    )
