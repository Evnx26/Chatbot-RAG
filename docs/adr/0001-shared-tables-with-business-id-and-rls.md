# Semua Business berbagi tabel yang sama, dipisah dengan business_id + Row-Level Security

Platform ini multi-tenant: banyak Business memakai satu database. Kami memilih satu set tabel bersama dengan kolom `business_id` di setiap tabel milik Business (termasuk tabel embedding pgvector), lalu memasang Postgres Row-Level Security sebagai pengaman kedua. Alasannya: cukup satu migrasi, vector search tinggal difilter per Business, dan kebocoran data antar Business tetap tertahan di level database walaupun ada query aplikasi yang lupa filter.

## Considered Options

- **Schema Postgres per Business**: isolasinya lebih kuat, tapi migrasi harus dijalankan di setiap schema dan index pgvector jadi tersebar. Terlalu berat untuk skala UMKM.
- **Database per Business**: ditolak karena biaya dan operasionalnya tidak sebanding.
