"""
Tests for the extractor module.
"""
import unittest
import tempfile
import os
from tex_tailor.extractor import extract_chunks_from_file, build_base_text_json


class TestChunkExtraction(unittest.TestCase):
    """Test chunk extraction functionality."""
    
    def test_extract_chunks(self):
        """Test extracting chunks from file content."""
        content = """% Some preamble

% === LLM:CHUNK START RESUME.SUMMARY ===
Experienced software engineer with 5 years of development experience.
% === LLM:CHUNK END RESUME.SUMMARY ===

% Some other content

% === LLM:CHUNK START SKILLS.Programming Languages ===
Python, Java, JavaScript, TypeScript
% === LLM:CHUNK END SKILLS.Programming Languages ===

% More content
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            chunks = extract_chunks_from_file(temp_path)
            
            # Check extracted chunks
            self.assertIn("RESUME.SUMMARY", chunks)
            self.assertIn("SKILLS.Programming Languages", chunks)
            
            self.assertEqual(chunks["RESUME.SUMMARY"], 
                           "Experienced software engineer with 5 years of development experience.")
            self.assertEqual(chunks["SKILLS.Programming Languages"],
                           "Python, Java, JavaScript, TypeScript")
            
        finally:
            os.unlink(temp_path)
    
    def test_no_chunks(self):
        """Test file with no chunks."""
        content = """% Just some regular LaTeX content
\\documentclass{article}
\\begin{document}
Hello world
\\end{document}"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            chunks = extract_chunks_from_file(temp_path)
            self.assertEqual(chunks, {})
        finally:
            os.unlink(temp_path)
    
    def test_multiline_chunks(self):
        """Test chunks with multiple lines."""
        content = """% === LLM:CHUNK START TEST.MULTILINE ===
Line 1 of content
Line 2 of content
Line 3 of content
% === LLM:CHUNK END TEST.MULTILINE ==="""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            chunks = extract_chunks_from_file(temp_path)
            expected = "Line 1 of content\nLine 2 of content\nLine 3 of content"
            self.assertEqual(chunks["TEST.MULTILINE"], expected)
        finally:
            os.unlink(temp_path)


class TestBaseTextBuilding(unittest.TestCase):
    """Test building base text JSON structure."""
    
    def test_build_base_text_json(self):
        """Test building complete base text structure."""
        # Create resume file
        resume_content = """% === LLM:CHUNK START RESUME.SUMMARY ===
Software engineer summary
% === LLM:CHUNK END RESUME.SUMMARY ===

% === LLM:CHUNK START SKILLS.Programming Languages ===
Python, Java
% === LLM:CHUNK END SKILLS.Programming Languages ===

% === LLM:CHUNK START SKILLS.Frontend ===
React, Vue.js
% === LLM:CHUNK END SKILLS.Frontend ==="""
        
        # Create cover letter file
        cover_content = """% === LLM:CHUNK START COVER.P1 ===
Dear Hiring Manager,
% === LLM:CHUNK END COVER.P1 ===

% === LLM:CHUNK START COVER.P2 ===
I am writing to express interest.
% === LLM:CHUNK END COVER.P2 ==="""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as resume_f:
            resume_f.write(resume_content)
            resume_path = resume_f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as cover_f:
            cover_f.write(cover_content)
            cover_path = cover_f.name
        
        try:
            base_text = build_base_text_json(resume_path, cover_path)
            
            # Check structure
            self.assertIn("resume", base_text)
            self.assertIn("cover_letter", base_text)
            self.assertIn("meta", base_text)
            
            # Check resume content
            resume = base_text["resume"]
            self.assertEqual(resume["summary"], "Software engineer summary")
            self.assertEqual(resume["skills"]["Programming Languages"], "Python, Java")
            self.assertEqual(resume["skills"]["Frontend"], "React, Vue.js")
            
            # Check cover letter content
            cover = base_text["cover_letter"]
            self.assertEqual(cover["paragraphs"][0], "Dear Hiring Manager,")
            self.assertEqual(cover["paragraphs"][1], "I am writing to express interest.")
            
            # Check metadata
            meta = base_text["meta"]
            self.assertIn("total_editable_chunks", meta)
            self.assertTrue(meta["total_editable_chunks"] > 0)
            
        finally:
            os.unlink(resume_path)
            os.unlink(cover_path)


if __name__ == '__main__':
    unittest.main()