"""
Run the full workflow without Click argument parsing.
"""

import argparse
import sys

from .workflow import run_workflow_steps


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the tex-tailor workflow for a job description."
    )
    parser.add_argument("job_description", help="Path to job description file")
    args = parser.parse_args()

    try:
        run_workflow_steps(args.job_description)
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
