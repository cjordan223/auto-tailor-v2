"""
Module for logging workflow output to files.
"""
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import TextIO, Optional


class WorkflowLogger:
    """Logger that captures all output to both console and log file."""

    def __init__(self, log_file: str = "workflow.log"):
        self.log_file = log_file
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.log_handle: Optional[TextIO] = None
        self.start_time = datetime.now()

    def start(self):
        """Start logging - redirect stdout/stderr to both console and file."""
        # Create log file with timestamp
        timestamp = self.start_time.strftime("%Y-%m-%d_%H-%M-%S")
        log_path = Path(f"workflow_{timestamp}.log")

        # Open log file
        self.log_handle = open(log_path, 'w', encoding='utf-8')

        # Write header
        header = f"""LaTeX Tailor Workflow Log
Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
Working Directory: {Path.cwd()}
{'='*60}

"""
        self.log_handle.write(header)
        self.log_handle.flush()

        # Create custom stdout/stderr that writes to both
        class DualOutput:
            def __init__(self, original_stream, log_handle):
                self.original_stream = original_stream
                self.log_handle = log_handle

            def write(self, text):
                # Write to original stream (console)
                self.original_stream.write(text)
                self.original_stream.flush()

                # Write to log file
                if self.log_handle:
                    self.log_handle.write(text)
                    self.log_handle.flush()

            def flush(self):
                self.original_stream.flush()
                if self.log_handle:
                    self.log_handle.flush()

        # Redirect stdout and stderr
        sys.stdout = DualOutput(self.original_stdout, self.log_handle)
        sys.stderr = DualOutput(self.original_stderr, self.log_handle)

        print(f"📝 Logging started: {log_path}")

    def stop(self):
        """Stop logging and restore original stdout/stderr."""
        if self.log_handle:
            # Write footer
            end_time = datetime.now()
            duration = end_time - self.start_time

            footer = f"""
{'='*60}
Workflow completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
Duration: {duration}
"""
            self.log_handle.write(footer)
            self.log_handle.close()

            # Restore original streams
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr

            print(f"📝 Logging stopped: {self.log_handle.name}")

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


def log_workflow(func):
    """Decorator to automatically log workflow functions."""
    def wrapper(*args, **kwargs):
        with WorkflowLogger():
            return func(*args, **kwargs)
    return wrapper


def get_latest_log() -> Optional[Path]:
    """Get the path to the most recent workflow log file."""
    log_files = list(Path().glob("workflow_*.log"))
    if not log_files:
        return None

    # Return the most recent log file
    return max(log_files, key=lambda p: p.stat().st_mtime)


def show_latest_log():
    """Display the contents of the most recent workflow log."""
    latest_log = get_latest_log()
    if not latest_log:
        print("No workflow logs found.")
        return

    print(f"📋 Latest workflow log: {latest_log}")
    print("=" * 60)

    try:
        with open(latest_log, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
    except Exception as e:
        print(f"Error reading log file: {e}")
