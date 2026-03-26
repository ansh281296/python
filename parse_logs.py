"""
parse_logs.py
=============
Practice script for file handling and log parsing.

Reads DFT / synthesis log files, extracts key information
(errors, warnings, result status, metrics) and prints a
summary report.

Sample log files (in the logs/ directory):
  - synthesis_failed.log
  - synthesis_passed_warnings.log
  - dft_failed.log
  - dft_passed_warnings.log

Usage:
  python parse_logs.py
"""

import os
import re


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #

def parse_log_file(filepath):
    """
    Read a single log file and return a dict with:
        filename  - base name of the log file
        errors    - list of error lines
        warnings  - list of warning lines
        result    - 'PASSED' | 'FAILED' | 'UNKNOWN'
        metrics   - dict of any numeric metric lines found

    Expected log format:
        - Error lines   begin with 'Error:'
        - Warning lines begin with 'Warning:'
        - Result status is encoded as 'RESULT: PASSED' or 'RESULT: FAILED'
        - Metric summary lines use the pattern '# <label> : <number>[%]'
          (e.g. '# Errors   : 5' or '# Fault Coverage: 76.95%')
    """
    result = {
        "filename": os.path.basename(filepath),
        "errors": [],
        "warnings": [],
        "result": "UNKNOWN",
        "metrics": {},
    }

    with open(filepath, "r") as fh:
        for line in fh:
            stripped = line.strip()

            # Collect error lines
            if stripped.startswith("Error:"):
                result["errors"].append(stripped)

            # Collect warning lines
            elif stripped.startswith("Warning:"):
                result["warnings"].append(stripped)

            # Detect overall pass/fail
            elif "RESULT: FAILED" in stripped:
                result["result"] = "FAILED"
            elif "RESULT: PASSED" in stripped:
                result["result"] = "PASSED"

            # Extract numeric metrics (lines containing a colon and a number)
            # e.g. "# Errors   : 5"  or  "# Fault Coverage: 76.95%"
            metric_match = re.match(r"#\s+([\w][\w\s-]*?)\s*:\s*([\d.]+%?)", stripped)
            if metric_match:
                key = metric_match.group(1).strip()
                value = metric_match.group(2).strip()
                result["metrics"][key] = value

    return result


def print_summary(parsed):
    """Print a human-readable summary for one parsed log."""
    status_icon = "[PASS]" if parsed["result"] == "PASSED" else (
        "[FAIL]" if parsed["result"] == "FAILED" else "[UNKNOWN]"
    )

    print(f"\n{'=' * 60}")
    print(f"  Log file : {parsed['filename']}")
    print(f"  Result   : {status_icon}  {parsed['result']}")
    print(f"  Errors   : {len(parsed['errors'])}")
    print(f"  Warnings : {len(parsed['warnings'])}")

    if parsed["metrics"]:
        print("  Metrics  :")
        for key, value in parsed["metrics"].items():
            print(f"    {key:<35} {value}")

    if parsed["errors"]:
        print("  Error details:")
        for err in parsed["errors"]:
            print(f"    - {err}")

    if parsed["warnings"]:
        print("  Warning details:")
        for warn in parsed["warnings"]:
            print(f"    - {warn}")

    print(f"{'=' * 60}")


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #

def main():
    # Locate the logs directory relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "logs")

    if not os.path.isdir(logs_dir):
        print(f"ERROR: logs directory not found at '{logs_dir}'")
        return

    # Gather all .log files
    log_files = sorted(
        os.path.join(logs_dir, f)
        for f in os.listdir(logs_dir)
        if f.endswith(".log")
    )

    if not log_files:
        print("No .log files found in the logs/ directory.")
        return

    print(f"\nFound {len(log_files)} log file(s) in '{logs_dir}'")

    passed_count = 0
    failed_count = 0

    for log_path in log_files:
        parsed = parse_log_file(log_path)
        print_summary(parsed)

        if parsed["result"] == "PASSED":
            passed_count += 1
        elif parsed["result"] == "FAILED":
            failed_count += 1

    # Overall summary
    print("\n" + "#" * 60)
    print(f"  OVERALL SUMMARY")
    print(f"  Total log files : {len(log_files)}")
    print(f"  Passed          : {passed_count}")
    print(f"  Failed          : {failed_count}")
    print("#" * 60)


if __name__ == "__main__":
    main()
