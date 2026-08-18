#!/usr/bin/env python3
import os
import sys
import random
import time
import subprocess
import shutil

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Globals
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POOL_DIR = os.path.join(BASE_DIR, 'pool')
SUBJECTS_DIR = os.path.join(BASE_DIR, 'subjects')
SERVER_REPO = os.path.join(BASE_DIR, 'server', 'rendu.git')
RENDU_DIR = os.path.join(BASE_DIR, 'rendu')
GRADEME_TEMP = os.path.join(BASE_DIR, 'grademe_temp')

# Globals for Exam state
SELECTED_EXAM = None
levels_dict = {}
LEVELS = []
current_level_idx = 0
current_exercise_dir = None
current_exercise = None
points = 0

def build_levels():
    global levels_dict, LEVELS
    exam_path = os.path.join(POOL_DIR, SELECTED_EXAM)
    levels_dict = {}
    
    for d in os.listdir(exam_path):
        d_path = os.path.join(exam_path, d)
        if os.path.isdir(d_path) and '-' in d:
            lvl_str = d.split('-')[0]
            if lvl_str.isdigit():
                lvl = int(lvl_str)
                if lvl not in levels_dict:
                    levels_dict[lvl] = []
                levels_dict[lvl].append(d)
                
    LEVELS = sorted(levels_dict.keys())

def init_workspace():
    # Setup server bare repo
    if os.path.exists(os.path.join(BASE_DIR, 'server')):
        shutil.rmtree(os.path.join(BASE_DIR, 'server'), ignore_errors=True)
    os.makedirs(SERVER_REPO)
    subprocess.run(['git', 'init', '--bare'], cwd=SERVER_REPO, capture_output=True)
    
    # Archive previous workspace if it exists
    ARCHIVES_DIR = os.path.join(BASE_DIR, 'archives')
    os.makedirs(ARCHIVES_DIR, exist_ok=True)
    
    if os.path.exists(RENDU_DIR) or os.path.exists(SUBJECTS_DIR):
        session_id = 1
        while os.path.exists(os.path.join(ARCHIVES_DIR, f"session_{session_id}")):
            session_id += 1
        sess_dir = os.path.join(ARCHIVES_DIR, f"session_{session_id}")
        os.makedirs(sess_dir)
        
        if os.path.exists(RENDU_DIR):
            shutil.move(RENDU_DIR, os.path.join(sess_dir, 'rendu'))
        if os.path.exists(SUBJECTS_DIR):
            shutil.move(SUBJECTS_DIR, os.path.join(sess_dir, 'subjects'))
        if os.path.exists(os.path.join(BASE_DIR, 'trace')):
            shutil.move(os.path.join(BASE_DIR, 'trace'), os.path.join(sess_dir, 'trace'))
            
    os.makedirs(SUBJECTS_DIR, exist_ok=True)
    
    # Clone locally for the user
    repo_path = SERVER_REPO.replace('\\', '/')
    subprocess.run(['git', 'clone', repo_path, RENDU_DIR], capture_output=True)

def pick_exercise(level_num):
    if level_num not in levels_dict:
        return None
    exercises = levels_dict[level_num]
    if not exercises:
        return None
    return random.choice(exercises)

def intro_animation():
    os.system('cls' if os.name == 'nt' else 'clear')
    art = [
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
        r"                                                                         "
    ]
    import math
    
    print("\n")
    for _ in art:
        print()
        
    sys.stdout.write('\033[?25l') # Masque le curseur
    
    frames = 45
    for frame in range(frames):
        sys.stdout.write(f"\033[{len(art)}A")
        
        output = ""
        for y, line in enumerate(art):
            for x, char in enumerate(line):
                if char == ' ':
                    output += ' '
                    continue
                # Onde Miami Vice (Cyan / Pink / Purple)
                wave = math.sin(x * 0.1 - frame * 0.2 + y * 0.1)
                r = int((wave * 0.5 + 0.5) * 100 + 155)
                g = int((-wave * 0.5 + 0.5) * 200 + 55)
                b = 255
                
                output += f"\033[38;2;{r};{g};{b}m{char}"
            output += "\033[0m\n"
        sys.stdout.write(output)
        sys.stdout.flush()
        time.sleep(0.04)
        
    sys.stdout.write('\033[?25h') # Réaffiche le curseur
    
    print(f"\n\033[38;2;0;255;255m\033[1m=========================================================================\033[0m")
    print(f"\033[38;2;0;255;255m                      42 PISCINE EXAM SIMULATOR                          \033[0m")
    print(f"\033[38;2;0;255;255m\033[1m=========================================================================\033[0m\n")

def login():
    intro_animation()
    
    login_id = input(f"login: ")
    import getpass
    getpass.getpass(f"Password: ")
    print(f"{YELLOW}Connecting to grading server...{RESET}")
    time.sleep(1.5)
    print(f"{GREEN}Connected!{RESET}\n")
    
    print(f"{CYAN}Available Exams:{RESET}")
    exams = [d for d in os.listdir(POOL_DIR) if os.path.isdir(os.path.join(POOL_DIR, d)) and not d.startswith('.')]
    exams.sort()
    for i, ex in enumerate(exams):
        print(f"  {i+1}. {ex}")
    
    while True:
        try:
            choice = int(input(f"Select exam [1-{len(exams)}]: "))
            if 1 <= choice <= len(exams):
                global SELECTED_EXAM
                SELECTED_EXAM = exams[choice-1]
                break
        except ValueError:
            pass
            
    print(f"\n{YELLOW}Initializing {SELECTED_EXAM}...{RESET}")
    build_levels()
    
    print(f"{YELLOW}Setting up your exam environment...{RESET}")
    init_workspace()
    
    print(f"{GREEN}Environment ready!{RESET}")
    print(f"I have automatically created your {CYAN}rendu/{RESET} and {CYAN}subjects/{RESET} folders.")
    
    import platform
    if platform.system() == 'Darwin': # macOS
        subprocess.Popen(['open', '-a', 'Terminal', BASE_DIR])
        print(f"\n{BOLD}A work terminal has been opened for you.{RESET}")
    elif platform.system() == 'Linux':
        try:
            subprocess.Popen(['gnome-terminal', '--working-directory=' + BASE_DIR])
            print(f"\n{BOLD}A work terminal has been opened for you.{RESET}")
        except FileNotFoundError:
            pass
    elif os.name == 'nt':
        subprocess.Popen(['start', 'powershell', '-NoExit', '-Command', f"cd '{BASE_DIR}'"], shell=True)
        print(f"\n{BOLD}A work terminal has been opened for you.{RESET}")
        
    print("\nType 'status' to get your first assignment.\n")

def print_help():
    print(f"{BOLD}Available commands:{RESET}")
    print("  status   - View current exam status and get assignment")
    print("  subject  - View current assignment subject")
    print("  grademe  - Grade your code")
    print("  finish   - End the exam")

def assign_exercise():
    global current_exercise_dir, current_exercise
    if current_level_idx >= len(LEVELS):
        print(f"{GREEN}You have finished the exam!{RESET}")
        return
        
    level_num = LEVELS[current_level_idx]
    current_exercise_dir = pick_exercise(level_num)
    
    if current_exercise_dir is None:
        print(f"{RED}Error loading exercises.{RESET}")
        return
        
    # Extract actual exercise name by splitting on first '-'
    if '-' in current_exercise_dir:
        current_exercise = current_exercise_dir.split('-', 1)[1]
    else:
        current_exercise = current_exercise_dir
        
    # Create user subject folder and copy subject
    user_sub_dir = os.path.join(SUBJECTS_DIR, current_exercise)
    os.makedirs(user_sub_dir, exist_ok=True)
    
    # Try finding subject.fr.txt or subject.en.txt or subject.txt
    src_sub = None
    for sub_name in ['subject.fr.txt', 'subject.en.txt', 'subject.txt', 'sub.txt']:
        p = os.path.join(POOL_DIR, SELECTED_EXAM, current_exercise_dir, sub_name)
        if os.path.exists(p):
            src_sub = p
            break
            
    if src_sub:
        shutil.copy(src_sub, os.path.join(user_sub_dir, 'subject.txt'))
        
    # Create rendu folder
    user_rendu_dir = os.path.join(RENDU_DIR, current_exercise)
    os.makedirs(user_rendu_dir, exist_ok=True)
    
    print(f"\n{GREEN}=============================================={RESET}")
    print(f"{BOLD}NEW ASSIGNMENT: {current_exercise}{RESET}")
    print(f"{GREEN}=============================================={RESET}")
    print(f"Subject has been created in: {CYAN}subjects/{current_exercise}/subject.txt{RESET}")
    print(f"Write your code in: {CYAN}rendu/{current_exercise}/{current_exercise}.c{RESET}\n")
    print(f"When you are done, open your work terminal and type:")
    print(f"{YELLOW}  cd rendu")
    print(f"  git add {current_exercise}")
    print(f"  git commit -m \"pushing {current_exercise}\"")
    print(f"  git push{RESET}\n")
    print(f"Then type {BOLD}grademe{RESET} here.\n")

def print_status():
    global current_exercise
    if current_exercise is None:
        assign_exercise()
    else:
        print(f"Level: {current_level_idx}")
        print(f"Points: {points}")
        print(f"Current Assignment: {BOLD}{current_exercise}{RESET}")
        print(f"Write your code in: {CYAN}rendu/{current_exercise}/{current_exercise}.c{RESET}")

def print_subject():
    if current_exercise is None:
        print("No assignment active. Use 'status'.")
        return
    sub_path = os.path.join(SUBJECTS_DIR, current_exercise, 'subject.txt')
    if os.path.exists(sub_path):
        with open(sub_path, 'r', encoding='utf-8', errors='ignore') as f:
            print(f"\n{f.read()}\n")
    else:
        print("Subject file not found.")

def compile_and_run(source_c, main_c, out_bin):
    cmd = ['gcc', '-Wall', '-Wextra', '-Werror', source_c]
    if main_c:
        cmd.append(main_c)
    cmd.extend(['-o', out_bin])
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        # If it's a function without main, gcc will fail linking. Try compiling as object file.
        if "main" in res.stderr or "undefined reference" in res.stderr:
            res_obj = subprocess.run(['gcc', '-Wall', '-Wextra', '-Werror', '-c', source_c], capture_output=True, text=True)
            if res_obj.returncode == 0:
                return True, "[FUNCTION_ONLY_NO_MAIN]"
        return False, res.stderr
        
    test_args = [[], ['test'], ['a', 'b', 'c'], ['123', '456']]
    outputs = []
    
    out_exe = out_bin
    if os.name == 'nt' and not out_bin.endswith('.exe'):
        out_exe += '.exe'
        
    for args in test_args:
        run_cmd = [out_exe] + args
        r = subprocess.run(run_cmd, capture_output=True, text=True)
        outputs.append(f"Args: {args}\nOut: {r.stdout}\nErr: {r.stderr}\nCode: {r.returncode}")
        
    return True, "\n---\n".join(outputs)

def write_trace(exercise, reason, stud_out, ref_out):
    trace_dir = os.path.join(BASE_DIR, 'trace')
    os.makedirs(trace_dir, exist_ok=True)
    trace_file = os.path.join(trace_dir, f"{exercise}_trace.txt")
    with open(trace_file, 'w', encoding='utf-8') as f:
        f.write(f"--- TRACE FOR {exercise} ---\n")
        f.write(f"REASON: {reason}\n\n")
        if stud_out:
            f.write(f"--- STUDENT OUTPUT / ERROR ---\n{stud_out}\n\n")
        if ref_out:
            f.write(f"--- EXPECTED OUTPUT ---\n{ref_out}\n")
    print(f"A trace has been generated in {CYAN}trace/{exercise}_trace.txt{RESET}")

def grade_exercise():
    global current_exercise, current_level_idx, points
    if current_exercise is None:
        print("No assignment active.")
        return

    confirm = input("Are you sure you want to grademe? (y/N) ")
    if confirm.lower() != 'y':
        return

    print(f"\n{YELLOW}Wait, grading in progress...{RESET}")
    time.sleep(2)

    if os.path.exists(GRADEME_TEMP):
        shutil.rmtree(GRADEME_TEMP, ignore_errors=True)
    
    repo_path = SERVER_REPO.replace('\\', '/')
    subprocess.run(['git', 'clone', repo_path, GRADEME_TEMP], capture_output=True)
    
    student_file = os.path.join(GRADEME_TEMP, current_exercise, f"{current_exercise}.c")
    if not os.path.exists(student_file):
        print(f"{RED}=> FAILURE: Nothing turned in!{RESET}")
        write_trace(current_exercise, "Nothing turned in", None, None)
        return
        
    ex_dir = os.path.join(POOL_DIR, SELECTED_EXAM, current_exercise_dir)
    
    main_c = os.path.join(ex_dir, "main.c")
    has_main = os.path.exists(main_c)
    ref_c = os.path.join(ex_dir, f"{current_exercise}.c")
    
    stud_bin = os.path.join(GRADEME_TEMP, "student_bin")
    stud_ok, stud_out = compile_and_run(student_file, main_c if has_main else None, stud_bin)
    
    if not stud_ok:
        print(f"{RED}=> FAILURE: Compilation error!{RESET}")
        write_trace(current_exercise, "Compilation error", stud_out, None)
        return
        
    ref_bin = os.path.join(GRADEME_TEMP, "ref_bin")
    ref_ok, ref_out = compile_and_run(ref_c, main_c if has_main else None, ref_bin)
    
    if stud_out == ref_out:
        print(f"{GREEN}=> SUCCESS!{RESET}")
        points += 15
        current_level_idx += 1
        current_exercise = None
        if current_level_idx >= len(LEVELS):
            print(f"\n{GREEN}{BOLD}CONGRATULATIONS! You passed the exam!{RESET}")
            sys.exit(0)
        else:
            print(f"\nType {BOLD}status{RESET} to get your next assignment.")
    else:
        print(f"{RED}=> FAILURE: Wrong output!{RESET}")
        write_trace(current_exercise, "Wrong output (diff failed)", stud_out, ref_out)

def shell():
    while True:
        try:
            cmd = input(f"\n{CYAN}examshell>{RESET} ").strip().lower()
            if not cmd:
                continue
            if cmd == 'help':
                print_help()
            elif cmd == 'status':
                print_status()
            elif cmd == 'subject':
                print_subject()
            elif cmd == 'grademe':
                grade_exercise()
            elif cmd == 'finish':
                confirm = input("Are you sure you want to finish the exam? (y/N) ")
                if confirm.lower() == 'y':
                    print("Exiting...")
                    break
            else:
                print(f"Unknown command. Type 'help'.")
        except (KeyboardInterrupt, EOFError):
            print("\nType 'finish' to exit.")
            break
            
if __name__ == "__main__":
    login()
    shell()
