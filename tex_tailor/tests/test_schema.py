"""
Tests for the schema validation module.
"""
import unittest
from tex_tailor.schema import (
    validate_json_schema, check_forbidden_latex, 
    validate_summary_edits, validate_skills_edits,
    validate_cover_letter_edits, validate_edits
)


class TestForbiddenLatex(unittest.TestCase):
    """Test LaTeX pattern detection."""
    
    def test_clean_text(self):
        """Test text with no forbidden patterns."""
        text = "This is clean text with normal punctuation."
        violations = check_forbidden_latex(text)
        self.assertEqual(violations, [])
    
    def test_forbidden_patterns(self):
        """Test detection of forbidden LaTeX patterns."""
        test_cases = [
            ("\\section{Test}", r"\\"),
            ("test{braces}", r"\{"),
            ("test}braces", r"\}"),
            ("100% done", r"%"),
            ("test_underscore", r"_"),
            ("x^2 formula", r"\^"),
            ("~/.bashrc", r"~"),
            ("\\begin{document}", r"\\begin"),
            ("\\textbf{bold}", r"\\textbf"),
        ]
        
        for text, expected_pattern in test_cases:
            with self.subTest(text=text):
                violations = check_forbidden_latex(text)
                self.assertTrue(len(violations) > 0)
                self.assertTrue(any(expected_pattern in v for v in violations))


class TestSummaryValidation(unittest.TestCase):
    """Test summary edit validation."""
    
    def test_valid_summary_edit(self):
        """Test valid summary edit."""
        original = "Software engineer with experience."
        new = "Software engineer with extensive experience."
        violations = validate_summary_edits(original, new)
        self.assertEqual(violations, [])
    
    def test_latex_in_summary(self):
        """Test summary with forbidden LaTeX."""
        original = "Software engineer with experience."
        new = "Software engineer with \\textbf{extensive} experience."
        violations = validate_summary_edits(original, new)
        self.assertTrue(len(violations) > 0)
        self.assertTrue(any("forbidden pattern" in v for v in violations))
    
    def test_empty_summary(self):
        """Test empty summary (should be valid)."""
        original = "Some text"
        new = ""
        violations = validate_summary_edits(original, new)
        self.assertEqual(violations, [])


class TestSkillsValidation(unittest.TestCase):
    """Test skills edit validation."""
    
    def test_valid_skills_edit(self):
        """Test valid skills edit."""
        original = "Python, Java, JavaScript"
        new = "Python, Java, TypeScript"
        violations = validate_skills_edits(original, new)
        self.assertEqual(violations, [])
    
    def test_invalid_format(self):
        """Test invalid skills format."""
        original = "Python, Java"
        new = "Python\nJava"  # Not comma-separated
        violations = validate_skills_edits(original, new)
        self.assertTrue(len(violations) > 0)
        self.assertTrue(any("comma-separated" in v for v in violations))


class TestCoverLetterValidation(unittest.TestCase):
    """Test cover letter validation."""
    
    def test_valid_cover_edit(self):
        """Test valid cover letter edit."""
        original = ["Para 1", "Para 2", "Para 3", "Para 4"]
        new = ["New Para 1", None, None, None]  # Only 1 edit
        violations = validate_cover_letter_edits(original, new)
        self.assertEqual(violations, [])
    
    def test_too_many_edits(self):
        """Test too many paragraph edits."""
        original = ["Para 1", "Para 2", "Para 3", "Para 4"]
        new = ["New 1", "New 2", "New 3", None]  # 3 edits (max is 2)
        violations = validate_cover_letter_edits(original, new)
        self.assertTrue(len(violations) > 0)
        self.assertTrue(any("Too many paragraphs" in v for v in violations))
    
    def test_wrong_paragraph_count(self):
        """Test wrong number of paragraphs."""
        original = ["Para 1", "Para 2", "Para 3", "Para 4"]
        new = ["New 1", "New 2"]  # Wrong count
        violations = validate_cover_letter_edits(original, new)
        self.assertTrue(len(violations) > 0)
        self.assertTrue(any("Must have exactly 4" in v for v in violations))


class TestJsonSchemaValidation(unittest.TestCase):
    """Test JSON schema validation."""
    
    def test_valid_edits_json(self):
        """Test valid edits JSON structure."""
        edits = {
            "summary": {"replace": "New summary"},
            "skills": {
                "Programming Languages": {"replace": "Python, Java"},
                "Frontend": {"replace": None},
                "Backend": {"replace": None},
                "Cloud & DevOps": {"replace": None},
                "AI & LLM Tools": {"replace": None},
                "Automation & Productivity": {"replace": None},
                "Security & Operating Systems": {"replace": None},
                "Databases": {"replace": None}
            },
            "cover_letter": {
                "paragraphs": [None, "New paragraph", None, None]
            }
        }
        
        # Should not raise an exception
        try:
            validate_json_schema(edits)
        except Exception:
            self.fail("Valid JSON schema should not raise exception")
    
    def test_invalid_json_structure(self):
        """Test invalid JSON structure."""
        edits = {
            "summary": "Invalid format",  # Should be object with "replace" key
            "skills": {},
            "cover_letter": {"paragraphs": []}
        }
        
        with self.assertRaises(Exception):
            validate_json_schema(edits)
    
    def test_missing_required_fields(self):
        """Test missing required fields."""
        edits = {
            "summary": {"replace": "New summary"}
            # Missing skills and cover_letter
        }
        
        with self.assertRaises(Exception):
            validate_json_schema(edits)


if __name__ == '__main__':
    unittest.main()