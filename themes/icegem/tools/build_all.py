"""Rebuild all IceGem variants and validate the generated CUR/ANI files."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
for name in ("IceBlue", "Violet", "RosePink", "Mint", "Amber"):
    folder = ROOT / "variants" / name
    print(f"Building {name}", flush=True)
    for script in ("build.py", "validate.py"):
        subprocess.run([sys.executable, str(folder / "tools" / script)], check=True)
