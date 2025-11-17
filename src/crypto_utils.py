"""
crypto_utils.py

Implements ChaCha20-Poly1305 file encryption/decryption with PBKDF2 key derivation.
Output format: hex(salt(16) || nonce(12) || ciphertext)

Usage (CLI):
  python src/crypto_utils.py encrypt --in src/tests/sample.txt --out out.enc --password
  python src/crypto_utils.py decrypt --in out.enc --out out.txt --password

Dependencies: cryptography
Install: pip install cryptography
"""

import os
import argparse
import binascii
from typing import Tuple, Optional

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


# Constants (keep in sync with SPEC.md)
SALT_LEN = 16
NONCE_LEN = 12
KEY_LEN = 32
PBKDF2_ITERS = 200000
MAX_INPUT_SIZE = 1 * 1024 * 1024  # 1 MB


def derive_key_from_password(password: str, salt: bytes, iterations: int = PBKDF2_ITERS) -> bytes:
    """Derive a 32-byte key from password using PBKDF2-HMAC-SHA256."""
    if not isinstance(password, (bytes, bytearray)):
        password = password.encode("utf-8")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LEN,
        salt=salt,
        iterations=iterations,
    )
    key = kdf.derive(password)
    return key


def encrypt_bytes(key: bytes, plaintext: bytes, associated_data: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    """Encrypt plaintext bytes with ChaCha20-Poly1305.
    Returns (nonce, ciphertext).
    The returned ciphertext already contains the authentication tag appended (as per API).
    """
    if len(key) != KEY_LEN:
        raise ValueError("Key must be 32 bytes long")
    chacha = ChaCha20Poly1305(key)
    nonce = os.urandom(NONCE_LEN)
    ct = chacha.encrypt(nonce, plaintext, associated_data)
    return nonce, ct


def decrypt_bytes(key: bytes, nonce: bytes, ciphertext: bytes, associated_data: Optional[bytes] = None) -> bytes:
    """Decrypt ciphertext with ChaCha20-Poly1305 and verify tag. Raises exception on failure."""
    if len(key) != KEY_LEN:
        raise ValueError("Key must be 32 bytes long")
    chacha = ChaCha20Poly1305(key)
    pt = chacha.decrypt(nonce, ciphertext, associated_data)
    return pt


def _read_file_check_size(path: str) -> bytes:
    st = os.stat(path)
    if st.st_size > MAX_INPUT_SIZE:
        raise ValueError(f"Input file too large ({st.st_size} bytes). Max allowed is {MAX_INPUT_SIZE} bytes")
    with open(path, "rb") as f:
        return f.read()


def encrypt_file(in_path: str, out_path: str, password: Optional[str] = None, key_hex: Optional[str] = None,
                 use_password: bool = True) -> None:
    """Encrypt file at in_path and write hex(salt||nonce||ciphertext) to out_path.

    Provide either password (derive key) or key_hex (32-byte hex string). If use_password=True, password must be provided.
    """
    if use_password and (password is None):
        raise ValueError("Password required when use_password=True")

    data = _read_file_check_size(in_path)

    # Determine key and salt
    if use_password:
        salt = os.urandom(SALT_LEN)
        key = derive_key_from_password(password, salt)
    else:
        if not key_hex:
            raise ValueError("key_hex required when not using password")
        key = binascii.unhexlify(key_hex)
        if len(key) != KEY_LEN:
            raise ValueError("Provided key_hex does not represent a 32-byte key")
        salt = b""  # no salt when raw key provided

    nonce, ciphertext = encrypt_bytes(key, data)

    # Output bytes: salt (if any, else empty) || nonce || ciphertext
    out_bytes = (salt + nonce + ciphertext)
    out_hex = binascii.hexlify(out_bytes).decode("ascii")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out_hex)


def decrypt_file(in_path: str, out_path: str, password: Optional[str] = None, key_hex: Optional[str] = None,
                 use_password: bool = True) -> None:
    """Read hex(salt||nonce||ciphertext) from in_path and write plaintext to out_path.

    If use_password=True, password must be provided and salt will be read from the input.
    If use_password=False, key_hex must be provided and no salt is expected in input.
    """
    with open(in_path, "r", encoding="utf-8") as f:
        hexdata = f.read().strip()
    try:
        all_bytes = binascii.unhexlify(hexdata)
    except binascii.Error:
        raise ValueError("Input file is not valid hex")

    if use_password:
        if len(all_bytes) < (SALT_LEN + NONCE_LEN + 16):  # minimal tag size
            raise ValueError("Input data too short to contain salt+nonce+ciphertext")
        salt = all_bytes[:SALT_LEN]
        nonce = all_bytes[SALT_LEN:SALT_LEN + NONCE_LEN]
        ciphertext = all_bytes[SALT_LEN + NONCE_LEN:]
        key = derive_key_from_password(password, salt)
    else:
        if len(all_bytes) < (NONCE_LEN + 16):
            raise ValueError("Input data too short to contain nonce+ciphertext")
        salt = b""
        nonce = all_bytes[:NONCE_LEN]
        ciphertext = all_bytes[NONCE_LEN:]
        if not key_hex:
            raise ValueError("key_hex required when not using password")
        key = binascii.unhexlify(key_hex)
        if len(key) != KEY_LEN:
            raise ValueError("Provided key_hex does not represent a 32-byte key")

    try:
        plaintext = decrypt_bytes(key, nonce, ciphertext)
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")

    with open(out_path, "wb") as f:
        f.write(plaintext)


# CLI functions removed; this file now contains only cryptographic utilities.
