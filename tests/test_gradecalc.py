import os
import subprocess
import sys
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import gradecalc  # noqa: E402


class GradeMath(unittest.TestCase):
    def setUp(self):
        self.course = gradecalc.load(os.path.join(ROOT, "assets", "course.json"))

    def test_current_standing(self):
        earned, graded, upcoming = gradecalc.course_state(self.course)
        self.assertAlmostEqual(graded + upcoming, 100.0)
        self.assertAlmostEqual(100 * earned / graded, 78.1, places=1)

    def test_a_unreachable(self):
        earned, _, upcoming = gradecalc.course_state(self.course)
        self.assertLess(earned + upcoming, 90)

    def test_skip_costs_points(self):
        base = gradecalc.final_pct(self.course)
        alt = gradecalc.final_pct(self.course, skip={"HW 5"})
        self.assertGreater(base - alt, 4.0)

    def test_perfect_scores(self):
        scores = {"HW 4": 100, "HW 5": 100, "Final": 100}
        self.assertAlmostEqual(gradecalc.final_pct(self.course, scores=scores), 89.5, places=1)


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-I", os.path.join(ROOT, "scripts", "gradecalc.py"), *args],
                              capture_output=True, text=True)

    def test_sample_modes(self):
        for cmd in ("need", "what-if", "triage"):
            r = self.run_cli(cmd, "--sample")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(r.stdout.strip())

    def test_triage_orders_by_value(self):
        out = self.run_cli("triage", "--sample").stdout.splitlines()
        self.assertIn("Quiz 6", out[1])

    def test_bad_file(self):
        r = self.run_cli("need", "missing.json")
        self.assertEqual(r.returncode, 1)
        self.assertIn("Bad input", r.stderr)


if __name__ == "__main__":
    unittest.main()
