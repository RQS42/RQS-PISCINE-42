# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    build_pool.py                                      :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: RQS_42 <RQS_42@student.42.fr>            +#+  +:+       +#+           #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/19 00:28:54 by RQS_42           #+#    #+#               #
#    Updated: 2026/08/19 00:28:54 by RQS_42          ###   ########.fr         #
#                                                                              #
# **************************************************************************** #

import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from deep_thought_core.babel_crypto import PoolManager, encrypt_bytes

# Clean reference solutions for all exercises
C_SOLUTIONS = {
    "ft_putstr": """#include <unistd.h>
void ft_putstr(char *str) {
    int i = 0;
    while (str && str[i]) {
        write(1, &str[i], 1);
        i++;
    }
}
""",
    "aff_first_param": """#include <unistd.h>
int main(int argc, char **argv) {
    if (argc > 1) {
        int i = 0;
        while (argv[1][i]) {
            write(1, &argv[1][i], 1);
            i++;
        }
    }
    write(1, "\\n", 1);
    return 0;
}
""",
    "repeat_alpha": """#include <unistd.h>
int main(int argc, char **argv) {
    if (argc == 2) {
        int i = 0;
        while (argv[1][i]) {
            char c = argv[1][i];
            int count = 1;
            if (c >= 'a' && c <= 'z') count = c - 'a' + 1;
            else if (c >= 'A' && c <= 'Z') count = c - 'A' + 1;
            while (count--) write(1, &c, 1);
            i++;
        }
    }
    write(1, "\\n", 1);
    return 0;
}
""",
    "search_and_replace": """#include <unistd.h>
int main(int argc, char **argv) {
    if (argc == 4 && argv[2][0] && !argv[2][1] && argv[3][0] && !argv[3][1]) {
        int i = 0;
        char a = argv[2][0];
        char b = argv[3][0];
        while (argv[1][i]) {
            char c = (argv[1][i] == a) ? b : argv[1][i];
            write(1, &c, 1);
            i++;
        }
    }
    write(1, "\\n", 1);
    return 0;
}
""",
    "alpha_mirror": """#include <unistd.h>
int main(int argc, char **argv) {
    if (argc == 2) {
        int i = 0;
        while (argv[1][i]) {
            char c = argv[1][i];
            if (c >= 'a' && c <= 'z') c = 'z' - (c - 'a');
            else if (c >= 'A' && c <= 'Z') c = 'Z' - (c - 'A');
            write(1, &c, 1);
            i++;
        }
    }
    write(1, "\\n", 1);
    return 0;
}
""",
    "ft_strcpy": """char *ft_strcpy(char *s1, char *s2) {
    int i = 0;
    while (s2 && s2[i]) {
        s1[i] = s2[i];
        i++;
    }
    s1[i] = '\\0';
    return s1;
}
""",
    "is_power_of_2": """int is_power_of_2(unsigned int n) {
    return (n > 0) && ((n & (n - 1)) == 0);
}
""",
    "max": """int max(int *tab, unsigned int len) {
    if (!tab || len == 0) return 0;
    int m = tab[0];
    for (unsigned int i = 1; i < len; i++) {
        if (tab[i] > m) m = tab[i];
    }
    return m;
}
""",
    "paramsum": """#include <unistd.h>
static void putnbr(int n) {
    if (n >= 10) putnbr(n / 10);
    char c = (n % 10) + '0';
    write(1, &c, 1);
}
int main(int argc, char **argv) {
    (void)argv;
    putnbr(argc - 1);
    write(1, "\\n", 1);
    return 0;
}
""",
    "do_op": """#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    if (argc == 4) {
        int a = atoi(argv[1]);
        int b = atoi(argv[3]);
        char op = argv[2][0];
        if (op == '+') printf("%d\\n", a + b);
        else if (op == '-') printf("%d\\n", a - b);
        else if (op == '*') printf("%d\\n", a * b);
        else if (op == '/' && b != 0) printf("%d\\n", a / b);
        else if (op == '%' && b != 0) printf("%d\\n", a % b);
        else printf("\\n");
    } else {
        printf("\\n");
    }
    return 0;
}
""",
    "str_capitalizer": """#include <unistd.h>
static int is_space(char c) { return (c == ' ' || c == '\\t'); }
int main(int argc, char **argv) {
    if (argc < 2) {
        write(1, "\\n", 1);
        return 0;
    }
    for (int a = 1; a < argc; a++) {
        int i = 0;
        int first = 1;
        while (argv[a][i]) {
            char c = argv[a][i];
            if (is_space(c)) {
                first = 1;
            } else {
                if (first && c >= 'a' && c <= 'z') c = c - 32;
                else if (!first && c >= 'A' && c <= 'Z') c = c + 32;
                first = 0;
            }
            write(1, &c, 1);
            i++;
        }
        write(1, "\\n", 1);
    }
    return 0;
}
""",
    "ft_strcspn": """#include <stddef.h>
size_t ft_strcspn(const char *s, const char *reject) {
    size_t i = 0;
    while (s[i]) {
        size_t j = 0;
        while (reject[j]) {
            if (s[i] == reject[j]) return i;
            j++;
        }
        i++;
    }
    return i;
}
""",
    "epur_str": """#include <unistd.h>
static int is_space(char c) { return (c == ' ' || c == '\\t'); }
int main(int argc, char **argv) {
    if (argc == 2) {
        int i = 0;
        while (is_space(argv[1][i])) i++;
        int space = 0;
        while (argv[1][i]) {
            if (is_space(argv[1][i])) {
                space = 1;
            } else {
                if (space) write(1, " ", 1);
                space = 0;
                write(1, &argv[1][i], 1);
            }
            i++;
        }
    }
    write(1, "\\n", 1);
    return 0;
}
""",
    "expand_str": """#include <unistd.h>
static int is_space(char c) { return (c == ' ' || c == '\\t'); }
int main(int argc, char **argv) {
    if (argc == 2) {
        int i = 0;
        while (is_space(argv[1][i])) i++;
        int space = 0;
        while (argv[1][i]) {
            if (is_space(argv[1][i])) {
                space = 1;
            } else {
                if (space) write(1, "   ", 3);
                space = 0;
                write(1, &argv[1][i], 1);
            }
            i++;
        }
    }
    write(1, "\\n", 1);
    return 0;
}
""",
    "tab_mult": """#include <unistd.h>
static int ft_atoi(char *s) {
    int res = 0;
    while (*s >= '0' && *s <= '9') res = res * 10 + (*s++ - '0');
    return res;
}
static void ft_putnbr(int n) {
    if (n >= 10) ft_putnbr(n / 10);
    char c = (n % 10) + '0';
    write(1, &c, 1);
}
int main(int argc, char **argv) {
    if (argc == 2) {
        int n = ft_atoi(argv[1]);
        for (int i = 1; i <= 9; i++) {
            ft_putnbr(i);
            write(1, " x ", 3);
            ft_putnbr(n);
            write(1, " = ", 3);
            ft_putnbr(i * n);
            write(1, "\\n", 1);
        }
    } else {
        write(1, "\\n", 1);
    }
    return 0;
}
""",
    "hidenp": """#include <unistd.h>
int main(int argc, char **argv) {
    if (argc == 3) {
        int i = 0, j = 0;
        while (argv[1][i] && argv[2][j]) {
            if (argv[1][i] == argv[2][j]) i++;
            j++;
        }
        if (!argv[1][i]) write(1, "1\\n", 2);
        else write(1, "0\\n", 2);
    } else {
        write(1, "\\n", 1);
    }
    return 0;
}
""",
    "add_prime_sum": """#include <unistd.h>
static int ft_atoi(char *s) {
    int r = 0;
    while (*s >= '0' && *s <= '9') {
        r = r * 10 + (*s - '0');
        s++;
    }
    return r;
}
static int is_prime(int n) {
    if (n <= 1) return 0;
    for (int i = 2; i * i <= n; i++) {
        if (n % i == 0) return 0;
    }
    return 1;
}
static void putnbr(int n) {
    if (n >= 10) putnbr(n / 10);
    char c = (n % 10) + '0';
    write(1, &c, 1);
}
int main(int argc, char **argv) {
    if (argc == 2) {
        int n = ft_atoi(argv[1]);
        if (n <= 0) {
            write(1, "0\\n", 2);
            return 0;
        }
        int sum = 0;
        for (int i = 2; i <= n; i++) {
            if (is_prime(i)) sum += i;
        }
        putnbr(sum);
        write(1, "\\n", 1);
    } else {
        write(1, "0\\n", 2);
    }
    return 0;
}
""",
    "fprime": """#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    if (argc == 2) {
        int n = atoi(argv[1]);
        if (n == 1) {
            printf("1\\n");
            return 0;
        }
        if (n <= 0) {
            printf("\\n");
            return 0;
        }
        int factor = 2;
        int first = 1;
        while (n > 1) {
            if (n % factor == 0) {
                if (!first) printf("*");
                printf("%d", factor);
                first = 0;
                n /= factor;
            } else {
                factor++;
            }
        }
        printf("\\n");
    } else {
        printf("\\n");
    }
    return 0;
}
""",
    "ft_rrange": """#include <stdlib.h>
int *ft_rrange(int start, int end) {
    int len = (end >= start) ? (end - start + 1) : (start - end + 1);
    int *tab = (int *)malloc(sizeof(int) * len);
    if (!tab) return NULL;
    int step = (end >= start) ? -1 : 1;
    int cur = end;
    for (int i = 0; i < len; i++) {
        tab[i] = cur;
        cur += step;
    }
    return tab;
}
""",
    "ft_list_size": """#include "list.h"
int ft_list_size(t_list *begin_list) {
    int count = 0;
    while (begin_list) {
        count++;
        begin_list = begin_list->next;
    }
    return count;
}
""",
    "ft_split": """#include <stdlib.h>
static int is_space(char c) {
    return (c == ' ' || c == '\\t' || c == '\\n');
}
static int count_words(char *str) {
    int count = 0;
    while (*str) {
        while (*str && is_space(*str)) str++;
        if (*str && !is_space(*str)) {
            count++;
            while (*str && !is_space(*str)) str++;
        }
    }
    return count;
}
static char *extract_word(char *str) {
    int len = 0;
    while (str[len] && !is_space(str[len])) len++;
    char *word = (char *)malloc(sizeof(char) * (len + 1));
    if (!word) return NULL;
    for (int i = 0; i < len; i++) word[i] = str[i];
    word[len] = '\\0';
    return word;
}
char **ft_split(char *str) {
    if (!str) return NULL;
    int words = count_words(str);
    char **tab = (char **)malloc(sizeof(char *) * (words + 1));
    if (!tab) return NULL;
    int j = 0;
    while (*str) {
        while (*str && is_space(*str)) str++;
        if (*str && !is_space(*str)) {
            tab[j] = extract_word(str);
            j++;
            while (*str && !is_space(*str)) str++;
        }
    }
    tab[j] = NULL;
    return tab;
}
""",
    "rev_print": """#include <unistd.h>
int main(int argc, char **argv) {
    if (argc == 2) {
        int i = 0;
        while (argv[1][i]) i++;
        while (i > 0) {
            i--;
            write(1, &argv[1][i], 1);
        }
    }
    write(1, "\\n", 1);
    return 0;
}
""",
    "ft_print_numbers": """#include <unistd.h>
void ft_print_numbers(void) {
    char c = '0';
    while (c <= '9') {
        write(1, &c, 1);
        c++;
    }
}
""",
    "sort_list": """#include "list.h"
#include <stdlib.h>
t_list *sort_list(t_list *lst, int (*cmp)(int, int)) {
    if (!lst) return NULL;
    int swapped = 1;
    while (swapped) {
        swapped = 0;
        t_list *cur = lst;
        while (cur && cur->next) {
            int a = *(int *)cur->data;
            int b = *(int *)cur->next->data;
            if (!cmp(a, b)) {
                void *tmp = cur->data;
                cur->data = cur->next->data;
                cur->next->data = tmp;
                swapped = 1;
            }
            cur = cur->next;
        }
    }
    return lst;
}
""",
}

def main():
    pm = PoolManager(BASE_DIR)
    raw_dict = {}
    for exam, exercises in pm._data_cache.items():
        raw_dict[exam] = {}
        for ex_dir, files in exercises.items():
            raw_dict[exam][ex_dir] = {}
            for fname, content in files.items():
                raw_dict[exam][ex_dir][fname] = content.decode("utf-8", errors="ignore")

    # Fix any renamed dirs (e.g. str-maxlenoc -> str_maxlenoc)
    if "Exam03" in raw_dict and "14-str-maxlenoc" in raw_dict["Exam03"]:
        raw_dict["Exam03"]["14-str_maxlenoc"] = raw_dict["Exam03"].pop("14-str-maxlenoc")

    # Inject / update clean solutions
    for exam, ex_dict in raw_dict.items():
        for ex_dir, files in ex_dict.items():
            ex_name = ex_dir.split("-", 1)[1] if "-" in ex_dir else ex_dir
            if ex_name in C_SOLUTIONS:
                c_fname = f"{ex_name}.c"
                files[c_fname] = C_SOLUTIONS[ex_name]

    # Save to pool.enc
    payload_json = json.dumps(raw_dict).encode("utf-8")
    enc_bytes = encrypt_bytes(payload_json)
    enc_path = os.path.join(BASE_DIR, "data", "ultimate_question_pool.enc")
    with open(enc_path, "wb") as f:
        f.write(enc_bytes)

    print(f"Pool updated: {sum(len(v) for v in raw_dict.values())} exercises in container.")

if __name__ == "__main__":
    main()
