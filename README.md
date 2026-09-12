# Analisis Mobilisasi Kendaraan per Kategori (kode_flow)

Analisi Mobilisasi untuk 4 kategori: FG, MOL, PO Inventory, SPTA dan halaman perbandingan.

## Cara Menjalankan

```bash
pip install -r requirements.txt
streamlit run app_kategori.py
```

Buka browser ke http://localhost:8501

## Struktur Folder

```
dashboard_kategori/
├── app_kategori.py         # aplikasi utama (gabungan 4 kategori + perbandingan)
├── requirements.txt
├── README.md
└── data/
    └── processed/
        ├── flow_transaction_level.csv
        ├── flow_step_duration_long.csv
        ├── flow_hourly_agg.csv
        └── data_quality_report.csv
```

## Isi Dashboard

Dipilih lewat sidebar:

1. **📊 Perbandingan Semua Kategori** — tabel & grafik bar/boxplot membandingkan rata-rata,
   median, min, max, std dev, dan standard error keempat kategori sekaligus. Otomatis
   menyebut kategori tercepat/terlama/paling konsisten, dengan catatan soal perbedaan ukuran
   sampel (n) antar kategori.

2. **FG / MOL / PO Inventory / SPTA** (halaman terpisah per kategori) — masing-masing berisi:
   - Ringkasan (jumlah transaksi, kendaraan, rata-rata/median/tercepat/terlama)
   - Alur Proses (funnel, jalur diambil otomatis dari data `flow_signature`)
   - Distribusi Waktu (histogram + boxplot)
   - Waktu per Tahapan (bar chart, dibedakan TRANSIT vs AKTIVITAS)
   - Transaksi Tercepat & Terlama (detail utk validasi lapangan)

## Kategori Dipisah Berdasarkan `kode_flow` Asli

Berbeda dari dashboard versi sebelumnya (`app.py`, yang mengelompokkan berdasarkan jalur fisik
`flow_type`), dashboard ini memfilter langsung dari kolom **`kode_flow`** asli — sehingga SPTA
dan PO Inventory ditampilkan sebagai kategori yang benar-benar terpisah, sesuai revisi kebutuhan
user (keduanya kebetulan memakai jalur fisik yang identik tapi punya arti bisnis berbeda: SPTA
= tebu masuk, PO Inventory = barang keluar gudang).


| Kategori | Transaksi | Kendaraan Unik |
|---|---:|---:|
| SPTA | 19.422 | 496 |
| PO Inventory | 821 | 29 |
| FG | 149 | 18 |
| MOL | 76 | 5 |

**Catatan penting:** ukuran sampel MOL (76) dan FG (149) jauh lebih kecil dari SPTA (19.422) —
statistik rata-rata/std dev untuk kategori kecil punya margin ketidakpastian jauh lebih besar.
Dashboard sudah menampilkan Standard Error di halaman Perbandingan untuk mengingatkan hal ini.
