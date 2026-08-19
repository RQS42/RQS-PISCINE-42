# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    test_crypto.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: RQS_42 <RQS_42@student.42.fr>            +#+  +:+       +#+           #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/19 00:28:54 by RQS_42           #+#    #+#               #
#    Updated: 2026/08/19 00:28:54 by RQS_42          ###   ########.fr         #
#                                                                              #
# **************************************************************************** #

"""
Unit tests for crypto and pool manager.
"""

import os
import sys
import tempfile
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from deep_thought_core.babel_crypto import (
    encrypt_bytes,
    decrypt_bytes,
    pack_pool_to_encrypted_file,
    PoolManager,
)


class TestCrypto(unittest.TestCase):
    def test_encrypt_decrypt_roundtrip(self):
        original = b"Hello 42 Piscine! This is secret test code."
        encrypted = encrypt_bytes(original, "test_secret_passphrase")
        self.assertNotEqual(original, encrypted)

        decrypted = decrypt_bytes(encrypted, "test_secret_passphrase")
        self.assertEqual(original, decrypted)

    def test_tamper_detection(self):
        original = b"Secure payload"
        encrypted = bytearray(encrypt_bytes(original, "secret"))
        # Flip a bit in ciphertext
        encrypted[-1] ^= 0xFF
        with self.assertRaises(ValueError):
            decrypt_bytes(bytes(encrypted), "secret")

    def test_pool_manager_plain_and_encrypted(self):
        pm = PoolManager(BASE_DIR)
        exams = pm.list_exams()
        self.assertIn("Exam00", exams)
        self.assertIn("Exam01", exams)
        self.assertIn("Exam02", exams)
        self.assertIn("Exam03", exams)

        # Check levels
        levels01 = pm.get_exam_levels("Exam01")
        self.assertIn(1, levels01)
        self.assertTrue(len(levels01[1]) > 0)

        # Check subject text
        subj = pm.get_subject_text("Exam01", "1-ft_strlen")
        self.assertIn("ft_strlen", subj)

        # Check files dict
        files = pm.get_files_dict("Exam01", "1-ft_strlen")
        self.assertIn("ft_strlen.c", files)


if __name__ == "__main__":
    unittest.main()
