#!/usr/bin/env python3
"""Copy entry.png from beside this file to $MAKEFUN_OUTPUT_DIR/entry.png.

Stdlib only. Default output dir is /output/entry.png when the env var is
unset.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
DST = os.path.join(OUT_DIR, "entry.png")

os.makedirs(OUT_DIR, exist_ok=True)
shutil.copyfile(SRC, DST)
print("COPIED", SRC, "->", DST)
