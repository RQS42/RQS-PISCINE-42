# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    babel_crypto.py                                    :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: RQS_42 <RQS_42@student.42.fr>            +#+  +:+       +#+           #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/19 00:28:54 by RQS_42           #+#    #+#               #
#    Updated: 2026/08/19 00:28:54 by RQS_42          ###   ########.fr         #
#                                                                              #
# **************************************************************************** #

"""
Crypto and Pool Manager for 42 Exam Simulator.
Provides authenticated encryption (zero-dependency pure Python) to package
the pool directory into a single encrypted container ('data/ultimate_question_pool.enc').
Enables dynamic in-memory decryption of subjects and reference files during exams.
"""

import os
import io
import sys
import json
import zlib
import hmac
import hashlib
import struct
import shutil

# Default embedded encryption key (derived via PBKDF2)
# The maintainer can override this or generate a custom key when packing.
import base64

DEFAULT_SALT = b"42_PISCINE_EXAMSHELL_RQS_2026"

def _get_default_passphrase() -> str:
    """Returns the default passphrase via obfuscation to prevent casual plaintext scraping."""
    # "42_moulinette_secret_key_rqs_piscine_exam"
    encoded = b'NDJfbW91bGluZXR0ZV9zZWNyZXRfa2V5X3Jxc19waXNjaW5lX2V4YW0='
    return base64.b64decode(encoded).decode('utf-8')

DEFAULT_PASSPHRASE = _get_default_passphrase()


def _derive_keys(passphrase: str, salt: bytes):
    """Derive 64 bytes of key material: 32 bytes for ChaCha/Keystream, 32 bytes for HMAC."""
    key_material = hashlib.pbkdf2_hmac(
        "sha256", passphrase.encode("utf-8"), salt, iterations=100_000, dklen=64
    )
    enc_key = key_material[:32]
    mac_key = key_material[32:]
    return enc_key, mac_key


def _keystream_generator(key: bytes, nonce: bytes):
    """
    Fast keystream generator using HMAC-SHA256 in counter mode.
    Pure python, robust, zero-dependency stream cipher.
    """
    counter = 0
    while True:
        counter_bytes = struct.pack(">Q", counter)
        block = hmac.new(key, nonce + counter_bytes, hashlib.sha256).digest()
        for b in block:
            yield b
        counter += 1


def encrypt_bytes(data: bytes, passphrase: str = None) -> bytes:
    """
    Encrypts data with authenticated stream encryption.
    Format: [SALT (16B)] + [NONCE (16B)] + [HMAC-SHA256 (32B)] + [CIPHERTEXT]
    """
    if passphrase is None:
        passphrase = _get_default_passphrase()
    salt = os.urandom(16)
    nonce = os.urandom(16)
    enc_key, mac_key = _derive_keys(passphrase, salt)

    # Compress before encryption
    compressed = zlib.compress(data, level=9)

    # Encrypt with keystream
    stream = _keystream_generator(enc_key, nonce)
    ciphertext = bytes(b ^ next(stream) for b in compressed)

    # Compute HMAC over (nonce + ciphertext)
    mac = hmac.new(mac_key, nonce + ciphertext, hashlib.sha256).digest()

    return salt + nonce + mac + ciphertext


def decrypt_bytes(payload: bytes, passphrase: str = None) -> bytes:
    """
    Decrypts and authenticates ciphertext.
    Returns decompressed plaintext bytes or raises ValueError if invalid.
    """
    if passphrase is None:
        passphrase = _get_default_passphrase()
    if len(payload) < 64:
        raise ValueError("Invalid encrypted payload (too short)")

    salt = payload[:16]
    nonce = payload[16:32]
    expected_mac = payload[32:64]
    ciphertext = payload[64:]

    enc_key, mac_key = _derive_keys(passphrase, salt)

    # Verify HMAC
    actual_mac = hmac.new(mac_key, nonce + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(expected_mac, actual_mac):
        raise ValueError("Authentication failed! Corrupted or tampered pool data.")

    # Decrypt
    stream = _keystream_generator(enc_key, nonce)
    compressed = bytes(b ^ next(stream) for b in ciphertext)

    # Decompress
    try:
        return zlib.decompress(compressed)
    except Exception as e:
        raise ValueError(f"Decompression error: {e}")


class PoolManager:
    """
    Manages exam pool data seamlessly.
    Supports either plain 'pool/' directory (dev mode) or encrypted 'data/ultimate_question_pool.enc' (production mode).
    In encrypted mode, subjects and references are decrypted in RAM on-demand.
    """

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.plain_pool_dir = os.path.join(base_dir, "pool")
        self.enc_pool_file = os.path.join(base_dir, "data/ultimate_question_pool.enc")
        self.is_encrypted = False
        self._data_cache = {}  # exam_name -> { exercise_dir -> { filename: bytes } }
        self._load_pool()

    def _load_pool(self):
        # Prefer encrypted pool if plain pool doesn't exist or if pool.enc is explicitly present
        if os.path.exists(self.enc_pool_file) and not os.path.isdir(
            self.plain_pool_dir
        ):
            self._load_encrypted()
        elif os.path.isdir(self.plain_pool_dir):
            self._load_plain()
        elif os.path.exists(self.enc_pool_file):
            self._load_encrypted()
        else:
            raise FileNotFoundError(
                f"Neither '{self.plain_pool_dir}' nor '{self.enc_pool_file}' was found!"
            )

    def _load_plain(self):
        self.is_encrypted = False
        self._data_cache = {}
        for exam in sorted(os.listdir(self.plain_pool_dir)):
            exam_path = os.path.join(self.plain_pool_dir, exam)
            if os.path.isdir(exam_path) and not exam.startswith("."):
                self._data_cache[exam] = {}
                for ex_dir in sorted(os.listdir(exam_path)):
                    ex_path = os.path.join(exam_path, ex_dir)
                    if os.path.isdir(ex_path) and not ex_dir.startswith("."):
                        self._data_cache[exam][ex_dir] = {}
                        for fname in os.listdir(ex_path):
                            fpath = os.path.join(ex_path, fname)
                            if os.path.isfile(fpath):
                                with open(fpath, "rb") as f:
                                    self._data_cache[exam][ex_dir][fname] = f.read()

    def _load_encrypted(self):
        self.is_encrypted = True
        with open(self.enc_pool_file, "rb") as f:
            raw_enc = f.read()
        decrypted_json = decrypt_bytes(raw_enc).decode("utf-8")
        raw_dict = json.loads(decrypted_json)

        # Convert hex/base64 or string files to bytes in RAM cache
        self._data_cache = {}
        for exam, exercises in raw_dict.items():
            self._data_cache[exam] = {}
            for ex_dir, files in exercises.items():
                self._data_cache[exam][ex_dir] = {}
                for fname, content in files.items():
                    if isinstance(content, str):
                        self._data_cache[exam][ex_dir][fname] = content.encode("utf-8")
                    else:
                        self._data_cache[exam][ex_dir][fname] = bytes(content)

    def list_exams(self):
        """Returns sorted list of available exams (e.g. ['Exam00', 'Exam01', ...])."""
        return sorted(
            [
                k
                for k in self._data_cache.keys()
                if not k.startswith(".") and k != "README.md"
            ]
        )

    def get_exam_levels(self, exam_name: str):
        """
        Returns a dict mapping level_int -> list of exercise directory names.
        Example: {0: ['0-aff_a', '0-aff_z'], 1: ['1-ft_strlen', ...]}
        """
        if exam_name not in self._data_cache:
            return {}

        levels = {}
        for ex_dir in self._data_cache[exam_name].keys():
            if "-" in ex_dir:
                lvl_str = ex_dir.split("-", 1)[0]
                if lvl_str.isdigit():
                    lvl = int(lvl_str)
                    levels.setdefault(lvl, []).append(ex_dir)
        for lvl in levels:
            levels[lvl].sort()
        return levels

    def get_all_exercises(self, exam_name: str = None):
        """
        Returns a list of all exercise names (or directory names) for an exam,
        or across all exams if exam_name is None.
        """
        if exam_name:
            if exam_name not in self._data_cache:
                return []
            return sorted(list(self._data_cache[exam_name].keys()))
        all_exos = {}
        for ex, exercises in self._data_cache.items():
            all_exos[ex] = sorted(list(exercises.keys()))
        return all_exos

    def get_total_exercise_count(self, exam_name: str = None):
        """Returns the total number of unique exercises in an exam or all exams."""
        if exam_name:
            return len(self._data_cache.get(exam_name, {}))
        return sum(len(exos) for exos in self._data_cache.values())

    def get_subject_text(self, exam_name: str, ex_dir: str) -> str:
        """Finds and returns the subject text (French/English preferred)."""
        files = self._data_cache.get(exam_name, {}).get(ex_dir, {})
        for name in ["subject.en.txt", "subject.fr.txt", "subject.txt", "sub.txt"]:
            if name in files:
                return files[name].decode("utf-8", errors="ignore")
        for name, content in files.items():
            if "subject" in name.lower() and name.endswith(".txt"):
                return content.decode("utf-8", errors="ignore")
        return "No subject file found."

    def get_files_dict(self, exam_name: str, ex_dir: str):
        """Returns a dict of filename -> bytes for the specified exercise."""
        return self._data_cache.get(exam_name, {}).get(ex_dir, {})


def pack_pool_to_encrypted_file(
    plain_pool_dir: str, output_enc_path: str, passphrase: str = None
):
    """
    Packs a plain 'pool/' directory into an encrypted 'data/ultimate_question_pool.enc' container.
    """
    if passphrase is None:
        passphrase = _get_default_passphrase()
    if not os.path.isdir(plain_pool_dir):
        raise FileNotFoundError(f"Source pool directory not found: {plain_pool_dir}")

    pool_data = {}
    for exam in sorted(os.listdir(plain_pool_dir)):
        exam_path = os.path.join(plain_pool_dir, exam)
        if os.path.isdir(exam_path) and not exam.startswith("."):
            pool_data[exam] = {}
            for ex_dir in sorted(os.listdir(exam_path)):
                ex_path = os.path.join(exam_path, ex_dir)
                if os.path.isdir(ex_path) and not ex_dir.startswith("."):
                    pool_data[exam][ex_dir] = {}
                    for fname in os.listdir(ex_path):
                        fpath = os.path.join(ex_path, fname)
                        if os.path.isfile(fpath) and not fname.startswith("."):
                            with open(fpath, "rb") as f:
                                # Store as string if UTF-8 text, or latin-1 fallback
                                raw = f.read()
                                try:
                                    pool_data[exam][ex_dir][fname] = raw.decode("utf-8")
                                except UnicodeDecodeError:
                                    pool_data[exam][ex_dir][fname] = raw.decode(
                                        "latin-1"
                                    )

    json_bytes = json.dumps(pool_data, ensure_ascii=False).encode("utf-8")
    enc_payload = encrypt_bytes(json_bytes, passphrase)

    with open(output_enc_path, "wb") as f:
        f.write(enc_payload)

    return len(enc_payload), len(json_bytes)
