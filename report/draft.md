# Draft Laporan — ChaCha20-Poly1305

## Ringkasan singkat

Dokumen ini merupakan draf awal bagian penelitian dan penjelasan algoritma untuk proyek "Keamanan Data". Tujuan: memberi landasan teoretis dan praktis untuk implementasi enkripsi/dekripsi menggunakan ChaCha20-Poly1305, sesuai KAK. Laporan ini mencakup: gambaran algoritma, alasan pemilihan, alur proses enkripsi/dekripsi, contoh manual singkat, dan daftar referensi singkat.

## Mengapa ChaCha20-Poly1305?

* ChaCha20-Poly1305 adalah konstruk AEAD (Authenticated Encryption with Associated Data) yang menyediakan kerahasiaan dan integritas dalam satu operasi.
* Implementasinya di pustaka Python (`cryptography`) bersifat langsung, aman, dan mengurangi potensi kesalahan implementasi yang umum ketika menggunakan mode blok tradisional (mis. AES-CBC + HMAC).
* ChaCha20 lebih cepat pada CPU tanpa akselerasi AES dan aman terhadap beberapa kelas serangan yang memerlukan padding atau mode operasi yang rumit.

## Ringkasan teknis (konsep)

* ChaCha20: stream cipher yang menghasilkan keystream 64-byte per blok internal. Enkripsi dilakukan dengan XOR antara plaintext dan keystream.
* Poly1305: MAC (message authentication code) yang menghasilkan tag autentikasi untuk memastikan integritas dan otentikasi pesan.
* ChaCha20-Poly1305 menggabungkan keduanya sehingga hasil enkripsi berisi ciphertext plus tag autentikasi. Dekripsi memverifikasi tag sebelum mengembalikan plaintext.

## Sifat yang relevan untuk tugas

* AEAD: tidak perlu implementasi MAC terpisah. Tag otomatis divalidasi oleh API dekripsi.
* Nonce unik per enkripsi: keamanan bergantung pada penggunaan nonce yang tidak berulang untuk pasangan key/nonce.
* Key length 32 byte (256-bit). Nonce 12 byte direkomendasikan (tergantung API). Salt untuk KDF disarankan 16 byte.

## Desain penyimpanan hasil enkripsi (disarankan)

Gunakan format terstruktur yang mudah diparsing:

```
hex( salt || nonce || ciphertext )
```

* salt: 16 byte random (dipakai saat derive key dari password)
* nonce: 12 byte random (dipakai langsung oleh ChaCha20-Poly1305)
* ciphertext: hasil enkripsi (termasuk tag yang melekat pada akhir ciphertext menurut API)

Tulis byte-order sebagai: salt (16) diikuti nonce (12) lalu ciphertext.

## Key management (pilihan implementasi untuk tugas)

Dua opsi:

1. Terima key 32-byte (hex) langsung dari pengguna. Simpel, cocok untuk uji cepat.
2. Terima password dari pengguna dan derive key via PBKDF2-HMAC-SHA256:

   * Salt: 16 bytes (random per enkripsi). Simpan salt bersama ciphertext.
   * Iterasi: gunakan nilai tinggi yang sesuai; draf ini merekomendasikan 200000 iterasi.

Pilihan (2) lebih ramah pengguna dan dianjurkan untuk laporan akhir.

## Alur (flowchart mermaid)

```mermaid
flowchart TD
  A[Mulai] --> B{Mode}
  B -- encrypt --> C[Baca input (file/teks)]
  C --> D[Periksa ukuran <= 1 MB]
  D --> E{Key source}
  E -- password --> F[Generate salt; derive key PBKDF2]
  E -- raw key --> G[Gunakan key langsung]
  F --> H[Generate nonce 12B]
  G --> H
  H --> I[Encrypt menggunakan ChaCha20-Poly1305]
  I --> J[Concat salt||nonce||ciphertext]
  J --> K[Hex-encode dan simpan sebagai out file]
  K --> L[Selesai]
  B -- decrypt --> M[Baca in file (hex)]
  M --> N[Parse salt||nonce||ciphertext]
  N --> O[Derive key jika perlu menggunakan salt]
  O --> P[Decrypt dan verifikasi tag]
  P --> Q[Tulis output plaintext]
  Q --> L
```

## Contoh manual singkat (ilustrasi langkah untuk string "HELLO")

1. Password: "mypw".
2. Generate salt (16b) = `0xA1B2...`.
3. Derive key = PBKDF2(password="mypw", salt, iter=200000) -> 32b key.
4. Generate nonce (12b) = `0x01FF...`.
5. Encrypt: ciphertext = ChaCha20Poly1305(key).encrypt(nonce, b"HELLO", aad=None) -> menghasilkan ciphertext+tag.
6. Output file = hex(salt||nonce||ciphertext+tag).

Contoh (hipotetis) hex: `a1b2... || 01ff... || deadbeef...`.

## Catatan implementasi praktis

* Pastikan memeriksa ukuran file sebelum alokasi memori (tolak >1MB).
* Tangani error dekripsi: bila tag tidak valid, tampilkan pesan "dekripsi gagal: tag mismatch / key salah" dan jangan tulis file output yang korup.
* Jangan reuse nonce untuk key yang sama. Implementasi ini menghasilkan nonce random 12b setiap enkripsi, sehingga kemungkinan tabrakan sangat kecil.

## Daftar referensi (draf)

* D. J. Bernstein, "ChaCha, a variant of Salsa20", e.g., RFC 8439 (ChaCha20 and Poly1305 for IETF protocols).
* "Cryptography.io" — dokumentasi library `cryptography` (ChaCha20Poly1305).
* "Crypto101" — pengantar kriptografi untuk praktisi.
* NIST SP 800-38A (untuk mode operasi blok; referensi lintas jika dibandingkan dengan CBC).
