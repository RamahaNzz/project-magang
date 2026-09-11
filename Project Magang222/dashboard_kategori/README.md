# Analisis Mobilisasi Kendaraan per Kategori (kode_flow)

Dashboard gabungan untuk 4 kategori: FG, MOL, PO Inventory, SPTA — plus halaman perbandingan.

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

## Background Foto Pabrik (Terbaru)

Latar belakang dashboard sekarang memakai foto udara pabrik (`assets/factory_bg.jpg`):
- Halaman utama: foto diterapkan dengan overlay putih transparan supaya kartu, tabel, dan grafik tetap mudah dibaca.
- Banner header di setiap halaman: foto lebih terlihat, dipadukan gradasi warna kategori + bayangan teks
  supaya judul putih tetap kontras.

Foto asli (1,28 MB) sudah dikompres jadi JPEG (~100 KB) supaya dashboard tetap ringan dimuat.
Kalau ingin ganti foto lain, tinggal timpa file `assets/factory_bg.jpg` dengan nama file yang sama.

## Versi Visual Profesional

`app_kategori.py` sudah dirombak jadi lebih interaktif & profesional dibanding versi sebelumnya
(`app_kategori_v1_backup.py`, disimpan sebagai cadangan):

- **Header banner** bergradasi warna sesuai kategori
- **Kartu statistik custom** dengan efek hover, bukan `st.metric` polos
- **Filter Periode** di sidebar (7 hari/30 hari/semua/pilih sendiri) — berlaku ke seluruh dashboard
- **Gauge chart** di tiap halaman kategori — langsung menunjukkan apakah kategori itu lebih cepat/lambat dari rata-rata seluruh kategori
- **Radar chart** di halaman Perbandingan — profil "Kecepatan vs Konsistensi vs Kepercayaan Data" tiap kategori dalam satu visual
- Skema warna konsisten per kategori di semua grafik

Semua kotak "Apa yang dapat dilihat / Apa artinya / Batasan" dari versi sebelumnya tetap
dipertahankan — perombakan ini murni visual & interaktivitas, bukan mengubah isi analisis.


| Kategori | Transaksi | Kendaraan Unik |
|---|---:|---:|
| SPTA | 19.422 | 496 |
| PO Inventory | 821 | 29 |
| FG | 149 | 18 |
| MOL | 76 | 5 |

**Catatan penting:** ukuran sampel MOL (76) dan FG (149) jauh lebih kecil dari SPTA (19.422) —
statistik rata-rata/std dev untuk kategori kecil punya margin ketidakpastian jauh lebih besar.
Dashboard sudah menampilkan Standard Error di halaman Perbandingan untuk mengingatkan hal ini.
