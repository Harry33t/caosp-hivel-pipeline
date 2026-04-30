# Table notes (paper draft)

## TABLE1

**Paper section:** Section 2

**Note.** Each row is a deterministic gate; the count is the size of the population that passes all gates *up to and including* this row. The *RV outlier follow-up* row is not a downstream cut — those 2 stars are excluded from the headline *Final strict* sample but kept in `data/processed/rv_outlier_followup.csv` for spectroscopic follow-up. A third RV-outlier exists in the master table but fails `q_lamost_quality` and so does not enter the follow-up subset.

## TABLE2

**Paper section:** Section 4.2

**Note.** Preliminary numbers come from Step 4B (Gaia-only kinematics with $1/\varpi$ distances). Final numbers come from Step 6B (BJ geometric distances + Gaia DR3 RV; 1\,000-draw Monte Carlo per star). The drop from 221 to 3 stars with $P_\mathrm{unbound}>0.5$ is the headline finding of this work.

## TABLE3

**Paper section:** Section 4.3 / Conclusions

**Note.** Distances are Bailer-Jones (2021) $r_\mathrm{med,geo}$ in kpc. $V_\mathrm{GSR}$ values are Monte-Carlo means (1\,000 draws sampling parallax, proper motion, RV and the BJ distance log-normal). LAMOST $T_\mathrm{eff}$, $\log g$, [Fe/H] are from the DR9 LRS stellar parameter catalogue, single-epoch best-SNR match. $\Delta_\mathrm{rv}$ = LAMOST $-$ Gaia. Notes flag stars with $P_\mathrm{unbound}>0.5$ (probable unbound) or $>0.9$ (highest-confidence unbound), simultaneously catalogued in li2021 and liao2024 (dual-catalog), and any RV outlier.
