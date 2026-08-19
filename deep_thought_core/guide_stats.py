# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    guide_stats.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: RQS_42 <RQS_42@student.42.fr>            +#+  +:+       +#+           #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/19 00:28:54 by RQS_42           #+#    #+#               #
#    Updated: 2026/08/19 00:28:54 by RQS_42          ###   ########.fr         #
#                                                                              #
# **************************************************************************** #

"""
Statistics and Session Archive Manager for 42 Exam Simulator.
Provides session recording, structured archiving per exam (archives/<ExamName>/session_...),
and comprehensive pool completion tracking with terminal dashboards.
"""

import os
import sys
import json
import time
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional

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
    progress_bar,
    print_header,
    print_info,
    print_success,
    print_warning,
)


class SessionRecorder:
    """Tracks the state of a single exam session in real time."""

    def __init__(self, base_dir: str, exam_name: str, login_id: str = "pisciner"):
        self.base_dir = base_dir
        self.exam_name = exam_name
        self.login_id = login_id
        self.start_dt = datetime.now()
        self.timestamp_str = self.start_dt.strftime("%Y%m%d_%H%M%S")
        self.session_id = f"session_{self.timestamp_str}"
        self.exercises_history: List[Dict[str, Any]] = []
        self.final_score = 0
        self.passed = False
        self.end_dt = None

    def record_exercise(
        self,
        level: int,
        exercise_dir: str,
        exercise_name: str,
        status: str,
        attempts: int,
        points_earned: int,
    ):
        self.exercises_history.append(
            {
                "level": level,
                "exercise_dir": exercise_dir,
                "exercise_name": exercise_name,
                "status": status,  # "SUCCESS", "FAILURE", "ABORTED"
                "attempts": attempts,
                "points_earned": points_earned,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def finish(self, final_score: int, passed: bool):
        self.final_score = final_score
        self.passed = passed
        self.end_dt = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        end_time = self.end_dt or datetime.now()
        duration_sec = int((end_time - self.start_dt).total_seconds())
        return {
            "session_id": self.session_id,
            "exam": self.exam_name,
            "login": self.login_id,
            "start_time": self.start_dt.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration_sec,
            "duration_formatted": f"{duration_sec // 60}m {duration_sec % 60}s",
            "final_score": self.final_score,
            "max_score": 100,
            "passed": self.passed,
            "exercises": self.exercises_history,
        }


class StatsManager:
    """
    Manages archives organized by exam and computes aggregated statistics.
    """

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.archives_dir = os.path.join(base_dir, "subetha_archives")
        os.makedirs(self.archives_dir, exist_ok=True)
        self._migrate_legacy_archives()

    def _migrate_legacy_archives(self):
        """Migrates legacy flat 'archives/session_X' folders to 'archives/Legacy/'."""
        if not os.path.exists(self.archives_dir):
            return

        legacy_items = [
            d
            for d in os.listdir(self.archives_dir)
            if os.path.isdir(os.path.join(self.archives_dir, d))
            and d.startswith("session_")
        ]
        if legacy_items:
            legacy_dest = os.path.join(self.archives_dir, "Legacy")
            os.makedirs(legacy_dest, exist_ok=True)
            for item in legacy_items:
                src = os.path.join(self.archives_dir, item)
                dst = os.path.join(legacy_dest, item)
                try:
                    shutil.move(src, dst)
                except Exception:
                    pass

    def archive_current_workspace(
        self, exam_name: str, session_recorder: Optional[SessionRecorder] = None
    ):
        """
        Archives current rendu/, subjects/, and trace/ into:
        archives/<exam_name>/session_YYYYMMDD_HHMMSS/
        """
        rendu_dir = os.path.join(self.base_dir, "rendu")
        subjects_dir = os.path.join(self.base_dir, "subjects")
        trace_dir = os.path.join(self.base_dir, "trace")

        has_content = (
            (os.path.exists(rendu_dir) and bool(os.listdir(rendu_dir)))
            or (os.path.exists(subjects_dir) and bool(os.listdir(subjects_dir)))
            or (os.path.exists(trace_dir) and bool(os.listdir(trace_dir)))
        )

        if not has_content and not session_recorder:
            return None

        exam_archive_dir = os.path.join(
            self.archives_dir, exam_name if exam_name else "Unknown"
        )
        os.makedirs(exam_archive_dir, exist_ok=True)

        if session_recorder:
            sess_folder_name = session_recorder.session_id
        else:
            sess_folder_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        sess_dir = os.path.join(exam_archive_dir, sess_folder_name)
        os.makedirs(sess_dir, exist_ok=True)

        # Move active folders
        if os.path.exists(rendu_dir):
            shutil.move(rendu_dir, os.path.join(sess_dir, "rendu"))
        if os.path.exists(subjects_dir):
            shutil.move(subjects_dir, os.path.join(sess_dir, "subjects"))
        if os.path.exists(trace_dir):
            shutil.move(trace_dir, os.path.join(sess_dir, "trace"))

        # Save session metadata json
        if session_recorder:
            meta_path = os.path.join(sess_dir, "session.json")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(session_recorder.to_dict(), f, indent=2)

        return sess_dir

    def save_session_record(self, exam_name: str, session_recorder: SessionRecorder):
        """Saves or updates session.json inside the session archive."""
        exam_archive_dir = os.path.join(self.archives_dir, exam_name)
        sess_dir = os.path.join(exam_archive_dir, session_recorder.session_id)
        os.makedirs(sess_dir, exist_ok=True)
        meta_path = os.path.join(sess_dir, "session.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(session_recorder.to_dict(), f, indent=2)

    def load_all_sessions(self) -> List[Dict[str, Any]]:
        """Loads all session records across all exams."""
        sessions = []
        if not os.path.exists(self.archives_dir):
            return sessions

        for exam_folder in sorted(os.listdir(self.archives_dir)):
            exam_path = os.path.join(self.archives_dir, exam_folder)
            if not os.path.isdir(exam_path) or exam_folder.startswith("."):
                continue
            for sess_name in sorted(os.listdir(exam_path)):
                sess_path = os.path.join(exam_path, sess_name)
                if not os.path.isdir(sess_path):
                    continue
                meta_path = os.path.join(sess_path, "session.json")
                if os.path.isfile(meta_path):
                    try:
                        with open(meta_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if "exam" not in data:
                                data["exam"] = exam_folder
                            sessions.append(data)
                    except Exception:
                        pass
        return sessions

    def get_aggregated_stats(self, pool_manager) -> Dict[str, Any]:
        """
        Computes detailed stats per exam and globally:
        - Total pool exercises vs solved / attempted
        - Success rate and best score
        - List of solved & remaining exercises
        """
        sessions = self.load_all_sessions()
        exams = pool_manager.list_exams()

        stats_per_exam = {}
        global_unique_solved = set()
        global_unique_attempted = set()
        total_pool_all_exams = 0

        for exam in exams:
            pool_exos = pool_manager.get_all_exercises(exam)
            # Pool exercises directory names or names
            clean_pool_exos = []
            for ex in pool_exos:
                clean_name = ex.split("-", 1)[1] if "-" in ex else ex
                clean_pool_exos.append((ex, clean_name))

            total_pool_all_exams += len(clean_pool_exos)

            solved_set = set()
            attempted_set = set()
            exam_sessions = [s for s in sessions if s.get("exam") == exam]

            best_score = 0
            passed_count = 0

            for sess in exam_sessions:
                score = sess.get("final_score", 0)
                if score > best_score:
                    best_score = score
                if sess.get("passed", False) or score >= 75:
                    passed_count += 1
                for ex in sess.get("exercises", []):
                    ex_name = ex.get("exercise_name")
                    attempted_set.add(ex_name)
                    if ex.get("status") == "SUCCESS":
                        solved_set.add(ex_name)
                        global_unique_solved.add(f"{exam}:{ex_name}")
                    global_unique_attempted.add(f"{exam}:{ex_name}")

            all_clean_names = [c[1] for c in clean_pool_exos]
            remaining = [name for name in all_clean_names if name not in solved_set]

            total_count = len(clean_pool_exos)
            solved_count = len(solved_set)
            completion_pct = (
                (solved_count / total_count * 100.0) if total_count > 0 else 0.0
            )

            stats_per_exam[exam] = {
                "total_pool": total_count,
                "attempted_count": len(attempted_set),
                "solved_count": solved_count,
                "completion_pct": completion_pct,
                "total_sessions": len(exam_sessions),
                "passed_sessions": passed_count,
                "best_score": best_score,
                "all_exercises": all_clean_names,
                "solved_exercises": sorted(list(solved_set)),
                "unsolved_exercises": sorted(remaining),
                "sessions": exam_sessions,
            }

        global_completion = (
            (len(global_unique_solved) / total_pool_all_exams * 100.0)
            if total_pool_all_exams > 0
            else 0.0
        )

        return {
            "exams": stats_per_exam,
            "global_total_pool": total_pool_all_exams,
            "global_solved_count": len(global_unique_solved),
            "global_attempted_count": len(global_unique_attempted),
            "global_completion_pct": global_completion,
            "total_sessions_count": len(sessions),
            "recent_sessions": sorted(
                sessions, key=lambda s: s.get("start_time", ""), reverse=True
            )[:5],
        }

    def render_dashboard(self, pool_manager):
        """Prints a rich, formatted terminal dashboard."""
        stats = self.get_aggregated_stats(pool_manager)

        print(
            f"\n{COLOR_42_TEAL}{BOLD}╔═══════════════════════════════════════════════════════════════════════╗{RESET}"
        )
        print(
            f"{COLOR_42_TEAL}{BOLD}║{WHITE}              📊 42 PISCINE PROGRESSION & EXAM DASHBOARD               {COLOR_42_TEAL}║{RESET}"
        )
        print(
            f"{COLOR_42_TEAL}{BOLD}╚═══════════════════════════════════════════════════════════════════════╝{RESET}\n"
        )

        # Global Summary Card
        print(f"{COLOR_NEON_BLUE}{BOLD}◆ GLOBAL SUMMARY{RESET}")
        print(
            f"  • Total Sessions Played : {BOLD}{stats['total_sessions_count']}{RESET}"
        )
        print(
            f"  • Unique Exos Mastered  : {GREEN}{BOLD}{stats['global_solved_count']}{RESET} / {stats['global_total_pool']}"
        )
        print(
            f"  • Total Pool Mastery    : {progress_bar(stats['global_solved_count'], stats['global_total_pool'], width=25, color=COLOR_42_TEAL)}"
        )
        print()

        # Per-Exam Overview
        print(f"{COLOR_NEON_BLUE}{BOLD}◆ PROGRESSION PER EXAM{RESET}")
        print(f"{COLOR_DARK_GRAY}{'─' * 74}{RESET}")
        print(
            f"{BOLD}  {'EXAM':<10} {'POOL':<7} {'SOLVED':<8} {'PROGRESSION':<32} {'BEST':<8} {'SESSIONS'}{RESET}"
        )
        print(f"{COLOR_DARK_GRAY}{'─' * 74}{RESET}")

        for exam, data in stats["exams"].items():
            bar = progress_bar(
                data["solved_count"],
                data["total_pool"],
                width=10,
                color=GREEN if data["completion_pct"] >= 75 else YELLOW,
            )
            best_str = (
                f"{data['best_score']}/100" if data["total_sessions"] > 0 else "-"
            )
            pass_str = f"{data['passed_sessions']}/{data['total_sessions']} passed"
            print(
                f"  {CYAN}{BOLD}{exam:<10}{RESET} {str(data['total_pool']):<7} {GREEN}{str(data['solved_count']):<8}{RESET} {bar}   {COLOR_GOLD}{best_str:<8}{RESET} {WHITE}{pass_str}{RESET}"
            )
        print(f"{COLOR_DARK_GRAY}{'─' * 74}{RESET}\n")

        # Detailed Checklist per Exam
        print(f"{COLOR_NEON_BLUE}{BOLD}◆ EXERCISE CHECKLIST DETAILS{RESET}")
        for exam, data in stats["exams"].items():
            print(
                f"\n  {COLOR_42_TEAL}{BOLD}[{exam}]{RESET} ({data['solved_count']}/{data['total_pool']} validated)"
            )
            ex_items = []
            for ex in data["all_exercises"]:
                is_solved = ex in data["solved_exercises"]
                mark = "[✓]" if is_solved else "[ ]"
                color = GREEN if is_solved else COLOR_GRAY
                # Pad text before applying ANSI colors so column spacing is exact
                padded_label = f"{mark} {ex}".ljust(23)
                ex_items.append(f"{color}{padded_label}{RESET}")

            # Print in 3 clean columns
            for i in range(0, len(ex_items), 3):
                row = ex_items[i : i + 3]
                print("    " + "".join(row))

        # Recent Sessions Table
        if stats["recent_sessions"]:
            print(f"\n{COLOR_NEON_BLUE}{BOLD}◆ RECENT SESSIONS HISTORY{RESET}")
            print(f"{COLOR_DARK_GRAY}{'─' * 74}{RESET}")
            print(
                f"{BOLD}  {'DATE & TIME':<18} {'EXAM':<10} {'SCORE':<10} {'STATUS':<12} {'DURATION':<10} {'EXOS'}{RESET}"
            )
            print(f"{COLOR_DARK_GRAY}{'─' * 74}{RESET}")

            for sess in stats["recent_sessions"]:
                dt_str = sess.get("start_time", "")[:16].replace("T", " ")
                exam_str = sess.get("exam", "-")
                score_str = f"{sess.get('final_score', 0)}/100"
                passed = sess.get("passed", False)
                status_str = (
                    f"{GREEN}PASSED{RESET}" if passed else f"{RED}FAILED{RESET}"
                )
                dur_str = sess.get("duration_formatted", "-")
                exos_count = len(sess.get("exercises", []))
                print(
                    f"  {COLOR_GRAY}{dt_str:<18}{RESET} {CYAN}{exam_str:<10}{RESET} {BOLD}{score_str:<10}{RESET} {status_str:<21} {dur_str:<10} {exos_count} attempted"
                )
            print(f"{COLOR_DARK_GRAY}{'─' * 74}{RESET}")

        print(
            f"\n{COLOR_GRAY}All session traces and archives are saved in {CYAN}archives/<ExamName>/session_...{RESET}\n"
        )
