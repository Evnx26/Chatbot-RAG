# Katalog Product disimpan di tabel SQL, bukan di vector store

Product disimpan sebagai tabel terstruktur (kategori, harga, stok). Chatbot mengaksesnya lewat tool. Hanya Knowledge (FAQ, kebijakan, panduan) yang di-embed ke pgvector. Alasannya: minat Prospect/Lead harus terhubung ke Product yang nyata supaya dashboard bisa menghitung "siapa tertarik ke produk apa". Selain itu, harga dan stok harus selalu akurat, padahal hasil retrieval dari teks bisa basi.
