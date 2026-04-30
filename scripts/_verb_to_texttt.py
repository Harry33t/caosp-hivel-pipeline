"""Replace \\verb|...| with \\texttt{...} in the manuscript so the long
identifiers can break across lines (verb cannot)."""
import re
from pathlib import Path

P = Path(r"D:/download_default/tianwen_siluofake/manuscript/manuscript.tex")
src = P.read_text(encoding="utf-8")

# Note: in a regular Python string '\\\\verb' is the two-char regex pattern
# matching a literal '\verb'. We must NOT use \v in a raw string here, as
# Python regex interprets \v as vertical-whitespace.
PATTERN = re.compile(r"\\verb\|([^|]+)\|")

def repl(m):
    return r"\texttt{" + m.group(1).replace("_", r"\_") + "}"

new = PATTERN.sub(repl, src)
n = src.count(r"\verb|")
P.write_text(new, encoding="utf-8")
print(f"replaced {n} verb spans -> {(new.count(r'\\texttt{') - src.count(r'\\texttt{'))} new texttt")
