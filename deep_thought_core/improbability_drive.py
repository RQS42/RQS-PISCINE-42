# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    improbability_drive.py                             :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: RQS_42 <RQS_42@student.42.fr>            +#+  +:+       +#+           #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/19 00:28:54 by RQS_42           #+#    #+#               #
#    Updated: 2026/08/19 00:28:54 by RQS_42          ###   ########.fr         #
#                                                                              #
# **************************************************************************** #

"""
Exam Engine and Interactive Shell for 42 Exam Simulator.
Manages exam state machine, assignments, git workspace lifecycle,
interactive commands (status, subject, grademe, stats, finish), and grading flow.
"""

import os
import sys
import time
import random
try:
    import readline
except ImportError:
    readline = None
import subprocess
import shutil
import getpass
from typing import Optional, List, Dict, Tuple, Set

from deep_thought_core.babel_crypto import PoolManager
from deep_thought_core.guide_stats import StatsManager, SessionRecorder
from deep_thought_core.moulinette_vogon_auditor import Moulinette
from deep_thought_core.sirius_cybernetics_ui import (
    RESET,
    BOLD,
    DIM,
    GREEN,
    RED,
    YELLOW,
    CYAN,
    WHITE,
    COLOR_42_TEAL,
    COLOR_NEON_BLUE,
    COLOR_NEON_PINK,
    COLOR_GOLD,
    COLOR_GRAY,
    COLOR_DARK_GRAY,
    render_intro_animation,
    print_header,
    print_success,
    print_failure,
    print_warning,
    print_info,
    open_work_terminal,
    progress_bar,
)

# Progression schedule per Exam: List of (level_number, points_awarded) for each step
EXAM_PROGRESSION_SCHEDULE: Dict[str, List[Tuple[int, int]]] = {
    "Exam00": [
        (0, 10),
        (1, 10),
        (1, 10),
        (2, 10),
        (3, 15),
        (4, 15),
        (4, 15),
        (5, 15),
    ],
    "Exam01": [
        (0, 10),
        (1, 10),
        (1, 10),
        (2, 10),
        (2, 10),
        (3, 10),
        (3, 15),
        (4, 10),
        (5, 15),
    ],
    "Exam02": [
        (0, 10),
        (1, 10),
        (2, 10),
        (2, 10),
        (3, 10),
        (3, 10),
        (3, 10),
        (4, 10),
        (5, 10),
        (6, 10),
    ],
    "Exam03": [
        (0, 10),
        (1, 10),
        (2, 10),
        (3, 10),
        (4, 5),
        (5, 5),
        (6, 5),
        (7, 5),
        (8, 5),
        (9, 5),
        (10, 5),
        (11, 5),
        (12, 5),
        (13, 5),
        (14, 5),
        (14, 5),
    ],
}


class ExamEngine:
    """Core exam controller and command interpreter."""

    def __init__(self, base_dir: str):
        self.base_dir = os.path.abspath(base_dir)
        self.subjects_dir = os.path.join(self.base_dir, "subjects")
        self.rendu_dir = os.path.join(self.base_dir, "rendu")
        self.server_repo = os.path.join(self.base_dir, "server", "rendu.git")

        self.pool_manager = PoolManager(self.base_dir)
        self.stats_manager = StatsManager(self.base_dir)
        self.moulinette = Moulinette(self.base_dir)

        self.login_id: str = "pisciner"
        self.selected_exam: Optional[str] = None
        self.levels_dict: Dict[int, List[str]] = {}
        self.levels: List[int] = []
        self.current_level_idx: int = 0
        self.current_exercise_dir: Optional[str] = None
        self.current_exercise: Optional[str] = None
        self.points: int = 0
        self.exercise_attempts: int = 0
        self.session_recorder: Optional[SessionRecorder] = None
        self.is_running: bool = True

    def init_workspace(self):
        """Initializes clean git environment and archives previous work."""
        # Archive previous active session if needed
        self.stats_manager.archive_current_workspace(
            exam_name=self.selected_exam or "Unknown",
            session_recorder=self.session_recorder,
        )

        # Setup server bare git repository
        server_base = os.path.join(self.base_dir, "server")
        if os.path.exists(server_base):
            shutil.rmtree(server_base, ignore_errors=True)
        os.makedirs(self.server_repo, exist_ok=True)
        subprocess.run(
            ["git", "init", "--bare"], cwd=self.server_repo, capture_output=True
        )

        # Clean workspace folders
        for folder in [
            self.rendu_dir,
            self.subjects_dir,
            os.path.join(self.base_dir, "trace"),
        ]:
            if os.path.exists(folder):
                shutil.rmtree(folder, ignore_errors=True)
        os.makedirs(self.subjects_dir, exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "trace"), exist_ok=True)

        # Clone locally for student
        repo_path = self.server_repo.replace("\\", "/")
        subprocess.run(["git", "clone", repo_path, self.rendu_dir], capture_output=True)

    def select_exam_menu(self):
        """Interactive exam selection with stats overview and clean menu navigation."""
        exams = self.pool_manager.list_exams()
        if not exams:
            print_failure("No exams found in pool database!")
            sys.exit(1)

        from deep_thought_core.sirius_cybernetics_ui import clear_screen

        while True:
            clear_screen()
            aggregated = self.stats_manager.get_aggregated_stats(self.pool_manager)

            print(f"\n{COLOR_NEON_BLUE}{BOLD}Available Exams & Options:{RESET}")
            print(f"{COLOR_DARK_GRAY}{'─' * 60}{RESET}")
            for i, ex in enumerate(exams):
                ex_stats = aggregated["exams"].get(ex, {})
                solved = ex_stats.get("solved_count", 0)
                total = ex_stats.get("total_pool", 0)
                best = ex_stats.get("best_score", 0)
                best_str = (
                    f"Best: {best}/100"
                    if ex_stats.get("total_sessions", 0) > 0
                    else "New"
                )
                bar = progress_bar(
                    solved,
                    total,
                    width=10,
                    color=GREEN if solved == total else COLOR_42_TEAL,
                )
                print(
                    f"  {BOLD}{i+1}. {CYAN}{ex:<10}{RESET} {bar} {COLOR_GOLD}{best_str}{RESET}"
                )
            print(
                f"  {BOLD}{len(exams)+1}. {YELLOW}📊 View Full Progression Stats & History{RESET}"
            )
            print(f"  {BOLD}0. {RED}🚪 Exit / Quitter{RESET}")
            print(f"{COLOR_DARK_GRAY}{'─' * 60}{RESET}")

            try:
                choice_str = input(
                    f"{BOLD}Select option [1-{len(exams)+1}, 0 to exit]: {RESET}"
                ).strip()
                if not choice_str:
                    continue
                if choice_str in ["0", "exit", "quit", "q"]:
                    print("\nGood luck with your Piscine! Exiting...")
                    sys.exit(0)

                choice = int(choice_str)
                if choice == len(exams) + 1:
                    self.stats_manager.render_dashboard(self.pool_manager)
                    input(f"\n{BOLD}{CYAN}Press Enter to return to main menu...{RESET}")
                    continue
                if 1 <= choice <= len(exams):
                    self.selected_exam = exams[choice - 1]
                    break
            except (ValueError, EOFError):
                pass
            except KeyboardInterrupt:
                print("\nGood luck with your Piscine! Exiting...")
                sys.exit(0)

            print(
                f"{RED}Invalid choice. Enter 1 to {len(exams)+1} or 0 to exit.{RESET}"
            )

    def setup_exam(self):
        """Builds exam level hierarchy, progression schedule and starts session recorder."""
        self.levels_dict = self.pool_manager.get_exam_levels(self.selected_exam)
        self.levels = sorted(self.levels_dict.keys())

        if self.selected_exam in EXAM_PROGRESSION_SCHEDULE:
            self.schedule = EXAM_PROGRESSION_SCHEDULE[self.selected_exam]
        else:
            total = len(self.levels)
            if total == 0:
                self.schedule = [(0, 100)]
            else:
                base = 100 // total
                rem = 100 % total
                self.schedule = [
                    (lvl, base + (rem if i == total - 1 else 0))
                    for i, lvl in enumerate(self.levels)
                ]

        self.current_step_idx = 0
        self.current_exercise_dir = None
        self.current_exercise = None
        self.points = 0
        self.exercise_attempts = 0
        self.session_solved: Set[str] = set()

        self.session_recorder = SessionRecorder(
            self.base_dir, self.selected_exam, self.login_id
        )
        self.init_workspace()

    def pick_next_exercise(self, level_num: int) -> Optional[str]:
        """Picks an exercise for the level, prioritizing unsolved ones for practice."""
        exercises = self.levels_dict.get(level_num, [])
        if not exercises:
            return None

        # Exclude exercises already solved in the CURRENT session
        unsolved_in_session = [
            ex
            for ex in exercises
            if (ex.split("-", 1)[1] if "-" in ex else ex) not in self.session_solved
        ]

        # Check previously solved exercises across historical sessions to prioritize variety
        agg = self.stats_manager.get_aggregated_stats(self.pool_manager)
        exam_data = agg["exams"].get(self.selected_exam, {})
        solved_names = set(exam_data.get("solved_exercises", []))

        candidates = [
            ex
            for ex in unsolved_in_session
            if (ex.split("-", 1)[1] if "-" in ex else ex) not in solved_names
        ]
        if candidates:
            return random.choice(candidates)
        if unsolved_in_session:
            return random.choice(unsolved_in_session)
        return random.choice(exercises)

    def get_level_points(self, step_idx: Optional[int] = None) -> int:
        """Returns the point value for a specific step in the exam schedule."""
        if step_idx is None:
            step_idx = self.current_step_idx
        if 0 <= step_idx < len(self.schedule):
            return self.schedule[step_idx][1]
        return 10

    def assign_exercise(self):
        """Assigns current level exercise and creates subject/rendu directories."""
        if self.current_step_idx >= len(self.schedule) or self.points >= 100:
            print(f"\n{GREEN}{BOLD}🎉 You have completed the exam!{RESET}")
            return

        level_num = self.schedule[self.current_step_idx][0]
        self.current_exercise_dir = self.pick_next_exercise(level_num)
        self.exercise_attempts = 0

        if not self.current_exercise_dir:
            print_failure("Error picking exercise from pool.")
            return

        if "-" in self.current_exercise_dir:
            self.current_exercise = self.current_exercise_dir.split("-", 1)[1]
        else:
            self.current_exercise = self.current_exercise_dir

        # Write subject
        subject_text = self.pool_manager.get_subject_text(
            self.selected_exam, self.current_exercise_dir
        )
        user_sub_dir = os.path.abspath(os.path.join(self.subjects_dir, self.current_exercise))
        if not user_sub_dir.startswith(os.path.abspath(self.subjects_dir)):
            raise ValueError("SECURITY BREACH: Path Traversal detected.")
        os.makedirs(user_sub_dir, exist_ok=True)
        with open(
            os.path.join(user_sub_dir, "subject.txt"), "w", encoding="utf-8"
        ) as f:
            f.write(subject_text)

        # Create user rendu folder
        user_rendu_dir = os.path.abspath(os.path.join(self.rendu_dir, self.current_exercise))
        if not user_rendu_dir.startswith(os.path.abspath(self.rendu_dir)):
            raise ValueError("SECURITY BREACH: Path Traversal detected.")
        os.makedirs(user_rendu_dir, exist_ok=True)

        level_pts = self.get_level_points(self.current_step_idx)

        print(
            f"\n{COLOR_42_TEAL}{BOLD}= Assignment ==================================================================={RESET}"
        )
        print(f"You are currently at {BOLD}Level {level_num}{RESET} (Question {self.current_step_idx + 1}/{len(self.schedule)})")
        print(f"You have been assigned: {CYAN}{BOLD}{self.current_exercise}{RESET}")
        print(f"This assignment is worth: {GREEN}{BOLD}{level_pts} points{RESET}")
        print(f"Current score: {COLOR_GOLD}{BOLD}{self.points} / 100{RESET}")
        print(
            f"Subject file : {CYAN}subjects/{self.current_exercise}/subject.txt{RESET}"
        )
        print(
            f"Turn-in path : {GREEN}{BOLD}rendu/{self.current_exercise}/{self.current_exercise}.c{RESET}"
        )
        print(
            f"{COLOR_42_TEAL}{BOLD}================================================================================{RESET}\n"
        )
        print(
            f"  {YELLOW}When you have written your code, in your work terminal run:{RESET}"
        )
        print(f"  {DIM}$ cd rendu")
        print(f"  $ git add {self.current_exercise}")
        print(f'  $ git commit -m "pushing {self.current_exercise}"')
        print(f"  $ git push{RESET}\n")
        print(f"  Then type {BOLD}{GREEN}grademe{RESET} here to be evaluated.\n")

    def cmd_status(self):
        """Displays current exam status in authentic 42 format."""
        if self.current_exercise is None:
            self.assign_exercise()
        else:
            cur_pts = self.get_level_points(self.current_step_idx)
            level_num = self.schedule[self.current_step_idx][0] if self.current_step_idx < len(self.schedule) else 0
            print(
                f"\n{COLOR_42_TEAL}{BOLD}= Exam Status =================================================================={RESET}"
            )
            print(f"You are currently at level {BOLD}{level_num}{RESET} (Question {self.current_step_idx + 1}/{len(self.schedule)})")
            print(
                f"You are working on the assignment: {CYAN}{BOLD}{self.current_exercise}{RESET}"
            )
            print(
                f"For assignment {self.current_exercise}, the requested file is: {GREEN}{BOLD}{self.current_exercise}.c{RESET} in {GREEN}rendu/{self.current_exercise}/{RESET}"
            )
            print(
                f"Subject path : {CYAN}subjects/{self.current_exercise}/subject.txt{RESET}"
            )
            print(f"Current score: {COLOR_GOLD}{BOLD}{self.points} / 100{RESET}")
            print(f"This assignment is worth: {GREEN}{cur_pts} points{RESET}")
            print(f"Attempts     : {self.exercise_attempts} on this assignment")
            print(
                f"{COLOR_42_TEAL}{BOLD}================================================================================{RESET}\n"
            )

    def cmd_subject(self):
        """Prints current exercise subject with clean styling."""
        if self.current_exercise is None:
            print_warning("No active assignment. Type 'status' first.")
            return

        subject_text = self.pool_manager.get_subject_text(
            self.selected_exam, self.current_exercise_dir
        )
        print(f"\n{COLOR_42_TEAL}{BOLD}╭{'─' * 70}╮{RESET}")
        print(
            f"{COLOR_42_TEAL}{BOLD}│ {WHITE}SUBJECT: {self.current_exercise.ljust(60)} {COLOR_42_TEAL}│{RESET}"
        )
        print(f"{COLOR_42_TEAL}{BOLD}╰{'─' * 70}╯{RESET}\n")
        print(subject_text)
        print(f"\n{COLOR_42_TEAL}{'─' * 72}{RESET}\n")

    def cmd_grademe(self):
        """Grades the current exercise through Moulinette."""
        if self.current_exercise is None:
            print_warning("No assignment active. Type 'status' to get one.")
            return

        confirm = (
            input(
                f"{BOLD}Are you sure you want to push your work to be graded? [y/N]: {RESET}"
            )
            .strip()
            .lower()
        )
        if confirm != "y":
            print("Grading aborted.")
            return

        self.exercise_attempts += 1
        print(
            f"\n{YELLOW}⏳ Wait, Moulinette is fetching your commit from local Vogsphere and evaluating...{RESET}"
        )
        time.sleep(1.2)

        passed, reason, trace_path = self.moulinette.evaluate(
            exam_name=self.selected_exam,
            exercise_dir=self.current_exercise_dir,
            exercise_name=self.current_exercise,
            pool_manager=self.pool_manager,
            server_repo=self.server_repo,
        )

        level_pts = self.get_level_points(self.current_step_idx)

        if passed:
            self.points = min(100, self.points + level_pts)
            self.session_solved.add(self.current_exercise)

            print(f"\n{GREEN}{BOLD}>>>>>>>>>> SUCCESS <<<<<<<<<<{RESET}")
            print(
                f"You have validated the assignment {BOLD}{self.current_exercise}{RESET}!"
            )
            print(f"You earned {GREEN}{BOLD}{level_pts} points{RESET}!")
            print(
                f"Your current score is now: {COLOR_GOLD}{BOLD}{self.points} / 100{RESET}.\n"
            )

            current_lvl = self.schedule[self.current_step_idx][0] if self.current_step_idx < len(self.schedule) else 0
            if self.session_recorder:
                self.session_recorder.record_exercise(
                    level=current_lvl,
                    exercise_dir=self.current_exercise_dir,
                    exercise_name=self.current_exercise,
                    status="SUCCESS",
                    attempts=self.exercise_attempts,
                    points_earned=level_pts,
                )

            self.current_step_idx += 1
            self.current_exercise = None
            self.current_exercise_dir = None

            if self.current_step_idx >= len(self.schedule) or self.points >= 100:
                print(
                    f"{COLOR_GOLD}{BOLD}🏆 CONGRATULATIONS! You have reached {self.points}/100!{RESET}"
                )
                self.cmd_finish(force_exit=True)
            else:
                next_lvl = self.schedule[self.current_step_idx][0]
                next_pts = self.get_level_points(self.current_step_idx)
                print(
                    f"You move on to {BOLD}Level {next_lvl}{RESET} (Question {self.current_step_idx + 1}/{len(self.schedule)}, worth {next_pts} points)!"
                )
                print(
                    f"Type {BOLD}{GREEN}status{RESET} to receive your next assignment.\n"
                )
        else:
            current_lvl = self.schedule[self.current_step_idx][0] if self.current_step_idx < len(self.schedule) else 0
            print(f"\n{RED}{BOLD}>>>>>>>>>> FAILURE <<<<<<<<<<{RESET}")
            print(
                f"You have failed the assignment {BOLD}{self.current_exercise}{RESET}."
            )
            if trace_path:
                rel_trace = os.path.relpath(trace_path, self.base_dir)
                print(f"A trace has been generated in: {CYAN}{rel_trace}{RESET}")

            print(
                f"\nYou are currently at {BOLD}Level {current_lvl}{RESET} with {COLOR_GOLD}{BOLD}{self.points} / 100{RESET} points."
            )
            print(
                f"You can retry this assignment for {GREEN}{level_pts} points{RESET}, or you can finish the exam."
            )
            print(f"Type {BOLD}status{RESET} to review your assignment.\n")

            if self.session_recorder:
                self.session_recorder.record_exercise(
                    level=current_lvl,
                    exercise_dir=self.current_exercise_dir,
                    exercise_name=self.current_exercise,
                    status="FAILURE",
                    attempts=self.exercise_attempts,
                    points_earned=0,
                )

    def cmd_finish(self, force_exit: bool = False):
        """Ends the current exam session, records stats, and archives work."""
        if not force_exit:
            confirm = (
                input(
                    f"{YELLOW}{BOLD}Are you sure you want to finish and submit your exam? (y/N): {RESET}"
                )
                .strip()
                .lower()
            )
            if confirm != "y":
                return

        passed = self.points >= 75
        if self.session_recorder:
            self.session_recorder.finish(self.points, passed)
            archive_path = self.stats_manager.archive_current_workspace(
                self.selected_exam, self.session_recorder
            )
        else:
            archive_path = None

        print(
            f"\n{COLOR_42_TEAL}{BOLD}===================================================={RESET}"
        )
        print(
            f"{WHITE}{BOLD}                 EXAM SESSION FINISHED              {RESET}"
        )
        print(
            f"{COLOR_42_TEAL}{BOLD}===================================================={RESET}"
        )
        print(f"  • Exam         : {CYAN}{BOLD}{self.selected_exam}{RESET}")
        print(f"  • Final Score  : {COLOR_GOLD}{BOLD}{self.points} / 100{RESET}")
        if archive_path:
            print(
                f"  • Archived in  : {CYAN}{os.path.relpath(archive_path, self.base_dir)}{RESET}"
            )
        print(
            f"{COLOR_42_TEAL}{BOLD}===================================================={RESET}\n"
        )

        # Show updated stats
        self.stats_manager.render_dashboard(self.pool_manager)
        self.is_running = False

    def cmd_help(self):
        """Displays available commands."""
        print(f"\n{COLOR_42_TEAL}{BOLD}Available Commands:{RESET}")
        print(
            f"  {GREEN}{BOLD}status{RESET}   - View current level, points, and assignment instructions"
        )
        print(
            f"  {GREEN}{BOLD}subject{RESET}  - Display the subject of your current assignment"
        )
        print(
            f"  {GREEN}{BOLD}grademe{RESET}  - Submit your code to the Moulinette for evaluation"
        )
        print(
            f"  {GREEN}{BOLD}stats{RESET}    - View detailed pool progression & session history"
        )
        print(
            f"  {GREEN}{BOLD}history{RESET}  - View past exam session records and scores"
        )
        print(f"  {GREEN}{BOLD}help{RESET}     - Show this help message")
        print(
            f"  {GREEN}{BOLD}finish{RESET}   - End the exam session and record final results\n"
        )

    def run_login_flow(self):
        """Runs 3-Act CRT Deep Thought animation, login, and authentic 42 system header."""
        render_intro_animation()

        print(
            f"{COLOR_42_TEAL}{BOLD}[EXAMSHELL]{RESET} Deep Thought v42.0 initialized.\n"
        )
        self.login_id = input(f"{BOLD}login: {RESET}").strip() or "pisciner"
        try:
            getpass.getpass(f"{BOLD}Password: {RESET}")
        except Exception:
            pass

        print(
            f"\n{YELLOW}Connecting to Vogsphere (vogsphere.42piscine.offline)...{RESET}"
        )
        time.sleep(0.9)
        print(
            f"{YELLOW}Authenticating with Deep Thought (computing answer: 42)...{RESET}"
        )
        time.sleep(0.8)
        print_success("Connected to Vogsphere-Simulator (Don't Panic)!\n")

        # Authentic 42 System Header
        import socket, platform, datetime

        host = socket.gethostname()
        sys_info = f"{platform.system()} {platform.release()} {platform.machine()}"
        now_str = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")

        print(
            f"{COLOR_DARK_GRAY}= Host-specific information ===================================================={RESET}"
        )
        print(f"$> hostname; uname -msr\n{host} {sys_info}")
        print(f"$> date\n{now_str}")
        print(
            f"{COLOR_DARK_GRAY}================================================================================{RESET}\n"
        )

        print(
            f"{COLOR_42_TEAL}{BOLD}********************************************************************************{RESET}"
        )
        print(
            f"{COLOR_42_TEAL}{BOLD}*                                                                              *{RESET}"
        )
        print(
            f"{COLOR_42_TEAL}{BOLD}*                          {WHITE}Welcome to the ExamShell                            {COLOR_42_TEAL}*{RESET}"
        )
        print(
            f"{COLOR_42_TEAL}{BOLD}*                                                                              *{RESET}"
        )
        print(
            f"{COLOR_42_TEAL}{BOLD}********************************************************************************{RESET}\n"
        )

        self.select_exam_menu()
        print(f"\n{YELLOW}Initializing {self.selected_exam} environment...{RESET}")
        self.setup_exam()
        print_success("Exam environment initialized!")
        print_info(
            f"Workspace initialized: {CYAN}rendu/{RESET} and {CYAN}subjects/{RESET}"
        )

        # Open secondary work terminal
        open_work_terminal(self.base_dir)

        print(f"\nType {BOLD}{GREEN}status{RESET} to get your first assignment.\n")

    def start_shell(self):
        """Main interactive REPL."""
        self.run_login_flow()

        while self.is_running:
            try:
                prompt = (
                    f"{COLOR_42_TEAL}{BOLD}examshell [{self.selected_exam}]>{RESET} "
                )
                cmd = input(prompt).strip().lower()
                if not cmd:
                    continue

                if cmd == "status":
                    self.cmd_status()
                elif cmd == "subject":
                    self.cmd_subject()
                elif cmd == "grademe":
                    self.cmd_grademe()
                elif cmd in ["stats", "history", "profile"]:
                    self.stats_manager.render_dashboard(self.pool_manager)
                elif cmd == "help":
                    self.cmd_help()
                elif cmd in ["finish", "exit", "quit"]:
                    self.cmd_finish()
                else:
                    print(
                        f"{RED}Unknown command '{cmd}'. Type {BOLD}help{RESET} for list of commands.{RESET}"
                    )

            except (KeyboardInterrupt, EOFError):
                print(
                    f"\n{YELLOW}Use 'finish' or 'exit' to cleanly exit the exam.{RESET}"
                )
                try:
                    self.cmd_finish()
                except Exception:
                    break
                break
