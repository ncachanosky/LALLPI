"""
run_pipeline.py

Runs the full LALLPI 2025 pipeline (01 through 06) in order. Each step
is run as a separate subprocess -- exactly as if you'd typed
`python3 01_build_skeleton.py` etc. yourself -- so behavior is
identical whether you run this or run the numbered scripts one at a
time.

Usage
-----
    python3 run_pipeline.py                  # run all six steps
    python3 run_pipeline.py --from 04        # run steps 04 onward
    python3 run_pipeline.py --only 03        # run just step 03
    python3 run_pipeline.py --list           # show the step list and exit

Stops immediately if any step fails (non-zero exit code) -- later steps
read the previous step's output from data/2025/interim/, so continuing
past a failure would just produce confusing downstream errors.
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

STEPS = [
    "01_build_skeleton.py",
    "02_vparty_prepare.py",
    "03_vparty_merge.py",
    "04_load_external.py",
    "05_build_index.py",
    "06_export_outputs.py",
]


def step_number(script_name: str) -> str:
    """Extract the leading two-digit step number, e.g. '04' from '04_load_external.py'."""
    return script_name.split("_", 1)[0]


def select_steps(steps: list[str], only: str | None, start_from: str | None) -> list[str]:
    if only:
        matches = [s for s in steps if step_number(s) == only.zfill(2)]
        if not matches:
            raise SystemExit(f"No step numbered {only!r} found. Use --list to see valid steps.")
        return matches

    if start_from:
        start_from = start_from.zfill(2)
        matches = [s for s in steps if step_number(s) >= start_from]
        if not matches:
            raise SystemExit(f"No step numbered >= {start_from!r} found. Use --list to see valid steps.")
        return matches

    return steps


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the LALLPI 2025 pipeline.")
    parser.add_argument("--from", dest="start_from", metavar="NN",
                         help="Run from step NN onward (e.g. --from 04)")
    parser.add_argument("--only", dest="only", metavar="NN",
                         help="Run only step NN (e.g. --only 03)")
    parser.add_argument("--list", action="store_true",
                         help="List the pipeline steps and exit")
    args = parser.parse_args()

    if args.list:
        for s in STEPS:
            print(s)
        return

    if args.only and args.start_from:
        raise SystemExit("Use either --from or --only, not both.")

    steps_to_run = select_steps(STEPS, args.only, args.start_from)
    script_dir = Path(__file__).resolve().parent

    print(f"Running {len(steps_to_run)} step(s): {', '.join(steps_to_run)}")
    overall_start = time.time()

    for script in steps_to_run:
        script_path = script_dir / script
        print(f"\n{'=' * 60}\n{script}\n{'=' * 60}")

        step_start = time.time()
        result = subprocess.run([sys.executable, str(script_path)], cwd=script_dir)
        step_elapsed = time.time() - step_start

        if result.returncode != 0:
            print(f"\nFAILED at {script} (exit code {result.returncode}, "
                  f"after {step_elapsed:.1f}s). Stopping -- later steps depend on this one's output.")
            sys.exit(result.returncode)

        print(f"({script} completed in {step_elapsed:.1f}s)")

    overall_elapsed = time.time() - overall_start
    print(f"\n{'=' * 60}\nPipeline complete in {overall_elapsed:.1f}s\n{'=' * 60}")


if __name__ == "__main__":
    main()