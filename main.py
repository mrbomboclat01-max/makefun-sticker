#!/usr/bin/env python3
"""make.fun sticker: Terminal Agent — copies pre-rendered entry.png to /output"""

import os
import shutil
from pathlib import Path

out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
out_dir.mkdir(parents=True, exist_ok=True)
shutil.copy(Path(__file__).parent / "entry.png", out_dir / "entry.png")
