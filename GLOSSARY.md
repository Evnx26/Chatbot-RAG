# Chatbot RAG UMKM

Platform tempat banyak bisnis UMKM memasang chatbot di website mereka. Chatbot menjawab pertanyaan pengunjung dari knowledge bisnis tersebut dan menangkap siapa yang tertarik ke produk apa.

## Language

### Pihak

**Business**:
Satu UMKM yang terdaftar di platform. Knowledge, Product, Prospect, dan Lead miliknya terpisah dari Business lain.
_Avoid_: Tenant, toko, client, perusahaan

**Admin**:
Orang dari sebuah Business yang mengelola knowledge dan katalog, lalu melihat Lead di dashboard.
_Avoid_: User, owner, pemilik

**Super Admin**:
Pemilik platform yang mengelola semua Business.
_Avoid_: Root, superuser, platform admin

**Visitor**:
Orang yang membuka website sebuah Business dan mengobrol dengan chatbot. Bisa anonim, bisa juga login ke akun Visitor milik Business tersebut.
_Avoid_: User, customer, pelanggan, pengunjung

**Visitor Account**:
Akun login Visitor yang hanya berlaku di satu Business.
_Avoid_: Member, customer account, profil

### Minat

**Prospect**:
Visitor anonim yang sudah menunjukkan minat ke satu atau lebih Product, tapi belum memberi kontak.
_Avoid_: Calon lead, anonymous lead

**Lead**:
Prospect yang sudah memberi kontak (nama dan WhatsApp/email) sehingga bisa di-follow-up oleh Admin.
_Avoid_: Customer, pelanggan, kontak

**Interest Level**:
Seberapa kuat minat Prospect atau Lead untuk membeli: cold, warm, atau hot.
_Avoid_: Score, lead score, temperature

**Follow-up Status**:
Tahap penanganan sebuah Lead oleh Admin: baru, dihubungi, closing, atau batal.
_Avoid_: Pipeline stage, lead status

### Percakapan

**Conversation**:
Rangkaian pesan antara satu Visitor dan chatbot sebuah Business.
_Avoid_: Chat, session, thread

**Unanswered Question**:
Pertanyaan Visitor yang tidak bisa dijawab chatbot dari Knowledge maupun katalog Product. Dicatat sebagai petunjuk Knowledge apa yang perlu ditambah Admin.
_Avoid_: Gap, missed question, fallback

### Isi

**Product**:
Barang yang dijual sebuah Business, tercatat di katalognya dengan kategori, harga, dan stok.
_Avoid_: Item, barang, SKU

**Knowledge**:
Informasi non-katalog milik sebuah Business (FAQ, ongkir, retur, panduan ukuran, cara bayar) yang dipakai chatbot untuk menjawab.
_Avoid_: Document, dokumen, FAQ, data
