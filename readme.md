# 🤖 AI Chatbot Bubble Style dengan Analisis Data Indonesia

Proyek ini adalah aplikasi **chatbot interaktif berbasis Streamlit** yang memungkinkan pengguna untuk:
- **Berkomunikasi** dengan AI menggunakan model pilihan (via OpenRouter),
- **Mengajukan pertanyaan berbasis data** terkait penduduk Indonesia,
- **Mendapatkan visualisasi data**, resume, serta query Pandas yang dihasilkan secara otomatis,
- **Beralih antara percakapan bebas (chitchat)** dan **analisis berbasis data** secara otomatis.

---

## 📦 Fitur Utama

✅ **Multi-Model AI**:  
Pilih model LLM dari beberapa opsi seperti DeepSeek, LLaMA 3.3, atau Qwen3.

✅ **Analisis Data Otomatis**:  
Bot akan memahami maksud pertanyaan dan jika relevan, menjalankan query Pandas terhadap dataset CSV.

✅ **Visualisasi Dinamis**:  
Hasil query divisualisasikan secara otomatis (bar chart, pie, dsb).

✅ **Resume Cerdas**:  
AI akan memberikan rangkuman dari data hasil query.

✅ **Chitchat Mode**:  
Jika pertanyaan bukan soal data, AI akan menjawab dengan percakapan biasa.

---

## 🗂️ Struktur Proyek
```
├── assets/
│ └── data_penduduk_indonesia.csv # Dataset CSV penduduk Indonesia
├── openrouter_client.py # Client Python untuk OpenRouter API
├── main.py # Aplikasi Streamlit utama
└── README.md # Dokumentasi ini
```

---

## 🚀 Cara Menjalankan

1. **Klon repo ini atau salin semua file yang dibutuhkan.**
2. Install dependensi:
```bash
pip install -r requirements.txt
```
3. Jalankan aplikasi:
```
streamlit run main.py
```
🔧 Konfigurasi Model
Pilih model dari sidebar:
- DeepSeek Chat V3 (Free)
- LLaMA 3.3 8B Instruct (Free)
- Qwen3 235B A22B (Free)
Model ini akan digunakan untuk semua percakapan dan pemrosesan pertanyaan.

📊 Alur Kerja Aplikasi
User menginput pertanyaan di chat
AI mengklasifikasi apakah itu chitchat atau data-driven question
Jika data-driven:
AI membuat query Pandas → dieksekusi → divisualisasikan
AI menyusun resume dan menampilkan hasil
Jika chitchat:
AI memberikan jawaban biasa

📁 Dataset
File CSV:
```assets/data_penduduk_indonesia.csv```
Pastikan file CSV tersedia sebelum menjalankan aplikasi.
