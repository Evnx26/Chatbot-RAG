# Fase Pengerjaan

Setiap fase adalah vertical slice: BE, AI, dan FE untuk satu fitur, sehingga di akhir fase selalu ada sesuatu yang bisa didemokan. Fase selesai hanya kalau semua poin **Selesai kalau** terpenuhi dan test-nya hijau. Project ini hanya berjalan lokal lewat `docker-compose`, tanpa deploy.

Status: ⬜ belum · 🟨 sedang · ✅ selesai

## ✅ Fase 0 – Fondasi

- Monorepo `backend/`, `frontend/`, `widget/` dan `docker-compose` (Postgres + pgvector, FastAPI, Next.js).
- Skema dasar Business, Admin, dan Super Admin, migrasi Alembic, serta Row-Level Security per `business_id`.
- Signup dan login Admin (JWT di FastAPI). Signup otomatis membuat Business baru.
- Seed Super Admin dan Business "Toko Demo" lewat script.
- Halaman login dan signup dashboard (Next.js + Tailwind).

**Selesai kalau:**
- `docker-compose up` menjalankan semua service.
- Admin bisa signup, login, dan melihat halaman dashboard kosong.
- Ada test yang membuktikan Admin Business A tidak bisa membaca data Business B, baik lewat API maupun lewat query langsung dengan RLS aktif.

## ⬜ Fase 1 – Knowledge & RAG

- Upload Knowledge berformat PDF, TXT/MD, dan DOCX, lalu chunking dan embedding lewat NVIDIA (`NVIDIAEmbeddings`) ke pgvector.
- Halaman Knowledge di dashboard: upload, daftar, dan hapus.
- Graph LangGraph sederhana: retrieve Knowledge milik Business, lalu jawab. Kalau Knowledge tidak cukup, bot menjawab jujur dan mencatat Unanswered Question.
- Endpoint chat dengan streaming SSE dan penyimpanan Conversation.
- Set uji sekitar 30 pertanyaan untuk Toko Demo (termasuk pertanyaan jebakan) dan script eval.

**Selesai kalau:**
- Bot menjawab FAQ Toko Demo lewat API dengan benar dan tidak mengarang.
- Pertanyaan jebakan tercatat sebagai Unanswered Question.
- Skor eval tercatat di README.

## ⬜ Fase 2 – Katalog Product & Landing Page

- CRUD Product dan import CSV, plus halaman Product di dashboard.
- Landing page fashion Toko Demo (baju, celana, rok, aksesoris pria dan wanita) yang membaca katalog dari API.
- Tool katalog di graph supaya bot bisa mencari Product berdasarkan kategori, ukuran, warna, harga, dan stok.

**Selesai kalau:**
- Bot menjawab pertanyaan kayak "ada rok hitam ukuran M?" dengan data katalog yang akurat.
- Landing page menampilkan Product dari database.

## ⬜ Fase 3 – Widget

- `widget.js` (Preact + Tailwind, build Vite jadi satu file) yang dirender di Shadow DOM.
- Public widget key per Business dan pengecekan allowed domains di backend.
- Visitor ID anonim di localStorage, supaya Conversation tetap nyambung saat Visitor kembali.
- Product card di chat, berisi gambar, nama, harga, dan link.
- Pengaturan nama bot, sapaan pembuka, dan warna widget, plus snippet embed di dashboard.
- Rate limit pesan per Visitor.

**Selesai kalau:**
- Chat berjalan di landing page lewat `<script>` tag yang sama persis dengan yang akan dipakai UMKM lain.
- Request dari domain yang tidak terdaftar ditolak.
- Style widget tidak bocor ke halaman host, dan style halaman host tidak bocor ke widget.

## ⬜ Fase 4 – Kualifikasi Lead

- Node deteksi minat di graph: output terstruktur berisi Product yang diminati dan Interest Level (cold/warm/hot), berdasarkan sinyal yang ditulis di prompt.
- Prospect tercipta otomatis begitu minat terdeteksi.
- Tawaran kontak via WhatsApp/email muncul satu kali per Conversation ketika Interest Level mencapai warm atau hot. Visitor juga bisa memberi kontak kapan saja.
- Google Sign-In untuk Visitor Account (per Business), dan riwayat anonim digabung ke akun saat Visitor login.
- Prospect naik menjadi Lead begitu kontaknya diketahui.

**Selesai kalau:**
- Percakapan uji menghasilkan Prospect atau Lead dengan Product dan Interest Level yang benar.
- Visitor yang login tanpa menunjukkan minat tidak menjadi Lead.

## ⬜ Fase 5 – Dashboard Lead

- Daftar dan detail Lead: kontak, Product yang diminati, Interest Level, ringkasan percakapan dari LLM, transkrip, dan waktu terakhir aktif.
- Follow-up Status: baru → dihubungi → closing / batal.
- Analitik: funnel Visitor → Prospect → Lead dan Product yang paling banyak diminati.
- Daftar Unanswered Question.

**Selesai kalau:**
- Admin bisa mengelola sebuah Lead dari baru sampai closing.
- Angka analitik cocok dengan data di database.

## ⬜ Fase 6 – Super Admin & Kuota

- Dashboard Super Admin: daftar Business, suspend dan aktifkan, statistik pemakaian (chat, token, jumlah Lead).
- Kuota pesan harian per Business yang bisa diubah Super Admin.
- README lengkap, diagram arsitektur, dan video demo lokal.

**Selesai kalau:**
- Business yang di-suspend atau kehabisan kuota tidak bisa dipakai chat, dan widget menampilkan pesan yang sopan.
- Super Admin tidak punya jalur apa pun untuk membaca Conversation atau Lead (lihat ADR 0003).
