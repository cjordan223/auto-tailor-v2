"""
Tests for the patcher module.
"""
import unittest
from tex_tailor.patcher import latex_escape, replace_chunk_content


class TestLatexEscape(unittest.TestCase):
    """Test LaTeX escaping functionality."""
    
    def test_basic_escaping(self):
        """Test basic character escaping."""
        test_cases = [
            ("hello world", "hello world"),  # No special chars
            ("test & test", "test \\& test"),  # Ampersand
            ("100% complete", "100\\% complete"),  # Percent
            ("cost $5", "cost \\$5"),  # Dollar sign
            ("test_var", "test\\_var"),  # Underscore
            ("x^2", "x\\textasciicircum{}2"),  # Caret
            ("~/.bashrc", "\\textasciitilde{}/.bashrc"),  # Tilde
            ("{brackets}", "\\{brackets\\}"),  # Braces
            ("path\\file.txt", "path\\textbackslash{}file.txt"),  # Backslash
            ("#hashtag", "\\#hashtag"),  # Hash
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = latex_escape(input_text)
                self.assertEqual(result, expected)
    
    def test_empty_input(self):
        """Test escaping empty or None input."""
        self.assertEqual(latex_escape(""), "")
        self.assertEqual(latex_escape(None), None)
    
    def test_combined_special_chars(self):
        """Test escaping multiple special characters."""
        input_text = "Price: $10 & up (100% guaranteed!) ~user/file.txt"
        expected = "Price: \\$10 \\& up (100\\% guaranteed!) \\textasciitilde{}user/file.txt"
        result = latex_escape(input_text)
        self.assertEqual(result, expected)
    
    def test_latex_command_preservation(self):
        """Test that LaTeX commands are preserved and not escaped."""
        test_cases = [
            ("\\noindent Hello team,", "\\noindent Hello team,"),  # noindent command
            ("\\textbf{Bold text}", "\\textbf\\{Bold text\\}"),  # textbf with braces
            ("\\noindent Hello & welcome", "\\noindent Hello \\& welcome"),  # Command + special chars
            ("Some text\\\\new line", "Some text\\\\new line"),  # Line break command
            ("\\vspace{10pt}", "\\vspace\\{10pt\\}"),  # vspace command
            ("Price: $5 \\textit{italic} text", "Price: \\$5 \\textit\\{italic\\} text"),  # Mixed content
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = latex_escape(input_text)
                self.assertEqual(result, expected)


class TestChunkReplacement(unittest.TestCase):
    """Test chunk content replacement functionality."""
    
    def setUp(self):
        """Set up test content with chunks."""
        self.test_content = """% === LLM:CHUNK START TEST.CHUNK1 ===
Original content here
with multiple lines
% === LLM:CHUNK END TEST.CHUNK1 ===

Some other content

% === LLM:CHUNK START TEST.CHUNK2 ===
Another chunk content
% === LLM:CHUNK END TEST.CHUNK2 ==="""
    
    def test_simple_replacement(self):
        """Test simple chunk replacement."""
        new_content = "New content"
        result = replace_chunk_content(self.test_content, "TEST.CHUNK1", new_content)
        
        self.assertIn("New content", result)
        self.assertNotIn("Original content here", result)
        self.assertIn("Another chunk content", result)  # Other chunks unchanged
    
    def test_special_character_escaping(self):
        """Test that special characters are escaped in replacement."""
        new_content = "Price: $10 & up"
        result = replace_chunk_content(self.test_content, "TEST.CHUNK1", new_content)
        
        self.assertIn("Price: \\$10 \\& up", result)
    
    def test_nonexistent_chunk(self):
        """Test replacement of nonexistent chunk."""
        original = self.test_content
        result = replace_chunk_content(self.test_content, "NONEXISTENT", "new content")
        
        # Should return original content unchanged
        self.assertEqual(result, original)
    
    def test_multiline_replacement(self):
        """Test replacement with multiline content."""
        new_content = "Line 1\nLine 2\nLine 3"
        result = replace_chunk_content(self.test_content, "TEST.CHUNK2", new_content)
        
        self.assertIn("Line 1", result)
        self.assertIn("Line 2", result)
        self.assertIn("Line 3", result)


if __name__ == '__main__':
    unittest.main()