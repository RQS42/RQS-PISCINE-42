# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    vogon_packer.py                                    :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: RQS_42 <RQS_42@student.42.fr>            +#+  +:+       +#+           #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/19 00:28:54 by RQS_42           #+#    #+#               #
#    Updated: 2026/08/19 00:28:54 by RQS_42          ###   ########.fr         #
#                                                                              #
# **************************************************************************** #

#!/usr/bin/env python3
"""
Pool Packaging & Encryption Utility for 42 Exam Simulator.
Packs the plain 'pool/' directory into an encrypted, compressed binary container ('data/ultimate_question_pool.enc').
Prevents users from browsing or extracting exercises in advance.
"""

import os
import sys
import argparse

# Add parent directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from deep_thought_core.babel_crypto import (
    pack_pool_to_encrypted_file,
    decrypt_bytes,
    DEFAULT_PASSPHRASE,
)
from deep_thought_core.sirius_cybernetics_ui import (
    RESET,
    BOLD,
    GREEN,
    RED,
    YELLOW,
    CYAN,
    WHITE,
    COLOR_42_TEAL,
    COLOR_NEON_BLUE,
    COLOR_GOLD,
    print_header,
    print_success,
    print_failure,
    print_warning,
    print_info,
)


def main():
    parser = argparse.ArgumentParser(
        description="Pack and Encrypt the 42 Piscine Exam Pool"
    )
    parser.add_argument(
        "--pool",
        "-p",
        default=os.path.join(BASE_DIR, "pool"),
        help="Path to source pool directory (default: ./pool)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=os.path.join(BASE_DIR, "data/ultimate_question_pool.enc"),
        help="Path to output encrypted file (default: ./pool.enc)",
    )
    parser.add_argument(
        "--key",
        "-k",
        default=DEFAULT_PASSPHRASE,
        help="Custom encryption passphrase (optional)",
    )
    args = parser.parse_args()

    pool_dir = os.path.abspath(args.pool)
    output_path = os.path.abspath(args.output)

    print(
        f"\n{COLOR_42_TEAL}{BOLD}╔════════════════════════════════════════════════════════════════════╗{RESET}"
    )
    print(
        f"{COLOR_42_TEAL}{BOLD}║{WHITE}          🔒 42 EXAMSHELL - POOL ENCRYPTION & PACKAGING             {COLOR_42_TEAL}║{RESET}"
    )
    print(
        f"{COLOR_42_TEAL}{BOLD}╚════════════════════════════════════════════════════════════════════╝{RESET}\n"
    )

    if not os.path.isdir(pool_dir):
        print_failure(f"Source pool directory does not exist: {pool_dir}")
        sys.exit(1)

    print(f"Scanning pool directory: {CYAN}{pool_dir}{RESET} ...")
    exams = [
        d
        for d in os.listdir(pool_dir)
        if os.path.isdir(os.path.join(pool_dir, d)) and not d.startswith(".")
    ]
    total_exos = 0
    total_files = 0

    for exam in exams:
        exam_path = os.path.join(pool_dir, exam)
        exos = [
            d
            for d in os.listdir(exam_path)
            if os.path.isdir(os.path.join(exam_path, d))
        ]
        total_exos += len(exos)
        for exo in exos:
            exo_path = os.path.join(exam_path, exo)
            files = [
                f
                for f in os.listdir(exo_path)
                if os.path.isfile(os.path.join(exo_path, f))
            ]
            total_files += len(files)

    print(
        f"Found {BOLD}{len(exams)}{RESET} exams, {BOLD}{total_exos}{RESET} exercises, {BOLD}{total_files}{RESET} files."
    )
    print(f"Encrypting and compressing into: {GREEN}{output_path}{RESET} ...")

    try:
        enc_size, raw_size = pack_pool_to_encrypted_file(
            pool_dir, output_path, args.key
        )

        # Self-test verification: try decrypting immediately
        with open(output_path, "rb") as f:
            test_payload = f.read()
        decrypted = decrypt_bytes(test_payload, args.key)
        assert len(decrypted) == raw_size, "Decrypted size mismatch!"

        ratio = (1.0 - (enc_size / raw_size)) * 100.0 if raw_size > 0 else 0.0

        print_success("Pool successfully encrypted and verified!")
        print(f"  • Plain JSON Size  : {raw_size:,} bytes")
        print(
            f"  • Encrypted Bundle : {GREEN}{BOLD}{enc_size:,} bytes{RESET} ({ratio:.1f}% compression)"
        )
        print(f"  • Output file      : {CYAN}{output_path}{RESET}\n")

        print(f"{YELLOW}💡 Next steps for distribution:{RESET}")
        print(f"  1. Keep '{os.path.basename(output_path)}' in the repository.")
        print(
            f"  2. You can safely remove or hide the '{os.path.basename(pool_dir)}/' directory for students."
        )
        print(
            f"  3. When students launch 'dont_panic.py', it will decrypt exercises in RAM only.\n"
        )

    except Exception as e:
        print_failure(f"Error during pool packaging: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
