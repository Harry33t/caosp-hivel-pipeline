"""Step 7: paper-ready figures & tables (no ML, no SHAP).

Produces 7 figures (PNG + PDF) and 3 tables (CSV + LaTeX) plus three
companion markdown documents (captions, table notes, inventory).
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from caosp_hivel.paths import ensure_dirs, PROCESSED_DIR
from caosp_hivel.log import get_logger

PAPER_DIR = ROOT / "paper"
FIG_DIR = PAPER_DIR / "figures"
TBL_DIR = PAPER_DIR / "tables"
REPORTS_DIR = ROOT / "reports"

# journal-style defaults
plt.rcParams.update({
    "font.family": "DejaVu Serif",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "legend.fontsize": 8,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "axes.linewidth": 0.8,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
})

CATALOG_COLORS = {"li2021": "tab:blue", "li2023": "tab:orange", "liao2024": "tab:green"}


def _save(fig: plt.Figure, name: str) -> tuple[Path, Path]:
    png = FIG_DIR / f"{name}.png"
    pdf = FIG_DIR / f"{name}.pdf"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
    return png, pdf


# ---------- helpers ----------
def _primary_catalog(s: str) -> str:
    """First catalog token from a comma-list."""
    if not isinstance(s, str) or not s:
        return ""
    return s.split(",")[0]


# ---------- Figure 1: sample funnel (proper flowchart) ----------
def fig1_funnel():
    # Each item: (stage label, count, gate explanation that produced this stage)
    main_chain = [
        ("VizieR catalogues",            1198, None),
        ("Gaia DR3 match",               1188, "resolve Gaia DR3 identifier"),
        ("Unique master sample",         1101, "remove duplicates across catalogues"),
        ("Astrometric quality",           948, r"RUWE $<$ 1.4, $\varpi/\sigma_{\varpi}>5$"),
        ("Gaia-only clean",               675, "Gaia DR3 RV available"),
        ("LAMOST cross-match",            651, "1 arcsec LAMOST DR9 LRS match"),
        ("LAMOST quality",                563, r"$T_{\mathrm{eff}}$, $\log g$, [Fe/H] available; S/N $\geq$ 20"),
        ("Gaia $\\times$ LAMOST clean",   358, "Gaia astrometry, Gaia RV, LAMOST quality"),
        ("Final strict",                  356, r"$|RV_{\mathrm{LAMOST}}-RV_{\mathrm{Gaia}}|\leq 50$ km s$^{-1}$"),
    ]
    rv_branch = ("RV outlier follow-up", 2,
                 r"$|\Delta v_{\mathrm{RV}}|>50$ km s$^{-1}$")

    fig, ax = plt.subplots(figsize=(8.5, 9.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 11)
    ax.invert_yaxis()
    ax.axis("off")

    box_w, box_h = 4.4, 0.62
    cx_main = 3.4     # main column x-centre
    cx_branch = 11.0  # side branch x-centre — placed far enough that the
                      # branch arrow has its own horizontal corridor and the
                      # branch gate label has room to render horizontally.
    main_color = "#e6f0fa"
    final_color = "#7ab87a"   # darker green
    branch_color = "#f3b885"

    # main chain
    centres = []
    for i, (label, n, _) in enumerate(main_chain):
        y0 = 0.6 + i * 1.05
        x0 = cx_main - box_w / 2
        is_final = (i == len(main_chain) - 1)
        face = final_color if is_final else main_color
        edge = "black"
        lw = 1.4 if is_final else 0.9
        box = FancyBboxPatch((x0, y0), box_w, box_h,
                             boxstyle="round,pad=0.03",
                             linewidth=lw, edgecolor=edge, facecolor=face)
        ax.add_patch(box)
        weight = "bold" if is_final else "normal"
        ax.text(cx_main, y0 + box_h / 2, f"{label}: {n}",
                ha="center", va="center", fontsize=10, fontweight=weight)
        centres.append((cx_main, y0 + box_h / 2, y0, y0 + box_h))

    # arrows + edge labels between consecutive boxes
    for i in range(len(main_chain) - 1):
        _, _, _, y_top = centres[i]
        _, _, y_bot, _ = centres[i + 1]
        arr = FancyArrowPatch((cx_main, y_top), (cx_main, y_bot),
                              arrowstyle="->", mutation_scale=14, color="black",
                              linewidth=0.9)
        ax.add_patch(arr)
        gate = main_chain[i + 1][2]
        if gate:
            ax.text(cx_main + box_w / 2 + 0.15, (y_top + y_bot) / 2, gate,
                    ha="left", va="center", fontsize=8, style="italic",
                    color="#444")

    # RV-outlier side branch — pulled off the "Gaia × LAMOST clean" stage.
    # The branch box is at the same y level as the source. Branch gate label
    # is placed ABOVE the arrow (inverted-y: smaller value) so it does not
    # collide with the main-chain gate label below the source box.
    src_idx = 7
    src_x, src_y, src_top, src_bottom = centres[src_idx]
    branch_y = src_y
    by0 = branch_y - box_h / 2
    bx0 = cx_branch - box_w / 2
    branch_box = FancyBboxPatch((bx0, by0), box_w, box_h,
                                boxstyle="round,pad=0.03",
                                linewidth=0.9, edgecolor="black",
                                facecolor=branch_color)
    ax.add_patch(branch_box)
    label, n, gate = rv_branch
    ax.text(cx_branch, branch_y, f"{label}: {n}",
            ha="center", va="center", fontsize=10)
    arr = FancyArrowPatch((src_x + box_w / 2, branch_y),
                          (cx_branch - box_w / 2, branch_y),
                          arrowstyle="->", mutation_scale=14, color="black",
                          linewidth=0.9)
    ax.add_patch(arr)
    ax.text((src_x + box_w / 2 + cx_branch - box_w / 2) / 2,
            branch_y - 0.22,
            r"$|\Delta_\mathrm{rv}| > 50$ km s$^{-1}$",
            ha="center", va="bottom", fontsize=8, style="italic", color="#444")

    return _save(fig, "fig1_sample_funnel")


# ---------- Figure 2: Galactic sky distribution ----------
def fig2_sky(only: pd.DataFrame, strict: pd.DataFrame, top: pd.DataFrame):
    from astropy.coordinates import SkyCoord
    import astropy.units as u

    def _gal(df):
        c = SkyCoord(df["ra"].values * u.deg, df["dec"].values * u.deg, frame="icrs")
        g = c.galactic
        return g.l.wrap_at(180 * u.deg).deg, g.b.deg

    fig, ax = plt.subplots(figsize=(8, 4.6), subplot_kw={"projection": "mollweide"})

    if not only.empty:
        l, b = _gal(only)
        ax.scatter(np.deg2rad(l), np.deg2rad(b), s=5, alpha=0.45,
                   color="#9aa0a6", edgecolors="none",
                   label=f"Gaia-only clean (N={len(only)})")

    if not strict.empty:
        l, b = _gal(strict)
        ax.scatter(np.deg2rad(l), np.deg2rad(b), s=10, alpha=0.85,
                   color="tab:blue", edgecolors="none",
                   label=f"final strict (N={len(strict)})")

    if not top.empty:
        topk = top.head(3)
        l, b = _gal(topk)
        ax.scatter(np.deg2rad(l), np.deg2rad(b), s=120, marker="*",
                   color="red", edgecolors="black", linewidths=0.7,
                   label="Top-3 unbound", zorder=10)
        for i, (_, r) in enumerate(topk.iterrows(), 1):
            ax.annotate(str(i), xy=(np.deg2rad(l[i - 1]), np.deg2rad(b[i - 1])),
                        xytext=(8, 8), textcoords="offset points", fontsize=11,
                        color="red", fontweight="bold")

    ax.grid(True, lw=0.3, alpha=0.5)
    ax.set_xticklabels(["150°", "120°", "90°", "60°", "30°", "0°",
                         "330°", "300°", "270°", "240°", "210°"], fontsize=7)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.18), ncol=3,
              fontsize=8, frameon=False)
    return _save(fig, "fig2_sky_distribution")


# ---------- Figure 3: distance comparison ----------
def fig3_distance(master: pd.DataFrame, prelim_top: pd.DataFrame):
    sub = master.dropna(subset=["bj_distance_pc", "distance_pc_inverse_parallax"])
    fig, ax = plt.subplots(figsize=(6, 6))
    qok = sub["q_plx"].fillna(False)
    ax.scatter(sub.loc[qok, "distance_pc_inverse_parallax"],
               sub.loc[qok, "bj_distance_pc"],
               s=8, alpha=0.5, color="tab:blue",
               label=fr"$\varpi/\sigma_\varpi > 5$  (N={int(qok.sum())})")
    ax.scatter(sub.loc[~qok, "distance_pc_inverse_parallax"],
               sub.loc[~qok, "bj_distance_pc"],
               s=8, alpha=0.4, color="tab:gray",
               label=fr"$\varpi/\sigma_\varpi \leq 5$  (N={int((~qok).sum())})")

    top50_median = None
    if not prelim_top.empty:
        merged = prelim_top.merge(
            master[["source_id", "bj_distance_pc",
                    "distance_pc_inverse_parallax"]],
            on="source_id", how="left",
        ).dropna(subset=["bj_distance_pc"])
        ax.scatter(merged["distance_pc_inverse_parallax"],
                   merged["bj_distance_pc"], s=24, marker="^",
                   facecolors="none", edgecolors="red", linewidths=0.9,
                   label=f"Top-50 preliminary (N={len(merged)})")
        ratios = (merged["bj_distance_pc"] /
                  merged["distance_pc_inverse_parallax"]).replace([np.inf, -np.inf], np.nan).dropna()
        if len(ratios):
            top50_median = float(ratios.median())

    pos = sub[sub["distance_pc_inverse_parallax"] > 0]
    lo = max(min(pos["distance_pc_inverse_parallax"].min(),
                 sub["bj_distance_pc"].min()), 1)
    hi = max(pos["distance_pc_inverse_parallax"].max(),
             sub["bj_distance_pc"].max())
    ax.plot([lo, hi], [lo, hi], "k--", lw=1, label=r"$y = x$")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"inverse-parallax distance  $1000/\varpi$  (pc)")
    ax.set_ylabel(r"Bailer-Jones  $r_\mathrm{med,geo}$  (pc)")
    if top50_median is not None:
        ax.text(0.97, 0.04,
                f"Top-50 median  $r_\\mathrm{{BJ}}/(1000/\\varpi)$ = {top50_median:.2f}",
                transform=ax.transAxes, ha="right", va="bottom", fontsize=9,
                bbox=dict(facecolor="white", edgecolor="black",
                          boxstyle="round,pad=0.3"))
    ax.legend(loc="upper left", fontsize=8, frameon=True)
    return _save(fig, "fig3_distance_comparison")


# ---------- Figure 4: Toomre diagram ----------
def fig4_toomre(only: pd.DataFrame, strict: pd.DataFrame, top: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    onb = only.dropna(subset=["U", "V", "W"])
    ax.scatter(onb["V"], np.sqrt(onb["U"] ** 2 + onb["W"] ** 2),
               s=5, alpha=0.35, color="lightgray",
               label=f"Gaia-only clean (N={len(onb)})")
    snb = strict.dropna(subset=["U", "V", "W"])
    ax.scatter(snb["V"], np.sqrt(snb["U"] ** 2 + snb["W"] ** 2),
               s=12, alpha=0.7, color="tab:blue",
               label=f"Final strict (N={len(snb)})")

    if not top.empty:
        topk = top.head(3)
        ax.scatter(topk["V"], np.sqrt(topk["U"] ** 2 + topk["W"] ** 2),
                   s=110, marker="*", color="red", edgecolors="black",
                   linewidths=0.6, label="Top-3 unbound", zorder=10)
        for i, (_, r) in enumerate(topk.iterrows(), 1):
            ax.annotate(str(i), xy=(r["V"], np.sqrt(r["U"] ** 2 + r["W"] ** 2)),
                        xytext=(6, 6), textcoords="offset points", fontsize=10,
                        color="red", fontweight="bold")

    # 200 / 300 km/s reference circles (Toomre convention)
    th = np.linspace(0, 2 * np.pi, 200)
    for r, ls in [(200, ":"), (300, "--"), (500, "-.")]:
        ax.plot(r * np.cos(th), r * np.sin(th), color="black", lw=0.6, ls=ls,
                alpha=0.6)
        ax.text(0, r + 8, f"{r} km/s", ha="center", fontsize=7, color="black")

    ax.set_xlim(-700, 700); ax.set_ylim(0, 800)
    ax.set_xlabel(r"$V$  (km s$^{-1}$, heliocentric Galactic Cartesian)")
    ax.set_ylabel(r"$\sqrt{U^{2} + W^{2}}$  (km s$^{-1}$)")
    ax.legend(loc="upper right", fontsize=8)
    return _save(fig, "fig4_toomre")


# ---------- Figure 5: V_total / v_esc vs distance ----------
def fig5_vgsr_distance(only: pd.DataFrame, strict: pd.DataFrame, top: pd.DataFrame):
    """Unbound criterion expressed as V_GSR / v_esc(R) vs distance.

    Using a ratio (rather than V_GSR alone with a separate v_esc curve)
    means the ``unbound'' threshold is a single horizontal line at y = 1
    independent of distance, which is the cleanest visualisation of the
    paper's main classification.
    """
    fig, ax = plt.subplots(figsize=(7, 5))

    def _d_kpc(df):
        return df["distance_pc"] / 1000.0

    def _ratio(df):
        return df["V_GSR"] / df["v_esc"]

    onb = only.dropna(subset=["distance_pc", "V_GSR", "v_esc"])
    ax.scatter(_d_kpc(onb), _ratio(onb), s=6, alpha=0.35, color="lightgray",
               label=f"Gaia-only clean (N={len(onb)})", zorder=1)
    snb = strict.dropna(subset=["distance_pc", "V_GSR", "v_esc"])
    ax.scatter(_d_kpc(snb), _ratio(snb), s=14, alpha=0.75, color="tab:blue",
               edgecolors="none",
               label=f"final strict (N={len(snb)})", zorder=2)

    # unbound boundary
    ax.axhline(1.0, color="black", lw=1.0, ls="--", zorder=3,
               label=r"$V_\mathrm{GSR} = v_\mathrm{esc}$ (unbound boundary)")
    ax.axhspan(1.0, ax.get_ylim()[1] if ax.get_ylim()[1] > 1 else 3,
               facecolor="red", alpha=0.05, zorder=0)

    if not top.empty:
        topk = top.head(3)
        topk = topk.dropna(subset=["distance_pc", "V_GSR", "v_esc"])
        ax.scatter(_d_kpc(topk), _ratio(topk), s=140, marker="*",
                   color="red", edgecolors="black", linewidths=0.7,
                   label="Top-3 unbound", zorder=10)
        for i, (_, r) in enumerate(topk.iterrows(), 1):
            ax.annotate(f"{i}", xy=(r["distance_pc"] / 1000.0,
                                    r["V_GSR"] / r["v_esc"]),
                        xytext=(8, 8), textcoords="offset points", fontsize=11,
                        color="red", fontweight="bold")

    ax.set_xscale("log")
    ax.set_xlabel("Bailer-Jones distance  (kpc)")
    ax.set_ylabel(r"$v_\mathrm{grf}\,/\,v_\mathrm{esc}(R_\mathrm{gc})$")
    ax.set_ylim(0, max(2.5, _ratio(onb).max() * 1.05))
    # legend in figure margin to avoid overlapping points
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0),
              fontsize=8, frameon=False, borderaxespad=0.0)
    fig.subplots_adjust(right=0.74)
    return _save(fig, "fig5_vgsr_distance")


# ---------- Figure 6: Top-30 P_unbound ----------
def fig6_top_punbound(top: pd.DataFrame):
    fig, axes = plt.subplots(2, 1, figsize=(7.5, 6.5), sharex=True,
                              gridspec_kw={"height_ratios": [2, 1.2]})
    ax = axes[0]
    n = len(top)
    x = np.arange(1, n + 1)

    # rank-1 / rank-2 / rank-3 get distinct accent colours; the rest are blue
    colors_top = ["#c0392b", "#e67e22", "#f1c40f"]   # red, orange, gold
    base_color = "tab:blue"
    point_colors = [colors_top[i] if i < 3 else base_color for i in range(n)]

    for xi, yi, ei, ci in zip(x, top["V_GSR_mc_mean"], top["V_GSR_mc_std"], point_colors):
        ax.errorbar(xi, yi, yerr=ei, fmt="o", ms=5, color=ci, ecolor=ci,
                    elinewidth=0.8, capsize=2)
    ax.axhline(500, color="gray", lw=0.8, ls="--", label=r"500 km s$^{-1}$")
    ax.set_ylabel(r"$v_\mathrm{grf}$  (km s$^{-1}$,  $\pm\,\sigma_\mathrm{MC}$)")
    ax.legend(loc="upper right", fontsize=8)

    ax2 = axes[1]
    bar_colors = [colors_top[i] if i < 3 else
                  ("tab:orange" if p > 0.5 else "tab:blue")
                  for i, p in enumerate(top["P_unbound_final"])]
    ax2.bar(x, top["P_unbound_final"], color=bar_colors,
            edgecolor="black", linewidth=0.4)
    ax2.axhline(0.5, color="gray", lw=0.8, ls="--")
    ax2.axhline(0.9, color="black", lw=0.8, ls=":")
    ax2.set_ylim(0, 1.05)
    ax2.set_ylabel(r"$P_\mathrm{unbound}$")
    ax2.set_xlabel("Candidate rank")
    n_ge05 = int((top["P_unbound_final"] > 0.5).sum())
    n_ge09 = int((top["P_unbound_final"] > 0.9).sum())
    ax2.text(0.99, 0.95,
             rf"$P_\mathrm{{unbound}}>0.5$: {n_ge05}/30  "
             rf"$P_\mathrm{{unbound}}>0.9$: {n_ge09}/30",
             transform=ax2.transAxes, ha="right", va="top",
             bbox=dict(facecolor="white", edgecolor="black",
                       boxstyle="round,pad=0.3"),
             fontsize=9)
    fig.tight_layout()
    return _save(fig, "fig6_top_punbound")


# ---------- Figure 7: RV sensitivity ----------
def fig7_rv_sensitivity(sens: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

    ax = axes[0]
    sub = sens.dropna(subset=["V_GSR_gaia_rv", "V_GSR_lamost_rv"])
    lo = min(sub["V_GSR_gaia_rv"].min(), sub["V_GSR_lamost_rv"].min())
    hi = max(sub["V_GSR_gaia_rv"].max(), sub["V_GSR_lamost_rv"].max())
    ax.scatter(sub["V_GSR_gaia_rv"], sub["V_GSR_lamost_rv"],
               s=10, alpha=0.6, color="tab:blue")
    ax.plot([lo, hi], [lo, hi], "k--", lw=1, label=r"$y = x$")
    # Build the labels by string-concatenating a math fragment with plain
    # text. matplotlib mathtext otherwise treats each capital in "LAMOST"
    # as a separate symbol (italic-spaced), giving "L A M O S T".
    ax.set_xlabel(r"$v_\mathrm{grf}$" + " (Gaia RV)  (km s" + r"$^{-1}$" + ")")
    ax.set_ylabel(r"$v_\mathrm{grf}$" + " (LAMOST RV)  (km s" + r"$^{-1}$" + ")")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_title("(a) per-star comparison", fontsize=10)

    ax = axes[1]
    dV = sens["V_GSR_delta"].dropna()
    ax.hist(dV, bins=40, color="tab:blue", edgecolor="black", linewidth=0.4)
    med = float(dV.median()); p90 = float(dV.abs().quantile(0.9))
    mx = float(dV.abs().max())
    ax.axvline(med, color="black", lw=1, ls="--",
               label=f"median = {med:.2f} km s" + r"$^{-1}$")
    ax.set_xlabel(r"$\Delta v_\mathrm{grf}$" + " (LAMOST $-$ Gaia)  (km s" + r"$^{-1}$" + ")")
    ax.set_ylabel("count")
    ax.set_title(
        rf"(b) distribution; $p_{{90}}\,|\Delta| = {p90:.2f}$, "
        rf"max $|\Delta| = {mx:.2f}$  km s$^{{-1}}$",
        fontsize=10,
    )
    ax.legend(loc="upper right", fontsize=8)

    fig.tight_layout()
    return _save(fig, "fig7_rv_sensitivity")


# ---------- Tables ----------
def _save_table(df: pd.DataFrame, name: str, *, caption: str | None = None,
                label: str | None = None, fmt: dict | None = None) -> tuple[Path, Path]:
    csv = TBL_DIR / f"{name}.csv"
    tex = TBL_DIR / f"{name}.tex"
    df.to_csv(csv, index=False)
    pretty = df.copy()
    # Defensive: any int column whose values exceed float64's exact range
    # (2^53 ≈ 9e15) MUST be converted to string before pandas to_latex routes
    # through Styler, which silently coerces to float and loses the trailing
    # digits of Gaia source_ids.
    INT64_SAFE = 1 << 53
    for c in pretty.columns:
        if pd.api.types.is_integer_dtype(pretty[c]):
            if pretty[c].abs().max() > INT64_SAFE:
                pretty[c] = pretty[c].astype(str)
    if fmt:
        for col, f in fmt.items():
            if col in pretty.columns:
                pretty[col] = pretty[col].apply(
                    lambda v: f.format(v) if pd.notna(v) else "—"
                )
    # We use escape=False because some headers (Table 3) contain hand-written
    # LaTeX math. Manually escape underscores in string cells to avoid
    # accidental subscripts -- but only in cells that look like plain text.
    # Cells that already contain a LaTeX backslash command or '$...$' math
    # are assumed to be hand-formatted and left alone.
    def _safe_escape_underscore(v):
        if not isinstance(v, str):
            return v
        if "\\" in v or "$" in v:
            return v  # hand-written LaTeX, do not touch
        return v.replace("_", r"\_")

    for c in pretty.columns:
        if pd.api.types.is_string_dtype(pretty[c]) or pretty[c].dtype == object:
            pretty[c] = pretty[c].map(_safe_escape_underscore)
    pretty.to_latex(
        tex, index=False, escape=False,
        caption=caption, label=label, longtable=False,
    )
    return csv, tex


def table1_funnel():
    # All Definition strings use LaTeX-safe forms: '<' and '>' rendered via
    # math mode, no Unicode logical operators (we use plain English `and`).
    rows = [
        ("VizieR rows", 1198,
         "All three high-velocity-star catalogues."),
        ("Gaia DR3 hit", 1188,
         "VizieR \\texttt{Gaia} ids that resolve in \\texttt{gaiadr3.gaia\\_source}."),
        ("Unique Gaia source\\_id (master)", 1101,
         "After de-duplication across catalogues."),
        ("\\texttt{q\\_gaia\\_astrometry}", 948,
         "$\\mathrm{RUWE}<1.4$ and $\\varpi>0$ and $\\varpi/\\sigma_{\\varpi}>5$."),
        ("Gaia-only clean", 675,
         "\\texttt{q\\_gaia\\_astrometry} and Gaia RV available."),
        ("Gaia~$\\times$~LAMOST matched", 651,
         "$1\\,\\mathrm{arcsec}$ sky cross-match (any quality)."),
        ("\\texttt{q\\_lamost\\_quality}", 563,
         "LAMOST $T_{\\rm eff}$, $\\log g$, [Fe/H] all reported and $\\mathrm{SNR}\\geq 20$."),
        ("Gaia~$\\times$~LAMOST clean", 358,
         "\\texttt{q\\_gaia\\_astrometry} and Gaia RV and \\texttt{q\\_lamost\\_quality}."),
        ("Final strict", 356,
         "Above and $|v_{\\rm RV,LAMOST}-v_{\\rm RV,Gaia}|\\leq 50\\;\\mathrm{km\\,s^{-1}}$."),
        ("RV-outlier follow-up", 2,
         "Above gates and $|\\Delta v_{\\rm RV}|>50\\;\\mathrm{km\\,s^{-1}}$; reported separately."),
    ]
    df = pd.DataFrame(rows, columns=["Stage", "N", "Definition"])
    return _save_table(
        df, "table1_sample_funnel",
        caption="Sample construction and quality cuts.",
        label="tab:funnel",
    )


def table2_sensitivity():
    """Compact 7-row distance-sensitivity table. RV-sensitivity numbers
    were moved to the Fig. 7 caption per the editorial advice that
    Table 2 was over-stuffed."""
    rows = [
        ("Sample size",                                           "356",  "356"),
        ("$P_{\\mathrm{unbound}} > 0.5$",                         "48",   "3"),
        ("$P_{\\mathrm{unbound}} > 0.7$",                         "29",   "1"),
        ("$P_{\\mathrm{unbound}} > 0.9$",                         "12",   "1"),
        ("Stars downgraded across $P=0.5$",                       "---",  "45"),
        ("Stars promoted across $P=0.5$",                         "---",  "0"),
        ("Median $r_{\\mathrm{med,geo}}/(1000/\\varpi)$",         "---",  "0.88"),
    ]
    df = pd.DataFrame(rows, columns=["Quantity", "Inverse parallax", "Bailer--Jones"])
    return _save_table(
        df, "table2_distance_sensitivity",
        caption=("Distance sensitivity on the same 356-star final-strict "
                 "sample; the two columns differ only in the distance "
                 "estimator."),
        label="tab:sensitivity",
    )


def table3_top(top: pd.DataFrame):
    """Top-15 in the main paper plus a separate Top-30 supplementary table.

    The main table uses $v_\\mathrm{grf}$ (3D Galactocentric rest-frame speed,
    used for $P_\\mathrm{unbound}$). Heliocentric $V_\\mathrm{tot,helio}$,
    MC dispersions, and $\\Delta v_{\\rm RV}$ live only in the supplementary
    table to keep the main table readable."""
    df = top.copy().head(30)
    df["source_id"] = df["source_id"].astype("int64").astype(str)
    df["bj_distance_kpc"] = df["distance_pc"] / 1000.0
    flags = pd.read_parquet(PROCESSED_DIR / "hivel_final_sample_flags.parquet")
    flags["source_id"] = flags["source_id"].astype("int64").astype(str)
    df = df.merge(flags[["source_id", "delta_rv"]], on="source_id", how="left")

    def _note(row):
        bits = []
        if row["P_unbound_final"] > 0.9:
            bits.append("high-confidence unbound")
        elif row["P_unbound_final"] > 0.5:
            bits.append("likely unbound")
        if pd.notna(row["delta_rv"]) and abs(row["delta_rv"]) > 50:
            bits.append("RV outlier")
        if "li2021,liao2024" in str(row["catalogs"]):
            bits.append("dual-catalogue")
        return "; ".join(bits) if bits else "---"
    df["notes"] = df.apply(_note, axis=1)
    df.insert(0, "rank", range(1, len(df) + 1))

    # ----- main table: Top-15, ten columns -----
    main_cols = [
        ("rank",            "rank", "{:d}"),
        ("source_id",       "Gaia DR3 source\\_id", None),
        ("catalogs",        "catalogues", None),
        ("bj_distance_kpc", "$d_\\mathrm{BJ}$ [kpc]", "{:.2f}"),
        ("V_GSR_mc_mean",   "$\\overline{v_{\\rm grf}}$ [\\,km\\,s$^{-1}$\\,]", "{:.0f}"),
        ("P_unbound_final", "$P_\\mathrm{unbound}$", "{:.3f}"),
        ("lamost_teff",     "$T_\\mathrm{eff}$ [K]", "{:.0f}"),
        ("lamost_logg",     "$\\log g$", "{:.2f}"),
        ("lamost_feh",      "[Fe/H]", "{:.2f}"),
        ("notes",           "notes", None),
    ]
    main = df.head(15)[[c for c, _, _ in main_cols]].copy()
    main.columns = [name for _, name, _ in main_cols]
    main_fmt = {name: f for col, name, f in main_cols if f}
    main_tuple = _save_table(
        main, "table3_final_top_candidates",
        caption=("Top-15 final high-velocity candidates ranked by "
                 "$P_\\mathrm{unbound}=P(v_\\mathrm{grf}>v_\\mathrm{esc})$. "
                 "Distances are Bailer--Jones $r_\\mathrm{med,geo}$; "
                 "$v_\\mathrm{grf}$ is the 3D Galactocentric rest-frame "
                 "speed; $T_\\mathrm{eff}$, $\\log g$ and [Fe/H] are LAMOST "
                 "DR9 LRS values. The full Top-30 with MC dispersions, "
                 "heliocentric $V_\\mathrm{tot,helio}$ and "
                 "$\\Delta v_{\\rm RV}$ is given in the machine-readable "
                 "supplementary Table~A1."),
        label="tab:top15", fmt=main_fmt,
    )

    # ----- supplementary Top-30 table -----
    supp_cols = [
        ("rank",            "rank", "{:d}"),
        ("source_id",       "Gaia DR3 source\\_id", None),
        ("catalogs",        "catalogues", None),
        ("bj_distance_kpc", "$d_\\mathrm{BJ}$ [kpc]", "{:.2f}"),
        ("V_GSR_mc_mean",   "$\\overline{v_{\\rm grf}}$ [\\,km\\,s$^{-1}$\\,]", "{:.0f}"),
        ("V_GSR_mc_std",    "$\\sigma_{v_{\\rm grf}}$ [\\,km\\,s$^{-1}$\\,]", "{:.0f}"),
        ("V_total",         "$V_\\mathrm{tot,helio}$ [\\,km\\,s$^{-1}$\\,]", "{:.0f}"),
        ("v_esc",           "$v_\\mathrm{esc}$ [\\,km\\,s$^{-1}$\\,]", "{:.0f}"),
        ("P_unbound_final", "$P_\\mathrm{unbound}$", "{:.3f}"),
        ("lamost_teff",     "$T_\\mathrm{eff}$ [K]", "{:.0f}"),
        ("lamost_logg",     "$\\log g$", "{:.2f}"),
        ("lamost_feh",      "[Fe/H]", "{:.2f}"),
        ("delta_rv",        "$\\Delta v_{\\rm RV}$ [\\,km\\,s$^{-1}$\\,]", "{:.1f}"),
        ("notes",           "notes", None),
    ]
    keep_pairs = [(c, n, f) for c, n, f in supp_cols if c in df.columns]
    supp = df[[c for c, _, _ in keep_pairs]].copy()
    supp.columns = [name for _, name, _ in keep_pairs]
    supp_fmt = {name: f for col, name, f in keep_pairs if f}
    _save_table(
        supp, "tableA1_supplementary_top30",
        caption="Supplementary Top-30 candidate list (extended columns).",
        label="tab:top30supp", fmt=supp_fmt,
    )
    return main_tuple


def main() -> int:
    ensure_dirs()
    PAPER_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TBL_DIR.mkdir(parents=True, exist_ok=True)
    log = get_logger("caosp.step7")

    # load data
    only = pd.read_parquet(PROCESSED_DIR / "final_kinematics_gaia_only_clean.parquet")
    strict = pd.read_parquet(PROCESSED_DIR / "final_kinematics_strict.parquet")
    top = pd.read_csv(PROCESSED_DIR / "final_top_candidates.csv")
    sens = pd.read_csv(PROCESSED_DIR / "final_rv_sensitivity.csv")
    master_bj = pd.read_parquet(PROCESSED_DIR / "hivel_with_bailer_jones_distance.parquet")
    prelim_top = pd.read_csv(PROCESSED_DIR / "top_unbound_candidates.csv")

    log.info("inputs: only=%d, strict=%d, top=%d, sens=%d",
             len(only), len(strict), len(top), len(sens))

    figs = [
        ("fig1", fig1_funnel(), "Sample construction funnel.", "Section 2 (Data and Sample)"),
        ("fig2", fig2_sky(only, strict, top), "Galactic-coordinate sky distribution.", "Section 4.1"),
        ("fig3", fig3_distance(master_bj, prelim_top), "Distance comparison.", "Section 3.2 / Section 4.2"),
        ("fig4", fig4_toomre(only, strict, top), "Toomre diagram.", "Section 4.1"),
        ("fig5", fig5_vgsr_distance(only, strict, top), "V_GSR vs Bailer-Jones distance.", "Section 4.2"),
        ("fig6", fig6_top_punbound(top), "Top-30 P_unbound and MC uncertainty.", "Section 4.3"),
        ("fig7", fig7_rv_sensitivity(sens), "RV sensitivity (Gaia vs LAMOST).", "Section 4.3 / Discussion"),
    ]
    for name, (png, pdf), _, _ in figs:
        log.info("%s: %s", name, png.relative_to(ROOT))

    tables = [
        ("table1", table1_funnel(), "Sample construction and quality cuts.", "Section 2"),
        ("table2", table2_sensitivity(), "Distance and kinematic sensitivity summary.", "Section 4.2"),
        ("table3", table3_top(top), "Top-30 final candidates.", "Section 4.3 / Conclusions"),
    ]
    for name, (csv, tex), _, _ in tables:
        log.info("%s: %s + .tex", name, csv.relative_to(ROOT))

    # captions
    captions = []
    captions.append("# Figure captions (paper draft)\n")
    captions.append("Each figure exists as both PNG (review) and PDF (LaTeX submission) "
                    "under `paper/figures/`.\n")
    cap_text = {
        "fig1": ("Sample construction. The vertical chain shows the row count after each "
                 "filter, with the gate criterion annotated to the right of the arrows. "
                 "The final-strict analysis sample (356 stars; dark green) is the "
                 "population used for the Top-30 candidate table; the RV-outlier "
                 "follow-up subset (2 stars; orange side branch) is reported separately "
                 "and is not part of the final strict sample."),
        "fig2": ("Galactic sky distribution of the Gaia-only clean background "
                 "(grey), the final-strict sample (blue) and the three highest-"
                 "confidence unbound candidates (red stars, labelled 1--3). Catalogue "
                 "provenance is not encoded by colour to keep the figure legible; in "
                 "particular the Li et al.\\ (2023) very-high-velocity subset is "
                 "retained in the Gaia-only analysis but contributes no objects to "
                 "the final strict sample under our LAMOST cross-match and quality "
                 "criteria."),
        "fig3": ("Pairwise comparison of inverse-parallax distances ($1000/\\varpi$) "
                 "and Bailer-Jones (2021) geometric distances ($r_\\mathrm{med,geo}$). "
                 "Triangles mark the 50 candidates with the largest preliminary "
                 "$P_\\mathrm{unbound}$. Bailer-Jones distances are systematically "
                 "smaller; the median ratio $r_\\mathrm{BJ}/(1000/\\varpi)$ is 0.88 "
                 "across the full 1101-star master sample and 0.76 on the "
                 "preliminary Top-50 (annotation)."),
        "fig4": ("Toomre diagram showing $\\sqrt{U^{2}+W^{2}}$ versus $V$ for the "
                 "Gaia-only clean (grey), the final-strict sample (blue) and the "
                 "Top-3 unbound candidates (red stars). The velocities are "
                 "heliocentric Galactic Cartesian, with $U$ positive toward the "
                 "Galactic centre, $V$ positive in the direction of Galactic rotation "
                 "and $W$ positive toward the North Galactic Pole; they are not "
                 "LSR-corrected (see Section~3 for the full convention). Dashed "
                 "circles mark constant heliocentric peculiar speeds of 200, 300 and "
                 "500\\,km\\,s$^{-1}$."),
        "fig5": ("Ratio of the Galactocentric speed $V_\\mathrm{GSR}$ to the local "
                 "escape speed $v_\\mathrm{esc}(R_\\mathrm{gc})$ under "
                 "MWPotential2014, plotted against Bailer-Jones distance. The dashed "
                 "horizontal line at $V_\\mathrm{GSR}/v_\\mathrm{esc}=1$ marks the "
                 "unbound boundary; the lightly shaded region above it is the "
                 "candidate-unbound zone. The Top-3 stars (red) are the only objects "
                 "in the final-strict sample that sit close to or above this line; "
                 "Gaia-only background (grey) and final strict (blue) populations "
                 "are shown for context."),
        "fig6": ("Top-30 final candidates ranked by $P_\\mathrm{unbound}$ (Step 6B). "
                 "Top panel: Monte Carlo mean $V_\\mathrm{GSR}$ with $\\pm 1\\sigma$ "
                 "error bars (1\\,000 draws per star). Bottom panel: $P_\\mathrm{unbound}$, "
                 "with the rank-1, 2 and 3 candidates highlighted in red, orange and "
                 "gold. Reference lines: $P=0.5$ (dashed), $P=0.9$ (dotted), and "
                 "$V_\\mathrm{GSR}=500$\\,km\\,s$^{-1}$ in the upper panel. After "
                 "adopting Bailer-Jones geometric distances only 3/30 stars retain "
                 "$P_\\mathrm{unbound}>0.5$ and 1/30 retains $P>0.9$, indicating "
                 "that the unbound classification is highly sensitive to the choice "
                 "of distance estimator."),
        "fig7": ("RV-choice sensitivity on the final-strict sample (N=356). "
                 "Panel (a): per-star $V_\\mathrm{GSR}$ computed with Gaia DR3 "
                 "radial velocities versus the same quantity computed with LAMOST "
                 "DR9 radial velocities. Panel (b): histogram of the difference "
                 "$\\Delta V_\\mathrm{GSR} = $ LAMOST $-$ Gaia; median = "
                 "0.00\\,km\\,s$^{-1}$, $p_{90}|\\Delta|$ = 5.7\\,km\\,s$^{-1}$, "
                 "max\\,$|\\Delta|$ = 32.0\\,km\\,s$^{-1}$. The headline unbound "
                 "classification is essentially insensitive to the choice of RV."),
    }
    for name, _, _, section in figs:
        captions.append(f"## {name.upper()}\n")
        captions.append(f"**Paper section:** {section}\n")
        captions.append(f"**Caption draft.** {cap_text[name]}\n")
    (PAPER_DIR / "figure_captions.md").write_text("\n".join(captions), encoding="utf-8")
    log.info("captions -> %s", PAPER_DIR / "figure_captions.md")

    # table notes
    notes = []
    notes.append("# Table notes (paper draft)\n")
    note_text = {
        "table1": (
            "Each row is a deterministic gate; the count is the size of the population that "
            "passes all gates *up to and including* this row. The *RV outlier follow-up* "
            "row is not a downstream cut — those 2 stars are excluded from the headline "
            "*Final strict* sample but kept in `data/processed/rv_outlier_followup.csv` for "
            "spectroscopic follow-up. A third RV-outlier exists in the master table but "
            "fails `q_lamost_quality` and so does not enter the follow-up subset."
        ),
        "table2": (
            "Preliminary numbers come from Step 4B (Gaia-only kinematics with $1/\\varpi$ "
            "distances). Final numbers come from Step 6B (BJ geometric distances + Gaia DR3 "
            "RV; 1\\,000-draw Monte Carlo per star). The drop from 221 to 3 stars with "
            "$P_\\mathrm{unbound}>0.5$ is the headline finding of this work."
        ),
        "table3": (
            "Distances are Bailer-Jones (2021) $r_\\mathrm{med,geo}$ in kpc. "
            "$V_\\mathrm{GSR}$ values are Monte-Carlo means (1\\,000 draws sampling "
            "parallax, proper motion, RV and the BJ distance log-normal). LAMOST $T_\\mathrm{eff}$, "
            "$\\log g$, [Fe/H] are from the DR9 LRS stellar parameter catalogue, single-epoch "
            "best-SNR match. $\\Delta_\\mathrm{rv}$ = LAMOST $-$ Gaia. Notes flag stars "
            "with $P_\\mathrm{unbound}>0.5$ (probable unbound) or $>0.9$ "
            "(highest-confidence unbound), simultaneously catalogued in li2021 and liao2024 "
            "(dual-catalog), and any RV outlier."
        ),
    }
    for name, _, _, section in tables:
        notes.append(f"## {name.upper()}\n")
        notes.append(f"**Paper section:** {section}\n")
        notes.append(f"**Note.** {note_text[name]}\n")
    (PAPER_DIR / "table_notes.md").write_text("\n".join(notes), encoding="utf-8")
    log.info("table notes -> %s", PAPER_DIR / "table_notes.md")

    # inventory
    inv = []
    inv.append("# Figure & table inventory\n")
    inv.append("Generated by `scripts/07_paper_figures_tables.py`. "
               "All figures exist as PNG (review) and PDF (LaTeX submission).\n")
    inv.append("## Figures\n")
    inv.append("| key | file | paper section |")
    inv.append("|---|---|---|")
    for name, (png, _), _, section in figs:
        inv.append(f"| {name} | `paper/figures/{png.stem}.{{png,pdf}}` | {section} |")
    inv.append("")
    inv.append("## Tables\n")
    inv.append("| key | file | paper section |")
    inv.append("|---|---|---|")
    for name, (csv, _), _, section in tables:
        inv.append(f"| {name} | `paper/tables/{csv.stem}.{{csv,tex}}` | {section} |")
    inv.append("")
    inv.append("## Companion documents\n")
    inv.append("- `paper/figure_captions.md` — caption drafts.")
    inv.append("- `paper/table_notes.md` — table notes / methodology blurbs.")
    inv.append("")
    (REPORTS_DIR / "figure_table_inventory.md").write_text("\n".join(inv), encoding="utf-8")
    log.info("inventory -> %s", REPORTS_DIR / "figure_table_inventory.md")

    print(f"\nFigures: {len(figs)} pairs (PNG+PDF) under paper/figures/")
    print(f"Tables: {len(tables)} pairs (CSV+TeX) under paper/tables/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
