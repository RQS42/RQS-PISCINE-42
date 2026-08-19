# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    test_stats.py                                      :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: RQS_42 <RQS_42@student.42.fr>            +#+  +:+       +#+           #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/19 00:28:54 by RQS_42           #+#    #+#               #
#    Updated: 2026/08/19 00:28:54 by RQS_42          ###   ########.fr         #
#                                                                              #
# **************************************************************************** #

"""
Unit tests for statistics and archiving per exam.
"""

import os
import sys
import shutil
import tempfile
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from deep_thought_core.babel_crypto import PoolManager
from deep_thought_core.guide_stats import StatsManager, SessionRecorder


class TestStats(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_stats_")
        self.stats_manager = StatsManager(self.temp_dir)
        self.pool_manager = PoolManager(BASE_DIR)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_archive_per_exam_structure(self):
        # Create dummy rendu and subjects in temp_dir
        rendu_path = os.path.join(self.temp_dir, "rendu", "ft_strlen")
        os.makedirs(rendu_path, exist_ok=True)
        with open(os.path.join(rendu_path, "ft_strlen.c"), "w") as f:
            f.write("int ft_strlen(char *s){return 0;}")

        recorder = SessionRecorder(self.temp_dir, "Exam01", "student42")
        recorder.record_exercise(0, "0-only_z", "only_z", "SUCCESS", 1, 15)
        recorder.record_exercise(1, "1-ft_strlen", "ft_strlen", "SUCCESS", 1, 15)
        recorder.finish(final_score=30, passed=False)

        arch_dir = self.stats_manager.archive_current_workspace("Exam01", recorder)
        self.assertTrue(os.path.isdir(arch_dir))
        self.assertIn("Exam01", arch_dir)

        # Verify session.json exists
        json_path = os.path.join(arch_dir, "session.json")
        self.assertTrue(os.path.isfile(json_path))

        # Check aggregated stats
        agg = self.stats_manager.get_aggregated_stats(self.pool_manager)
        exam01_data = agg["exams"]["Exam01"]
        self.assertEqual(exam01_data["total_sessions"], 1)
        self.assertEqual(exam01_data["best_score"], 30)
        self.assertIn("only_z", exam01_data["solved_exercises"])
        self.assertIn("ft_strlen", exam01_data["solved_exercises"])

    def test_exam_progression_schedules(self):
        from deep_thought_core.improbability_drive import ExamEngine, EXAM_PROGRESSION_SCHEDULE
        engine = ExamEngine(BASE_DIR)
        for exam_name, schedule in EXAM_PROGRESSION_SCHEDULE.items():
            total_pts = sum(pts for _, pts in schedule)
            self.assertEqual(total_pts, 100, f"{exam_name} schedule does not sum to 100 points")
            
            engine.selected_exam = exam_name
            engine.login_id = "test_user"
            engine.setup_exam()
            
            # Verify exercises can be picked sequentially
            for lvl, pts in schedule:
                ex = engine.pick_next_exercise(lvl)
                self.assertIsNotNone(ex, f"Failed to pick exercise for {exam_name} level {lvl}")
                ex_name = ex.split("-", 1)[1] if "-" in ex else ex
                engine.session_solved.add(ex_name)


if __name__ == "__main__":
    unittest.main()
