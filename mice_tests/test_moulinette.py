# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    test_moulinette.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: RQS_42 <RQS_42@student.42.fr>            +#+  +:+       +#+           #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/19 00:28:54 by RQS_42           #+#    #+#               #
#    Updated: 2026/08/19 00:28:54 by RQS_42          ###   ########.fr         #
#                                                                              #
# **************************************************************************** #

"""
Unit tests for Moulinette grading engine.
"""

import os
import sys
import shutil
import tempfile
import subprocess
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from deep_thought_core.babel_crypto import PoolManager
from deep_thought_core.moulinette_vogon_auditor import Moulinette


class TestMoulinette(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_examshell_")
        self.server_repo = os.path.join(self.temp_dir, "server", "rendu.git")
        os.makedirs(self.server_repo, exist_ok=True)
        subprocess.run(
            ["git", "init", "--bare"], cwd=self.server_repo, capture_output=True
        )

        self.rendu_dir = os.path.join(self.temp_dir, "rendu")
        subprocess.run(
            ["git", "clone", self.server_repo, self.rendu_dir], capture_output=True
        )

        self.pool_manager = PoolManager(BASE_DIR)
        self.moulinette = Moulinette(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _push_student_code(self, exercise_name: str, code_content: str):
        exo_dir = os.path.join(self.rendu_dir, exercise_name)
        os.makedirs(exo_dir, exist_ok=True)
        c_file = os.path.join(exo_dir, f"{exercise_name}.c")
        with open(c_file, "w", encoding="utf-8") as f:
            f.write(code_content)

        subprocess.run(["git", "add", "."], cwd=self.rendu_dir, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"add {exercise_name}"],
            cwd=self.rendu_dir,
            capture_output=True,
        )
        subprocess.run(["git", "push"], cwd=self.rendu_dir, capture_output=True)

    def test_grade_function_success(self):
        # Good ft_strlen
        code = """
int ft_strlen(char *str) {
    int i = 0;
    while (str[i]) i++;
    return i;
}
"""
        self._push_student_code("ft_strlen", code)
        passed, reason, trace = self.moulinette.evaluate(
            "Exam01", "1-ft_strlen", "ft_strlen", self.pool_manager, self.server_repo
        )
        self.assertTrue(passed)
        self.assertEqual(reason, "SUCCESS")

    def test_grade_function_wrong_output(self):
        # Wrong ft_strlen
        code = """
int ft_strlen(char *str) {
    (void)str;
    return 42;
}
"""
        self._push_student_code("ft_strlen", code)
        passed, reason, trace = self.moulinette.evaluate(
            "Exam01", "1-ft_strlen", "ft_strlen", self.pool_manager, self.server_repo
        )
        self.assertFalse(passed)
        self.assertEqual(reason, "Wrong output")
        self.assertTrue(os.path.exists(trace))

    def test_grade_program_success(self):
        # Good only_z
        code = """
#include <unistd.h>
int main(void) {
    write(1, "z", 1);
    return 0;
}
"""
        self._push_student_code("only_z", code)
        passed, reason, trace = self.moulinette.evaluate(
            "Exam01", "0-only_z", "only_z", self.pool_manager, self.server_repo
        )
        self.assertTrue(passed)
        self.assertEqual(reason, "SUCCESS")

    def test_grade_timeout_protection(self):
        # Infinite loop
        code = """
#include <unistd.h>
int main(void) {
    while (1) {
        // infinite loop
    }
    return 0;
}
"""
        self._push_student_code("only_z", code)
        passed, reason, trace = self.moulinette.evaluate(
            "Exam01", "0-only_z", "only_z", self.pool_manager, self.server_repo
        )
        self.assertFalse(passed)
        self.assertIn("TIMEOUT", reason)


if __name__ == "__main__":
    unittest.main()
