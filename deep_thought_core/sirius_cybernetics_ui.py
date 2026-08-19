# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    sirius_cybernetics_ui.py                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: RQS_42 <RQS_42@student.42.fr>            +#+  +:+       +#+           #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/19 00:28:54 by RQS_42           #+#    #+#               #
#    Updated: 2026/08/19 00:28:54 by RQS_42          ###   ########.fr         #
#                                                                              #
# **************************************************************************** #

"""
UI and Terminal Styling Module for 42 Exam Simulator.
Provides Cyberpunk/42-themed TrueColor banners, animations, progress bars,
formatted tables, and cross-platform terminal launcher helpers.
"""

import os
import sys
import time
import math
import platform
import subprocess

# ANSI Colors
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

# Foreground Colors
BLACK = "\033[30m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"

# Background Colors
BG_BLACK = "\033[40m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"


# 42 Themed TrueColor helpers
def rgb(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"


def bg_rgb(r: int, g: int, b: int) -> str:
    return f"\033[48;2;{r};{g};{b}m"


COLOR_42_TEAL = rgb(0, 186, 188)
COLOR_NEON_PINK = rgb(255, 0, 128)
COLOR_NEON_BLUE = rgb(0, 210, 255)
COLOR_NEON_PURPLE = rgb(180, 0, 255)
COLOR_GOLD = rgb(255, 215, 0)
COLOR_GRAY = rgb(130, 130, 130)
COLOR_DARK_GRAY = rgb(70, 70, 70)

ASCII_BANNER = [
    r"                                                                         ",
    r"    ██████╗  ██████╗  ██████╗    ██╗  ██╗██████╗                         ",
    r"    ██╔══██╗██╔═══██╗██╔════╝    ██║  ██║╚════██╗                        ",
    r"    ██████╔╝██║   ██║╚█████╗     ███████║ █████╔╝                        ",
    r"    ██╔══██╗██║▄▄ ██║ ╚═══██╗    ╚════██║██╔═══╝                         ",
    r"    ██║  ██║╚██████╔╝██████╔╝         ██║███████╗                        ",
    r"    ╚═╝  ╚═╝ ╚══▀▀═╝ ╚═════╝          ╚═╝╚══════╝                        ",
    r"                                                                         ",
    r"    █████╗ ██████╗  █████╗ ████████╗██████╗ ███████╗███████╗██╗  ██╗     ",
    r"   ██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗╚══███╔╝██╔════╝██║ ██╔╝     ",
    r"   ███████║██████╔╝███████║   ██║   ██████╔╝  ███╔╝ █████╗  █████╔╝      ",
    r"   ██╔══██║██╔═══╝ ██╔══██║   ██║   ██╔══██╗ ███╔╝  ██╔══╝  ██╔═██╗      ",
    r"   ██║  ██║██║     ██║  ██║   ██║   ██║  ██║███████╗███████╗██║  ██╗     ",
    r"   ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝     ",
    r"                                                                         ",
]

# CRT Computer Frame Elements
CHASSIS_COLOR = "\033[38;2;120;135;155m"
SCREEN_BORDER = "\033[38;2;65;75;95m"
GREEN_OK = "\033[38;2;0;255;150m\033[1m[OK]\033[0m"
GOLD_VAL = "\033[38;2;255;215;0m\033[1m"
CYAN_PROMPT = "\033[38;2;0;220;255m\033[1m"

CRT_FRAME_TOP = f"{CHASSIS_COLOR}  ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ {RESET}"
CRT_BEZEL_TOP1 = f"{CHASSIS_COLOR} █                                                                           █{RESET}"
CRT_BEZEL_TOP2 = f"{CHASSIS_COLOR} █   {SCREEN_BORDER}.-------------------------------------------------------------------.{CHASSIS_COLOR}   █{RESET}"
CRT_BEZEL_BOT = f"{CHASSIS_COLOR} █   {SCREEN_BORDER}'-------------------------------------------------------------------'{CHASSIS_COLOR}   █{RESET}"
CRT_CHASSIS_BOT1 = f"{CHASSIS_COLOR} █                                                                           █{RESET}"
CRT_CHASSIS_BOT2 = f"{CHASSIS_COLOR} █   {BOLD}[■] 42_DECK       [≡] [≡] [≡]                  [○] PWR  {RESET}[\033[38;2;0;255;128m●\033[0m \033[1mONLINE\033[0m{CHASSIS_COLOR}]      █{RESET}"
CRT_CHASSIS_BOT3 = f"{CHASSIS_COLOR} █▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█{RESET}"
CRT_STAND_1 = f"{CHASSIS_COLOR}       \\                                                               /      {RESET}"
CRT_STAND_2 = f"{CHASSIS_COLOR}        \\_____________________________________________________________/       {RESET}"

CRT_LOGO_LINES = [
    "                                                                 ",
    "        ██████╗  ██████╗  ██████╗    ██╗  ██╗██████╗             ",
    "        ██╔══██╗██╔═══██╗██╔════╝    ██║  ██║╚════██╗            ",
    "        ██████╔╝██║   ██║╚█████╗     ███████║ █████╔╝            ",
    "        ██╔══██╗██║▄▄ ██║ ╚═══██╗    ╚════██║██╔═══╝             ",
    "        ██║  ██║╚██████╔╝██████╔╝         ██║███████╗            ",
    "        ╚═╝  ╚═╝ ╚══▀▀═╝ ╚═════╝          ╚═╝╚══════╝            ",
    "                                                                 ",
    "                    P  I  S  C  I  N  E   4 2                    ",
    "                                                                 ",
]


def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def render_screen_line(line_content: str = "") -> str:
    """Formats a single line inside the CRT computer screen (65 chars wide)."""
    return f"{CHASSIS_COLOR} █   {SCREEN_BORDER}|{RESET} {line_content} {SCREEN_BORDER}|{CHASSIS_COLOR}   █{RESET}"


def render_intro_animation(skip_animation: bool = False):
    """
    Renders the retro CRT Deep Thought Computer Boot Sequence in 3 Acts:
    - Act 1: The Machine Awakening & Deep Thought Boot Sequence.
    - Act 2: CRT Wipe, 42 Piscine Logo reveal, and Synthwave TrueColor Wave.
    - Act 3: Frozen neon glow and seamless transition to the login prompt.
    """
    clear_screen()

    if skip_animation:
        # Static CRT render
        print(f"\n{CRT_FRAME_TOP}")
        print(CRT_BEZEL_TOP1)
        print(CRT_BEZEL_TOP2)
        for line in CRT_LOGO_LINES:
            print(render_screen_line(f"{COLOR_42_TEAL}{BOLD}{line}{RESET}"))
        print(CRT_BEZEL_BOT)
        print(CRT_CHASSIS_BOT1)
        print(CRT_CHASSIS_BOT2)
        print(CRT_CHASSIS_BOT3)
        print(CRT_STAND_1)
        print(CRT_STAND_2)
        print()
        return

    sys.stdout.write("\033[?25l")  # Hide cursor
    try:
        # Helper to draw the screen and bottom frame
        def draw_bottom_half(screen_buf):
            for scr_line in screen_buf:
                sys.stdout.write(render_screen_line(scr_line) + "\n")
            sys.stdout.write(CRT_BEZEL_BOT + "\n")
            sys.stdout.write(CRT_CHASSIS_BOT1 + "\n")
            sys.stdout.write(CRT_CHASSIS_BOT2 + "\n")
            sys.stdout.write(CRT_CHASSIS_BOT3 + "\n")
            sys.stdout.write(CRT_STAND_1 + "\n")
            sys.stdout.write(CRT_STAND_2 + "\n")
            sys.stdout.flush()

        # Act 1: Display CRT Computer and boot up sequence
        print(f"\n{CRT_FRAME_TOP}")
        print(CRT_BEZEL_TOP1)
        print(CRT_BEZEL_TOP2)

        current_screen = [" " * 65 for _ in range(10)]
        draw_bottom_half(current_screen)

        # Boot log lines: (line_idx, prefix_ansi, text_to_type, right_tag, delay_after)
        boot_steps = [
            (
                0,
                f"  {CYAN}[SYSTEM]{RESET} ",
                "BOOTING DEEP THOUGHT v42.0...",
                f"{GREEN_OK}     ",
                0.4,
            ),
            (
                1,
                f"  {MAGENTA}[DEEP THOUGHT]{RESET} ",
                "CACHE: 42 TB...",
                f"{GREEN_OK}     ",
                0.4,
            ),
            (
                2,
                f"  {MAGENTA}[DEEP THOUGHT]{RESET} ",
                "PROCESSING ULTIMATE ANSWER...",
                "         ",
                0.5,
            ),
            (
                3,
                f"  {MAGENTA}[DEEP THOUGHT]{RESET} ",
                "RECALCULATING PARAMETERS...",
                "         ",
                0.5,
            ),
            (
                4,
                f"  {CYAN}[SYSTEM]{RESET} ",
                "SIMULATING EXTERNAL INPUT: PISCINE EXAM.",
                "         ",
                0.6,
            ),
            (
                5,
                f"  {MAGENTA}[DEEP THOUGHT]{RESET} ",
                "PROCESSING... (TAKES YEARS OR SECONDS)",
                "         ",
                0.8,
            ),
            (
                7,
                f"  {COLOR_42_TEAL}[PROGRESS]{RESET} ",
                "PROGRESS_BAR",
                "         ",
                0.5,
            ),
            (
                8,
                f"  {CYAN}[CREDITS]{RESET} ",
                "LOADING K11Q/MINI-MOULINETTE LOGIC...",
                f"{GREEN_OK}     ",
                0.3,
            ),
            (
                9,
                f"  {MAGENTA}[DEEP THOUGHT]{RESET} ",
                "INITIALIZING PISCINE PROTOCOL...",
                f"{GREEN}{BOLD}[READY]{RESET}  ",
                1.0,
            ),
        ]

        import re

        for line_idx, prefix, typing_part, right_tag, end_delay in boot_steps:
            clean_prefix = re.sub(r"\x1b\[[0-9;]*m", "", prefix)
            clean_right = re.sub(r"\x1b\[[0-9;]*m", "", right_tag)

            if typing_part == "PROGRESS_BAR":
                bar_width = 32
                for pct in range(0, 101, 2):
                    if pct < 42:
                        time.sleep(0.071)
                    elif pct == 42:
                        time.sleep(1.0)
                    else:
                        time.sleep(0.017)

                    filled = int((pct / 100) * bar_width)
                    bar = "#" * filled + "." * (bar_width - filled)
                    bar_str = f"[{COLOR_42_TEAL}{bar}{RESET}] {pct:3d}%"

                    clean_bar = (
                        f"[{'#' * filled}{'.' * (bar_width - filled)}] {pct:3d}%"
                    )
                    gap_len = max(
                        0, 65 - len(clean_prefix) - len(clean_bar) - len(clean_right)
                    )

                    line_str = (
                        prefix + bar_str + (" " * gap_len) + (" " * len(clean_right))
                    )
                    current_screen[line_idx] = line_str

                    sys.stdout.write("\033[16A")
                    draw_bottom_half(current_screen)
                time.sleep(end_delay)
                continue

            # Typewriter effect character by character
            for i in range(1, len(typing_part) + 1):
                partial_text = typing_part[:i]
                gap_len = max(
                    0, 65 - len(clean_prefix) - len(partial_text) - len(clean_right)
                )

                # We leave the right tag empty while typing, just spaces
                line_str = (
                    prefix + partial_text + (" " * gap_len) + (" " * len(clean_right))
                )
                current_screen[line_idx] = line_str

                sys.stdout.write("\033[16A")  # 10 screen + 6 frame lines
                draw_bottom_half(current_screen)
                time.sleep(0.035)  # slightly slower human typing speed

            # Add the right tag (e.g. [OK] or [READY])
            gap_len = max(
                0, 65 - len(clean_prefix) - len(typing_part) - len(clean_right)
            )
            line_str = prefix + typing_part + (" " * gap_len) + right_tag
            current_screen[line_idx] = line_str

            sys.stdout.write("\033[16A")
            draw_bottom_half(current_screen)
            time.sleep(end_delay)

        # Act 2: CRT Wipe and Logo Synthwave Wave Animation
        time.sleep(0.3)
        # Phosphor screen clear
        sys.stdout.write("\033[16A")
        empty_screen = [" " * 65 for _ in range(10)]
        draw_bottom_half(empty_screen)
        time.sleep(0.15)

        # Synthwave Wave Animation
        frames = 35
        for frame in range(frames):
            sys.stdout.write("\033[16A")
            wave_screen = []
            for y, line in enumerate(CRT_LOGO_LINES):
                colored_line = ""
                for x, char in enumerate(line):
                    if char == " ":
                        colored_line += " "
                        continue
                    wave = math.sin(x * 0.14 - frame * 0.25 + y * 0.18)
                    r = int((wave * 0.5 + 0.5) * 130 + 125)
                    g = int((-wave * 0.5 + 0.5) * 210 + 45)
                    b = 255
                    colored_line += f"\033[38;2;{r};{g};{b}m{char}"
                colored_line += RESET
                wave_screen.append(colored_line)

            # Pulse the LED
            led_color = (
                "\033[38;2;0;255;128m"
                if (frame // 4) % 2 == 0
                else "\033[38;2;0;180;255m"
            )
            dynamic_chassis_bot2 = f"{CHASSIS_COLOR} █   {BOLD}[■] 42_DECK       [≡] [≡] [≡]                  [○] PWR  {RESET}[{led_color}●{RESET} \033[1mONLINE\033[0m{CHASSIS_COLOR}]      █{RESET}"

            # Render frame
            for scr_line in wave_screen:
                sys.stdout.write(render_screen_line(scr_line) + "\n")
            sys.stdout.write(CRT_BEZEL_BOT + "\n")
            sys.stdout.write(CRT_CHASSIS_BOT1 + "\n")
            sys.stdout.write(dynamic_chassis_bot2 + "\n")
            sys.stdout.write(CRT_CHASSIS_BOT3 + "\n")
            sys.stdout.write(CRT_STAND_1 + "\n")
            sys.stdout.write(CRT_STAND_2 + "\n")
            sys.stdout.flush()
            time.sleep(0.035)

    finally:
        # Act 3: Cursor moves below the computer frame, unhides for login
        sys.stdout.write("\033[?25h")  # Show cursor
        sys.stdout.flush()
        print()


def print_header(title: str, subtitle: str = None):
    print(f"\n{COLOR_42_TEAL}{BOLD}╭{'─' * 60}╮{RESET}")
    print(f"{COLOR_42_TEAL}{BOLD}│ {WHITE}{title.center(58)} {COLOR_42_TEAL}│{RESET}")
    if subtitle:
        print(
            f"{COLOR_42_TEAL}{BOLD}│ {COLOR_GRAY}{subtitle.center(58)} {COLOR_42_TEAL}│{RESET}"
        )
    print(f"{COLOR_42_TEAL}{BOLD}╰{'─' * 60}╯{RESET}\n")


def print_success(msg: str):
    print(f"{GREEN}{BOLD}✓ {msg}{RESET}")


def print_failure(msg: str):
    print(f"{RED}{BOLD}✗ {msg}{RESET}")


def print_warning(msg: str):
    print(f"{YELLOW}{BOLD}⚠ {msg}{RESET}")


def print_info(msg: str):
    print(f"{CYAN}{BOLD}ℹ {msg}{RESET}")


def progress_bar(current: int, total: int, width: int = 20, color: str = GREEN) -> str:
    """Returns a formatted ANSI progress bar."""
    if total <= 0:
        pct = 0.0
        filled = 0
    else:
        pct = (current / total) * 100.0
        filled = int((current / total) * width)

    filled = max(0, min(width, filled))
    empty = width - filled

    bar = f"{color}{'█' * filled}{COLOR_DARK_GRAY}{'░' * empty}{RESET}"
    return f"[{bar}] {color}{BOLD}{pct:5.1f}%{RESET} ({current}/{total})"


def open_work_terminal(base_dir: str):
    """
    Opens a separate work terminal window cleanly across macOS, Linux, and Windows.
    """
    current_os = platform.system()
    try:
        if current_os == "Darwin":  # macOS
            # AppleScript to open Terminal in directory
            script = (
                f'tell application "Terminal" to do script "cd {base_dir} && clear"'
            )
            subprocess.Popen(
                ["osascript", "-e", script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(
                f"\n{GREEN}✓{RESET} {BOLD}A work terminal has been opened for you on macOS.{RESET}"
            )
        elif (
            current_os == "Linux"
        ):  # Linux (GNOME / x-terminal-emulator / konsole / xterm)
            terminal_launched = False
            for term in [
                "gnome-terminal",
                "x-terminal-emulator",
                "konsole",
                "xfce4-terminal",
                "xterm",
            ]:
                if shutil_which(term):
                    if term == "gnome-terminal":
                        subprocess.Popen(
                            ["gnome-terminal", f"--working-directory={base_dir}"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                    elif term == "x-terminal-emulator":
                        subprocess.Popen(
                            ["x-terminal-emulator", f"--working-directory={base_dir}"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                    else:
                        subprocess.Popen(
                            [term],
                            cwd=base_dir,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                    terminal_launched = True
                    break
            if terminal_launched:
                print(
                    f"\n{GREEN}✓{RESET} {BOLD}A work terminal has been opened for you on Linux.{RESET}"
                )
        elif os.name == "nt" or current_os == "Windows":  # Windows
            subprocess.Popen(
                ["start", "powershell", "-NoExit", "-Command", f"cd '{base_dir}'"],
                shell=True,
            )
            print(
                f"\n{GREEN}✓{RESET} {BOLD}A work terminal has been opened for you on Windows (PowerShell).{RESET}"
            )
    except Exception as e:
        print_warning(f"Could not automatically open a work terminal: {e}")
        print(f"Please open a second terminal manually and 'cd {base_dir}'.")


def shutil_which(cmd: str) -> bool:
    import shutil

    return shutil.which(cmd) is not None
