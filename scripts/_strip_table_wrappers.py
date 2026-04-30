"""Helper: strip the outer \\begin{table}...\\end{table} and caption/label
from each LaTeX table in paper/tables/, leaving only the tabular
environment so it can be \\input{} into the manuscript."""
from pathlib import Path
import re

SRC = Path("paper/tables")
DST = Path(r"D:/download_default/tianwen_siluofake/manuscript/tables")
DST.mkdir(parents=True, exist_ok=True)

pat = re.compile(r"(\\begin\{tabular\}.*?\\end\{tabular\})", re.S)
for tex in SRC.glob("*.tex"):
    text = tex.read_text(encoding="utf-8")
    m = pat.search(text)
    if not m:
        print("no tabular in", tex.name)
        continue
    (DST / tex.name).write_text(m.group(1) + "\n", encoding="utf-8")
    print("->", (DST / tex.name).name, "rows=", m.group(1).count(r"\\"))
