#!/usr/bin/env python3
"""
Simple script to run the tex-tailor init command.
"""
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from tex_tailor.markers import init_files
    print("Running tex-tailor init...")
    init_files()
    print("✓ Initialization complete!")
    print("Files created with LOCK/CHUNK markers and résumé sections reordered.")
except Exception as e:
    print(f"Error during initialization: {e}")
    sys.exit(1)
