"""Run all four studies in sequence. See README.md."""
import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))

for study in ["sn_radial.py", "tails_1d.py", "born_rule.py", "no_signaling.py"]:
    print(f"\n===== {study} =====")
    r = subprocess.run([sys.executable, os.path.join(HERE, "src", study)],
                       cwd=os.path.join(HERE, "src"))
    if r.returncode != 0:
        sys.exit(f"{study} failed with exit code {r.returncode}")
print("\nAll studies completed. See figures/ and results/.")
