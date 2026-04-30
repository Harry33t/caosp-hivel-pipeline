"""Replace Unicode chars used by Step 7 with LaTeX-safe equivalents in the
already-stripped tabular .tex files under the manuscript directory."""
from pathlib import Path

DST = Path(r"D:/download_default/tianwen_siluofake/manuscript/tables")

REPLACEMENTS = {
    "∧": r"$\wedge$",   # logical AND
    "∨": r"$\vee$",     # logical OR
    "∩": r"$\cap$",     # set intersection
    "∪": r"$\cup$",     # set union
    "≤": r"$\leq$",     # ≤
    "≥": r"$\geq$",     # ≥
    "−": "$-$",         # Unicode minus
    "×": r"$\times$",   # ×
    "°": r"$^{\circ}$", # °
    "—": "---",         # em dash
    "–": "--",          # en dash
    "…": r"\ldots",     # …
    "±": r"$\pm$",      # ±
    "→": r"$\rightarrow$",
    "←": r"$\leftarrow$",
    "Δ": r"$\Delta$",
    "δ": r"$\delta$",
    "α": r"$\alpha$",
    "β": r"$\beta$",
    "σ": r"$\sigma$",
    "μ": r"$\mu$",
    "ϖ": r"$\varpi$",
    "θ": r"$\theta$",
}

import re

for tex in DST.glob("*.tex"):
    text = tex.read_text(encoding="utf-8")
    orig = text
    for k, v in REPLACEMENTS.items():
        text = text.replace(k, v)
    # Escape stray '%' that pandas didn't escape (pandas to_latex escape=False
    # leaves '%' as a comment char; we must protect it inside cells).
    # Replace '%' that is NOT already preceded by a backslash.
    text = re.sub(r"(?<!\\)%", r"\\%", text)
    if text != orig:
        tex.write_text(text, encoding="utf-8")
        print("patched", tex.name)
    else:
        print("clean", tex.name)
