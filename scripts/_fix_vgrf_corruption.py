"""One-off script to repair the V_GSR -> v_grf rename corruption.

The original sed command (s/\\Vgsr/\\vgrf/g) interpreted \\v as the VT
control byte (0x0B) inside the replacement string, leaving 0x0B + 'grf'
in place of '\\vgrf'. Subsequent shell-quoted Python fixes did not
correctly emit a literal backslash. This module reads the file as bytes
and substitutes deterministically."""
from pathlib import Path

VT = b"\x0b"
TARGET = b"\\vgrf"  # backslash-v-g-r-f, the LaTeX macro we want
fp = Path(r"D:/download_default/tianwen_siluofake/manuscript/manuscript.tex")
data = fp.read_bytes()

# Pattern produced by the bad sed: 0x0B + 'grf'
bad1 = VT + b"grf"
n1 = data.count(bad1)
data = data.replace(bad1, TARGET)

# Sanity guard: also collapse any '\\\\vgrf' (double-bs) into '\\vgrf'.
bad2 = b"\\\\vgrf"
n2 = data.count(bad2)
data = data.replace(bad2, TARGET)

# Final guard: ensure no stray VT bytes remain.
n_vt = data.count(VT)

fp.write_bytes(data)
print(f"replaced {n1} bad VT sequences and {n2} double-bs sequences")
print(f"final \\vgrf count: {data.count(TARGET)}")
print(f"residual VT bytes: {n_vt}")
