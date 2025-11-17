Algorithm: ChaCha20-Poly1305 (AEAD)
Key derivation: PBKDF2-HMAC-SHA256
PBKDF2 iterations: 200000
Salt length: 16 bytes (random)
Nonce length: 12 bytes (random per encryption)
Key length: 32 bytes
Input types: text, .txt, .csv (max size 1 MB)
Output format: hex encoding of (salt || nonce || ciphertext)
CLI modes: encrypt, decrypt
Dependency: cryptography, pandas (optional)
