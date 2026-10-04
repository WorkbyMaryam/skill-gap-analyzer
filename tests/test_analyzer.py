"""Unit tests (run with:  python -m unittest discover -s tests  or  pytest)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzer import analyze
from src.file_parsers import extract_text
from src.skill_extractor import expand_implied, extract_skills
from src.text_processing import clean_text

RESUME = ("Python, SQL, Pandas, Scikit-learn, Power BI, Machine Learning, statistics. "
          "Built dashboards and automated reports for the sales team over two years of work.")
JD = ("Looking for a Data Analyst with Python, SQL, Tableau, Excel, Power BI, statistics and AWS. "
      "Advanced Excel skills are required for this analytics role in our team.")


class TestExtraction(unittest.TestCase):
    def test_basic_and_boundaries(self):
        s = extract_skills("Experienced in Python, MySQL, NoSQL and JavaScript; not Javascripty things.")
        self.assertIn("Python", s)
        self.assertIn("MySQL", s)
        self.assertIn("NoSQL", s)
        self.assertNotIn("SQL", s)           # 'mysql' / 'nosql' must not match bare SQL
        self.assertIn("JavaScript", s)

    def test_special_characters(self):
        s = extract_skills("Skills: C++, C#, Node.js and .NET")
        for name in ("C++", "C#", "Node.js", ".NET"):
            self.assertIn(name, s)

    def test_case_sensitive_ambiguous(self):
        self.assertNotIn("Rust", extract_skills("the pipes began to rust over time"))
        self.assertIn("Rust", extract_skills("Systems programming in Rust"))
        self.assertNotIn("R", extract_skills("we are happy to go on"))

    def test_importance_weighting(self):
        jd = extract_skills("Requirements:\n- Python\nNice to have:\n- Docker\n- Kafka", weighted=True)
        self.assertEqual(jd["Python"].importance, "required")
        self.assertEqual(jd["Docker"].importance, "preferred")
        self.assertGreater(jd["Python"].weight, jd["Docker"].weight)

    def test_implied(self):
        e = expand_implied(extract_skills("Pandas and Scikit-learn"))
        self.assertTrue(e["Python"].implied)
        self.assertIn("Machine Learning", e)


class TestAnalyze(unittest.TestCase):
    def test_matching_and_missing(self):
        r = analyze(RESUME, JD)
        matched = {m["skill"] for m in r.matching_skills}
        missing = {m["skill"] for m in r.missing_skills}
        self.assertTrue({"Python", "SQL", "Power BI", "Statistics"} <= matched)
        self.assertTrue({"Tableau", "AWS", "Advanced Excel"} <= missing)
        self.assertTrue(0 <= r.score <= 100)
        self.assertIn("Tableau", r.recommendation)

    def test_transferable_flagged(self):
        r = analyze(RESUME, JD)
        tab = next(g for g in r.gaps if g["skill"] == "Tableau")
        self.assertIn("Power BI", tab["transferable_from"])

    def test_perfect_vs_poor_ordering(self):
        good = analyze(JD + " Tableau Excel AWS", JD).score
        poor = analyze("Chef with ten years of experience in restaurant kitchens and menu design for fine dining.", JD).score
        self.assertGreater(good, poor)
        self.assertGreater(good, 80)

    def test_too_short(self):
        with self.assertRaises(ValueError):
            analyze("Python", JD)


class TestUtils(unittest.TestCase):
    def test_clean_text(self):
        self.assertEqual(clean_text("• Python\u200b   SQL\r\n\r\n\r\n\r\nR"), "- Python SQL\n\nR")

    def test_txt_parser_and_bad_ext(self):
        self.assertEqual(extract_text("a.txt", b"hello"), "hello")
        with self.assertRaises(ValueError):
            extract_text("a.exe", b"x")


if __name__ == "__main__":
    unittest.main()
