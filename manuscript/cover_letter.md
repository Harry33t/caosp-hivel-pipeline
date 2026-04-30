# Cover letter — *Contributions of the Astronomical Observatory Skalnaté Pleso* (CAOSP)

**Manuscript title.** *A Gaia DR3–LAMOST reassessment of high-velocity star candidates with geometric-distance-aware kinematics*

**Section.** Regular article.

**Authors.** F.\ Li (Nanjing Vocational College of Information Technology), G.\ Huang (Northwest A\&F University). Both authors contributed equally.

---

Dear Editor,

We submit for your consideration the manuscript *A Gaia DR3–LAMOST reassessment of high-velocity star candidates with geometric-distance-aware kinematics* as a regular article for *Contributions of the Astronomical Observatory Skalnaté Pleso*.

The manuscript revisits three published Gaia/LAMOST high-velocity-star catalogues: Li et al. (2021), Li et al. (2023), and Liao et al. (2024). Rather than proposing a new candidate catalogue, we ask a narrow methodological question: how much of the inferred unbound classification is driven by the adopted distance estimator, and how much by the choice of radial-velocity catalogue?

To isolate this effect, we construct a fixed final-strict sample of 356 stars passing Gaia astrometric quality cuts, a 1 arcsec LAMOST DR9 LRS cross-match, atmospheric-parameter requirements, and a Gaia–LAMOST radial-velocity consistency cut. We then run the same 1000-draw Monte Carlo kinematic calculation twice on the identical sample: once using inverse-parallax distances, and once using the Bailer-Jones et al. (2021) geometric distances. Under the galpy `MWPotential2014` Galactic potential, replacing inverse-parallax distances with Bailer-Jones distances reduces the number of likely unbound stars from 48 to 3 for $P_{\rm unbound}>0.5$, and from 12 to 1 for $P_{\rm unbound}>0.9$. Replacing Gaia radial velocities with LAMOST radial velocities on the same sample changes the median $v_{\rm grf}$ by 0.00 km s$^{-1}$ and changes the $P_{\rm unbound}>0.5$ classification of only one star. The result is therefore a fixed-sample demonstration that the unbound classification of these published candidates is dominated by the distance prescription rather than by the radial-velocity catalogue.

The manuscript is intended as a methodological complement to the recent CAOSP paper by Elsanhoury (2025). That work used similar Gaia–LAMOST high-velocity-star data to study global Galactic kinematic quantities, including velocity ellipsoids, the solar motion, and Oort constants. Our manuscript does not recompute those population-level kinematic statistics and does not introduce a new HVS catalogue. Instead, it keeps the source catalogues, cross-match, quality cuts, radial velocities, and Monte Carlo machinery fixed, and varies only the distance estimator entering the unbound probability. This controlled, single-parameter comparison keeps the claim narrow and directly testable.

The paper includes seven figures and three main tables. We also provide a machine-readable supplementary CSV containing the Top-30 candidates with Monte Carlo dispersions, heliocentric total speed, local escape speed, and Gaia–LAMOST radial-velocity differences. All input data are from public archives, including VizieR, the Gaia archive, and LAMOST DR9, and the analysis uses open-source software including `astropy`, `astroquery`, and `galpy`. A reproducibility repository with the catalogue queries, cross-matching scripts, kinematic solver, and figure/table generation code, together with the manuscript LaTeX source and the supplementary Top-30 CSV, is publicly available at <https://github.com/Harry33t/caosp-hivel-pipeline>.

Neither author has any conflict of interest to declare. Both authors contributed equally to this work.

Thank you for considering our manuscript for publication in *Contributions of the Astronomical Observatory Skalnaté Pleso*.

Sincerely,

F.\ Li and G.\ Huang
