# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    moulinette_vogon_auditor.py                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: RQS_42 <RQS_42@student.42.fr>            +#+  +:+       +#+           #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/19 00:28:54 by RQS_42           #+#    #+#               #
#    Updated: 2026/08/19 00:28:54 by RQS_42          ###   ########.fr         #
#                                                                              #
# **************************************************************************** #

"""
Moulinette Test & Grading Engine for 42 Exam Simulator.
Provides comprehensive C code evaluation, automated test harness generation,
anti-infinite loop timeout protection, signal/segfault handling, and diff trace generation.
"""

import os
import sys
import time
import shutil
import tempfile
import subprocess
from typing import Dict, Tuple, List, Optional, Any

from deep_thought_core.sirius_cybernetics_ui import (
    RESET,
    BOLD,
    DIM,
    GREEN,
    RED,
    YELLOW,
    CYAN,
    WHITE,
    print_success,
    print_failure,
    print_warning,
    print_info,
)

# Standard function test harnesses when no main.c is present in the pool
FUNCTION_HARNESSES: Dict[str, str] = {
    "ft_strlen": """
#include <stdio.h>
int ft_strlen(char *str);
int main(void) {
    char *tests[] = {"", "a", "42", "Hello World!", "Testing\\twith\\nspecial\\0hidden", "Long string 12345678901234567890"};
    for (int i = 0; i < 6; i++) {
        printf("len('%s') = %d\\n", tests[i], ft_strlen(tests[i]));
    }
    return 0;
}
""",
    "ft_swap": """
#include <stdio.h>
void ft_swap(int *a, int *b);
int main(void) {
    int a = 42, b = 24;
    ft_swap(&a, &b);
    printf("swap(42, 24) -> a=%d, b=%d\\n", a, b);
    a = -100; b = 500;
    ft_swap(&a, &b);
    printf("swap(-100, 500) -> a=%d, b=%d\\n", a, b);
    a = 0; b = 0;
    ft_swap(&a, &b);
    printf("swap(0, 0) -> a=%d, b=%d\\n", a, b);
    return 0;
}
""",
    "ft_strcmp": """
#include <stdio.h>
int ft_strcmp(char *s1, char *s2);
int main(void) {
    char *p[][2] = {
        {"hello", "hello"},
        {"abc", "abd"},
        {"abd", "abc"},
        {"", ""},
        {"a", ""},
        {"", "a"},
        {"42Piscine", "42piscine"},
        {"test123", "test"}
    };
    for (int i = 0; i < 8; i++) {
        int res = ft_strcmp(p[i][0], p[i][1]);
        int sign = (res > 0) ? 1 : ((res < 0) ? -1 : 0);
        printf("strcmp('%s', '%s') = %d (sign: %d)\\n", p[i][0], p[i][1], res, sign);
    }
    return 0;
}
""",
    "ft_strrev": """
#include <stdio.h>
#include <string.h>
char *ft_strrev(char *str);
int main(void) {
    char t1[] = "";
    char t2[] = "a";
    char t3[] = "42";
    char t4[] = "kayak";
    char t5[] = "Hello World!";
    char t6[] = "abcdef";
    printf("rev('') -> '%s'\\n", ft_strrev(t1));
    printf("rev('a') -> '%s'\\n", ft_strrev(t2));
    printf("rev('42') -> '%s'\\n", ft_strrev(t3));
    printf("rev('kayak') -> '%s'\\n", ft_strrev(t4));
    printf("rev('Hello World!') -> '%s'\\n", ft_strrev(t5));
    printf("rev('abcdef') -> '%s'\\n", ft_strrev(t6));
    return 0;
}
""",
    "ft_atoi": """
#include <stdio.h>
int ft_atoi(const char *str);
int main(void) {
    char *tests[] = {
        "0", "42", "-42", "   +1234", "  -9876abc",
        "2147483647", "-2147483648", "\\t\\n\\r\\v\\f  -523",
        "--42", "++42", "+-42", "abc42", ""
    };
    for (int i = 0; i < 13; i++) {
        printf("atoi('%s') = %d\\n", tests[i], ft_atoi(tests[i]));
    }
    return 0;
}
""",
    "ft_range": """
#include <stdio.h>
#include <stdlib.h>
int *ft_range(int min, int max);
int main(void) {
    int cases[][2] = {{1, 3}, {-1, 2}, {0, 0}, {0, -3}, {5, 2}, {-5, -2}};
    for (int c = 0; c < 6; c++) {
        int min = cases[c][0];
        int max = cases[c][1];
        int *tab = ft_range(min, max);
        printf("range(%d, %d): ", min, max);
        if (!tab) {
            printf("NULL\\n");
        } else {
            int len = (min < max) ? (max - min) : (min - max + 1);
            for (int i = 0; i < len; i++) {
                printf("%d ", tab[i]);
            }
            printf("\\n");
            free(tab);
        }
    }
    return 0;
}
""",
    "ft_itoa": """
#include <stdio.h>
#include <stdlib.h>
char *ft_itoa(int nbr);
int main(void) {
    int tests[] = {0, 42, -42, 2147483647, -2147483648, 1, -1, 1000, -9999};
    for (int i = 0; i < 9; i++) {
        char *res = ft_itoa(tests[i]);
        printf("itoa(%d) = '%s'\\n", tests[i], res ? res : "NULL");
        if (res) free(res);
    }
    return 0;
}
""",
    "ft_split": """
#include <stdio.h>
#include <stdlib.h>
char **ft_split(char *str);
int main(void) {
    char *tests[] = {
        "   hello   world   42   piscine  ",
        "one_word",
        "   ",
        "",
        "tab\\tseparated\\nwords\\vtest",
        "  a   b   c  "
    };
    for (int t = 0; t < 6; t++) {
        printf("split test %d:\\n", t);
        char **res = ft_split(tests[t]);
        if (!res) {
            printf("  NULL\\n");
            continue;
        }
        for (int i = 0; res[i]; i++) {
            printf("  [%d] = '%s'\\n", i, res[i]);
            free(res[i]);
        }
        free(res);
    }
    return 0;
}
""",
    "ft_strcpy": """
#include <stdio.h>
char *ft_strcpy(char *s1, char *s2);
int main(void) {
    char buf[100];
    printf("strcpy: '%s'\\n", ft_strcpy(buf, "Hello 42!"));
    printf("strcpy: '%s'\\n", ft_strcpy(buf, ""));
    printf("strcpy: '%s'\\n", ft_strcpy(buf, "Test with special chars #@!$%^&*()"));
    return 0;
}
""",
    "print_bits": """
#include <unistd.h>
void print_bits(unsigned char octet);
int main(void) {
    unsigned char vals[] = {0, 1, 2, 42, 65, 128, 255};
    for (int i = 0; i < 7; i++) {
        print_bits(vals[i]);
        write(1, "\\n", 1);
    }
    return 0;
}
""",
    "reverse_bits": """
#include <stdio.h>
unsigned char reverse_bits(unsigned char octet);
int main(void) {
    unsigned char vals[] = {0, 1, 2, 42, 65, 128, 255};
    for (int i = 0; i < 7; i++) {
        printf("rev_bits(%u) = %u\\n", vals[i], (unsigned int)reverse_bits(vals[i]));
    }
    return 0;
}
""",
    "swap_bits": """
#include <stdio.h>
unsigned char swap_bits(unsigned char octet);
int main(void) {
    unsigned char vals[] = {0, 1, 2, 42, 65, 128, 255};
    for (int i = 0; i < 7; i++) {
        printf("swap_bits(%u) = %u\\n", vals[i], (unsigned int)swap_bits(vals[i]));
    }
    return 0;
}
""",
    "sort_list": """
#include <stdio.h>
#include <stdlib.h>
#include "list.h"

int ascending(int a, int b) {
    return (a <= b);
}

t_list *create_node(int data) {
    t_list *n = malloc(sizeof(t_list));
    n->data = data;
    n->next = NULL;
    return n;
}

t_list *sort_list(t_list* lst, int (*cmp)(int, int));

int main(void) {
    int arr[] = {42, 10, 5, 100, 24, 5, 0, -10};
    t_list *head = NULL, *cur = NULL;
    for (int i = 0; i < 8; i++) {
        t_list *n = create_node(arr[i]);
        if (!head) head = n;
        else cur->next = n;
        cur = n;
    }
    head = sort_list(head, ascending);
    cur = head;
    printf("sorted: ");
    while (cur) {
        printf("%d ", cur->data);
        t_list *tmp = cur;
        cur = cur->next;
        free(tmp);
    }
    printf("\\n");
    return 0;
}
""",
}

# Diverse argument test matrix for standalone programs
PROGRAM_ARG_TESTS: List[List[str]] = [
    [],
    [""],
    ["test"],
    ["hello", "world"],
    ["   42  piscine   paris  \t "],
    ["a", "b", "c", "d"],
    ["z"],
    ["-2147483648", "2147483647", "0", "-42"],
    ["padinton", "paqefwtdjetyiytjneytjoeyjnejeyj"],
    ["df6vewg64f", "fourtytwo"],
    ["rien ne sert de", "courir il faut", "partir a point"],
    ["salut", "a", "tous", "tout", "le", "monde"],
]


class Moulinette:
    """Evaluates student submissions against reference implementations and test harnesses."""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.trace_dir = os.path.join(base_dir, "trace")
        self.temp_dir = os.path.join(base_dir, "grademe_temp")
        os.makedirs(self.trace_dir, exist_ok=True)

    def _compile_c(
        self, src_file: str, extra_files: List[str], out_bin: str, cwd: str
    ) -> Tuple[bool, str]:
        """Compiles C code using gcc or clang with standard 42 flags."""
        
        # [SECURITY: Anti-Malware Scanner]
        banned = ["system(", "execve(", "exec(", "fork(", "popen("]
        for f in [src_file] + extra_files:
            if os.path.isfile(f) and f.endswith('.c'):
                try:
                    with open(f, 'r', encoding='utf-8', errors='ignore') as c_file:
                        content = c_file.read()
                        for b in banned:
                            if b in content:
                                return False, f"SECURITY BREACH: Banned function '{b}' detected in {f}. Execution aborted to prevent Arbitrary Code Execution."
                except Exception:
                    pass

        compiler = "cc" if shutil.which("cc") else "gcc"
        cmd = (
            [compiler, "-Wall", "-Wextra", "-Werror", src_file]
            + extra_files
            + ["-o", out_bin]
        )

        try:
            res = subprocess.run(
                cmd, cwd=cwd, capture_output=True, text=True, timeout=10
            )
            if res.returncode != 0:
                return False, res.stderr
            return True, ""
        except Exception as e:
            return False, str(e)

    def _run_binary(
        self, bin_path: str, args: List[str], cwd: str, timeout: float = 3.0
    ) -> Tuple[bool, str, int, str]:
        """
        Runs binary with timeout protection against infinite loops.
        Returns: (success, stdout, returncode, error_msg)
        """
        exe = bin_path
        if os.name == "nt" and not exe.endswith(".exe"):
            exe += ".exe"

        try:
            res = subprocess.run(
                [exe] + args, cwd=cwd, capture_output=True, text=True, timeout=timeout
            )
            return True, res.stdout, res.returncode, res.stderr
        except subprocess.TimeoutExpired:
            return (
                False,
                "",
                -1,
                f"TIMEOUT (Program exceeded {timeout}s - infinite loop detected!)",
            )
        except Exception as e:
            return False, "", -1, f"EXECUTION ERROR: {e}"

    def write_trace(
        self,
        exercise: str,
        reason: str,
        details: str = "",
        student_out: str = "",
        ref_out: str = "",
    ):
        """Writes detailed trace log for student feedback."""
        os.makedirs(self.trace_dir, exist_ok=True)
        trace_file = os.path.join(self.trace_dir, f"{exercise}_trace.txt")
        with open(trace_file, "w", encoding="utf-8") as f:
            f.write(
                f"╔════════════════════════════════════════════════════════════════╗\n"
            )
            f.write(f"║ MOULINETTE TRACE: {exercise.ljust(44)} ║\n")
            f.write(
                f"╚════════════════════════════════════════════════════════════════╝\n\n"
            )
            f.write(f"STATUS: {reason}\n")
            if details:
                f.write(f"\nDETAILS:\n{details}\n")
            if student_out:
                f.write(f"\n{'─' * 30} YOUR OUTPUT {'─' * 30}\n{student_out}\n")
            if ref_out:
                f.write(f"\n{'─' * 28} EXPECTED OUTPUT {'─' * 28}\n{ref_out}\n")
            f.write(f"\n{'─' * 73}\n")
        return trace_file

    def evaluate(
        self,
        exam_name: str,
        exercise_dir: str,
        exercise_name: str,
        pool_manager: Any,
        server_repo: str,
    ) -> Tuple[bool, str, str]:
        """
        Executes complete evaluation:
        1. Clones from local git bare repo to temporary sandbox.
        2. Identifies if submission is a program or a function.
        3. Compiles student code and reference code with test harnesses.
        4. Runs test suite with timeout and comparisons.
        5. Returns: (passed_bool, status_reason, trace_filepath)
        """
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        os.makedirs(self.temp_dir, exist_ok=True)

        # Clone from git server
        repo_path = server_repo.replace("\\", "/")
        clone_res = subprocess.run(
            ["git", "clone", repo_path, self.temp_dir], capture_output=True, text=True
        )
        if clone_res.returncode != 0:
            trace_path = self.write_trace(
                exercise_name, "Git Clone Error", clone_res.stderr
            )
            return False, "Git error (nothing pushed or clone failed)", trace_path

        # Locate student code
        student_file = os.path.join(self.temp_dir, exercise_name, f"{exercise_name}.c")
        if not os.path.exists(student_file):
            # Check root of student repo just in case
            alt_student_file = os.path.join(self.temp_dir, f"{exercise_name}.c")
            if os.path.exists(alt_student_file):
                student_file = alt_student_file
            else:
                trace_path = self.write_trace(
                    exercise_name,
                    "Nothing turned in",
                    f"Expected file at: rendu/{exercise_name}/{exercise_name}.c\nPlease git add, commit, and push your file.",
                )
                return False, "Nothing turned in", trace_path

        # Get reference files from pool manager (in-memory)
        ref_files = pool_manager.get_files_dict(exam_name, exercise_dir)

        # Write reference files and headers into sandbox
        sandbox_dir = tempfile.mkdtemp(prefix="moulinette_eval_")
        try:
            # Write student file to sandbox
            stud_src = os.path.join(sandbox_dir, "student.c")
            shutil.copy(student_file, stud_src)

            # Write reference C file
            ref_c_content = ref_files.get(f"{exercise_name}.c") or ref_files.get(
                f"{exercise_name.replace('-', '_')}.c"
            )
            if not ref_c_content:
                # Find any .c file that isn't main.c
                for fname, fbytes in ref_files.items():
                    if fname.endswith(".c") and fname != "main.c":
                        ref_c_content = fbytes
                        break

            ref_src = os.path.join(sandbox_dir, "ref.c")
            with open(ref_src, "wb") as f:
                f.write(ref_c_content if ref_c_content else b"")

            # Write extra headers or files (e.g. list.h, main.c)
            for fname, fbytes in ref_files.items():
                if fname not in [
                    f"{exercise_name}.c",
                    "subject.en.txt",
                    "subject.fr.txt",
                    "subject.txt",
                ]:
                    extra_path = os.path.join(sandbox_dir, fname)
                    with open(extra_path, "wb") as f:
                        f.write(fbytes)

            # Check if standalone main.c exists in pool
            has_pool_main = "main.c" in ref_files
            has_custom_harness = exercise_name in FUNCTION_HARNESSES

            # Determine whether student file has its own main()
            with open(stud_src, "r", encoding="utf-8", errors="ignore") as f:
                stud_code_text = f.read()
            student_has_main = (
                "main(" in stud_code_text or "main (" in stud_code_text
            ) and not "// int main" in stud_code_text

            stud_bin = os.path.join(sandbox_dir, "stud_bin")
            ref_bin = os.path.join(sandbox_dir, "ref_bin")

            extra_compile_files = []
            if "list.h" in ref_files:
                pass  # list.h will be included via #include "list.h"

            # Case A: Exercise has harness or pool main.c (It is a FUNCTION)
            if has_pool_main or (has_custom_harness and not student_has_main):
                # Write main harness
                main_src = os.path.join(sandbox_dir, "test_main.c")
                if has_pool_main:
                    with open(main_src, "wb") as f:
                        f.write(ref_files["main.c"])
                else:
                    with open(main_src, "w", encoding="utf-8") as f:
                        f.write(FUNCTION_HARNESSES[exercise_name])

                # Compile Student
                stud_ok, stud_err = self._compile_c(
                    stud_src, [main_src], stud_bin, sandbox_dir
                )
                if not stud_ok:
                    trace_path = self.write_trace(
                        exercise_name, "Compilation Error", stud_err
                    )
                    return False, "Compilation error", trace_path

                # Compile Reference
                ref_ok, ref_err = self._compile_c(
                    ref_src, [main_src], ref_bin, sandbox_dir
                )
                if not ref_ok:
                    # Fallback: if reference failed with harness, compile student standalone
                    pass

                # Run test harness
                stud_run_ok, stud_out, stud_code, stud_run_err = self._run_binary(
                    stud_bin, [], sandbox_dir, timeout=4.0
                )
                if not stud_run_ok:
                    trace_path = self.write_trace(
                        exercise_name, "Execution Crash / Timeout", stud_run_err
                    )
                    return False, stud_run_err, trace_path

                ref_run_ok, ref_out, ref_code, ref_run_err = self._run_binary(
                    ref_bin, [], sandbox_dir, timeout=4.0
                )

                if stud_out == ref_out and stud_code == ref_code:
                    return True, "SUCCESS", ""
                else:
                    diff_detail = f"Exit code - Student: {stud_code}, Expected: {ref_code}\nStderr: {stud_run_err}"
                    trace_path = self.write_trace(
                        exercise_name,
                        "Wrong Output (Harness Failed)",
                        diff_detail,
                        stud_out,
                        ref_out,
                    )
                    return False, "Wrong output", trace_path

            # Case B: Standalone PROGRAM (runs with argc/argv test matrix)
            else:
                # Compile Student
                stud_ok, stud_err = self._compile_c(stud_src, [], stud_bin, sandbox_dir)
                if not stud_ok:
                    trace_path = self.write_trace(
                        exercise_name, "Compilation Error", stud_err
                    )
                    return False, "Compilation error", trace_path

                # Compile Reference
                ref_ok, ref_err = self._compile_c(ref_src, [], ref_bin, sandbox_dir)
                if not ref_ok:
                    # If reference has no main, try testing with generic harness
                    pass

                # Run through test vector matrix
                for test_args in PROGRAM_ARG_TESTS:
                    s_ok, s_out, s_code, s_err = self._run_binary(
                        stud_bin, test_args, sandbox_dir, timeout=3.0
                    )
                    if not s_ok:
                        trace_path = self.write_trace(
                            exercise_name,
                            "Execution Crash / Timeout",
                            f"Failed with args: {test_args}\n{s_err}",
                        )
                        return False, s_err, trace_path

                    r_ok, r_out, r_code, r_err = self._run_binary(
                        ref_bin, test_args, sandbox_dir, timeout=3.0
                    )

                    if s_out != r_out or s_code != r_code:
                        arg_desc = f"Failed with arguments: {test_args}\nExit code: Student {s_code} vs Expected {r_code}"
                        trace_path = self.write_trace(
                            exercise_name, "Wrong Output", arg_desc, s_out, r_out
                        )
                        return (
                            False,
                            f"Wrong output on test args: {test_args}",
                            trace_path,
                        )

                return True, "SUCCESS", ""

        finally:
            shutil.rmtree(sandbox_dir, ignore_errors=True)
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
