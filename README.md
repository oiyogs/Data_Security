# Keamanan Data CLI — ChaCha20-Poly1305

## Deskripsi

Aplikasi Command-Line Interface (CLI) untuk melakukan enkripsi dan dekripsi file menggunakan algoritma ChaCha20-Poly1305. Aplikasi mendukung dua metode key management:

1. **Password-based encryption** (PBKDF2-HMAC-SHA256 → key 32 byte)
2. **Raw key mode** (pengguna langsung memasukkan key hex 32 byte)

Aplikasi ini dibuat sesuai pedoman pada KAK Kriptografi/Keamanan Data dan memenuhi seluruh persyaratan input, proses, dan output.

---

## Fitur Utama

* Enkripsi & dekripsi file `.txt` dan `.csv` (maksimal ukuran 1 MB).
* Penggunaan algoritma ChaCha20-Poly1305 (AEAD): confidentiality + integrity.
* PBKDF2-HMAC-SHA256 sebagai metode derivasi key dari password.
* Salt 16B untuk PBKDF2, Nonce 12B untuk ChaCha20.
* Output terenkripsi dalam format: **hex(salt || nonce || ciphertext)** (untuk password mode).
* Raw key mode untuk penggunaan tingkat lanjut.
* Dukungan error-handling untuk file rusak, password salah, atau tag authentication gagal.

---

## Instalasi

### 1. Aktifkan Virtual Environment

**Windows PowerShell**

```
.venv\Scripts\Activate.ps1
```

**Linux/macOS**

```
source .venv/bin/activate
```

### 2. Install dependency

```
pip install -r requirements.txt
```

---

## Cara Penggunaan

### 1. Enkripsi dengan Password (Mode Utama)

```
python src/cli_crypto.py encrypt --in src/tests/sample.txt --out sample.enc --password cihuy123
```

Output:

* `sample.enc` berisi hex: salt(16B) + nonce(12B) + ciphertext+tag

### 2. Dekripsi dengan Password

```
python src/cli_crypto.py decrypt --in sample.enc --out hasil.txt --password cihuy123
```

`hasil.txt` harus identik dengan file input.

---

## Raw Key Mode (Opsional)

### 1. Generate Raw Key 32-byte Hex

```
python -c "import os,binascii; print(binascii.hexlify(os.urandom(32)).decode())"
```

Contoh output:

```
2a9fbb13e3d5c7ae0b29fddce372991f4491aa1234556789ffeabcd124567890
```

### 2. Enkripsi dengan Raw Key

```
python src/cli_crypto.py encrypt --in src/tests/sample.txt --out raw.enc --keyhex <hexkey> --rawkey
```

Output format:

* **nonce(12B) || ciphertext+tag** (tanpa salt)

### 3. Dekripsi dengan Raw Key

```
python src/cli_crypto.py decrypt --in raw.enc --out raw_dec.txt --keyhex <hexkey> --rawkey
```

---

## Struktur Direktori

```
Keamanandata/
│ README.md
│ SPEC.md
│ requirements.txt
│
├─ src/
│  ├─ cli_crypto.py
│  ├─ crypto_utils.py
│  └─ tests/
│      ├─ sample.txt
│      └─ sample.csv
│
└─ report/
    └─ draft.md
```

---

## Format Output Enkripsi

### Password Mode

```
hex( salt(16B) || nonce(12B) || ciphertext+tag )
```

### Raw Key Mode

```
hex( nonce(12B) || ciphertext+tag )
```

---

## Pengujian (Opsional)

### Dengan Pytest

Tes memastikan enkripsi → dekripsi menghasilkan file identik.

```
pytest -q
```

---

## Catatan Keamanan

* Jangan reuse key + nonce.
* Simpan password dengan aman.
* Kerusakan ciphertext atau salah password akan menyebabkan **Authentication Tag Mismatch** (expected behavior).

---

## Lisensi

Proyek ini dibuat dalam konteks tugas akademik Keamanan Data.
