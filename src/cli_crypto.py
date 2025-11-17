#!/usr/bin/env python3
"""
CLI wrapper for encryption utilities.
This script calls functions from crypto_utils.py which implements ChaCha20-Poly1305
with PBKDF2 key derivation.

Run from project root as:
  python src/cli_crypto.py encrypt --in src/tests/sample.txt --out out.enc --password mypass
  python src/cli_crypto.py decrypt --in out.enc --out out.txt --password mypass

If you prefer raw key mode (no PBKDF2/salt), provide --keyhex <hexkey> and add --rawkey.
"""
import sys
import argparse

# Ensure the src directory is on path when running from project root
from pathlib import Path
proj_root = Path(__file__).resolve().parents[1]
if str(proj_root / 'src') not in sys.path:
    sys.path.insert(0, str(proj_root / 'src'))

try:
    from crypto_utils import encrypt_file, decrypt_file
except Exception as e:
    print(f"Failed to import crypto utilities: {e}")
    sys.exit(1)


def _parse_args():
    p = argparse.ArgumentParser(description="CLI: ChaCha20-Poly1305 file encrypt/decrypt")
    sub = p.add_subparsers(dest="cmd", required=True)

    enc = sub.add_parser("encrypt", help="Encrypt a file")
    enc.add_argument("--in", dest="in_path", required=True, help="Input file path")
    enc.add_argument("--out", dest="out_path", required=True, help="Output file path (hex) to write")
    group = enc.add_mutually_exclusive_group(required=True)
    group.add_argument("--password", help="Password to derive key (PBKDF2)")
    group.add_argument("--keyhex", help="Raw 32-byte key as hex string")
    enc.add_argument("--rawkey", action="store_true", help="Treat provided key as raw hex key (no salt will be used)")

    dec = sub.add_parser("decrypt", help="Decrypt a file")
    dec.add_argument("--in", dest="in_path", required=True, help="Input file path (hex) to read")
    dec.add_argument("--out", dest="out_path", required=True, help="Output plaintext file path")
    group2 = dec.add_mutually_exclusive_group(required=True)
    group2.add_argument("--password", help="Password to derive key (PBKDF2)")
    group2.add_argument("--keyhex", help="Raw 32-byte key as hex string")
    dec.add_argument("--rawkey", action="store_true", help="Treat provided key as raw hex key (no salt expected in input)")

    return p.parse_args()


def main():
    args = _parse_args()

    if args.cmd == "encrypt":
        use_password = not args.rawkey
        password = args.password
        keyhex = args.keyhex
        try:
            encrypt_file(args.in_path, args.out_path, password=password, key_hex=keyhex, use_password=use_password)
            print(f"Encrypted '{args.in_path}' -> '{args.out_path}'")
        except Exception as e:
            print(f"Encryption failed: {e}")
            sys.exit(2)

    elif args.cmd == "decrypt":
        use_password = not args.rawkey
        password = args.password
        keyhex = args.keyhex
        try:
            decrypt_file(args.in_path, args.out_path, password=password, key_hex=keyhex, use_password=use_password)
            print(f"Decrypted '{args.in_path}' -> '{args.out_path}'")
        except Exception as e:
            print(f"Decryption failed: {e}")
            sys.exit(3)


if __name__ == "__main__":
    main()
