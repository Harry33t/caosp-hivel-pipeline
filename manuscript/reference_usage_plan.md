# Reference usage plan

Section-by-section assignment of the 40 references in
`references.bib`. Cite each reference at least once in its primary section;
optional secondary citations are listed in parentheses.

## §1 Introduction (must-cite)

| key | role |
|---|---|
| `Hills1988HVS` | foundational ejection mechanism |
| `YuTremaine2003Ejection` | MBH ejection theory |
| `Brown2005FirstHVS` | first observed HVS |
| `Brown2015HVSReview` | HVS review |
| `Boubert2018Revisiting` | Gaia-era reassessment template; closest in spirit to this paper |
| `Marchetti2019Fastest` | Gaia DR2 6D fastest-stars search |
| `Li2021HVS591` | one of three input catalogues (591 HiVels) |
| `Li2023ExtremeVelocity88` | one of three input catalogues (88 extreme velocity) |
| `Liao2024HVS519` | one of three input catalogues (519 HiVels) |

Optional secondary mentions for §1 (HVS survey context):
`Bromley2006EjectionVelocities`, `Brown2007BoundHVS`, `Kenyon2008HVSGCtoHalo`,
`Brown2014MMTSurvey`.

## §2 Data and sample construction (must-cite)

| key | role |
|---|---|
| `GaiaDR3Summary2023` | Gaia DR3 archive citation |
| `Cui2012LAMOST` | LAMOST telescope reference |
| `Zhao2012LAMOSTSurvey` | LAMOST survey overview |
| `Deng2012LEGUE` | LEGUE / Galactic-component survey plan |
| `Xiang2015LSP3` | LSP3 stellar-parameter pipeline (Teff/logg/[Fe/H]) |
| `Yan2022LAMOSTDecade` | LAMOST decadal overview |
| `Ochsenbein2000VizieR` | VizieR database service |
| `Ginsburg2019Astroquery` | astroquery (used to pull VizieR/Gaia/SIMBAD) |
| `Astropy2013` | astropy (coordinate transforms) |
| `Astropy2018` | astropy v2.0 update citation |

Use `Lindegren2021ParallaxBias` and `Luri2018GaiaParallaxes` here when
discussing parallax-quality cuts.

## §3 Methods (must-cite)

| key | role |
|---|---|
| `BailerJones2021Distances` | adopted geometric distances |
| `BailerJones2015Distances` | rationale for not using $1/\varpi$ |
| `Luri2018GaiaParallaxes` | parallax-use caveats |
| `Bovy2015galpy` | galpy `MWPotential2014`, escape velocity |

Optional methodological references in §3:
`Lindegren2021ParallaxBias` (parallax zero-point),
`McMillan2017MWMass` (alternative MW-mass model — for sensitivity),
`Piffl2014RAVEvesc`, `Monari2018Vesc` (escape-velocity literature anchor).

## §4 Results

`Elsanhoury2025CAOSPKinematics` — cite in §4.1/§4.3 as the most recent CAOSP
LAMOST+Gaia kinematic study against which we compare scope and methodology.
`Marchetti2019Fastest`, `Boubert2018Revisiting` — back-reference when
discussing how our headline 221 → 3 number contrasts with the Gaia DR2-era
estimates.

## §5 Discussion

| key | role |
|---|---|
| `Nelson2024ExtremeVelChem` | **Top-1 candidate context** — extreme-velocity-star chemistry |
| `Hattori2019LAMOSTHVS1` | LAMOST-HVS1 follow-up template |
| `Du2018LocalHalo` | Gaia + LAMOST high-velocity sample (independent) |
| `Du2018Origin` | high-velocity-star origins paper |
| `Li2020LateTypeHVS` | late-type / giant HVS candidates — relevant since Top-3 are giants |
| `Bromley2018NearbyHighSpeed` | Gaia DR2 high-speed stars |
| `Hawkins2018ChemicalTagging` | chemical tagging of fastest stars |
| `Quispe2024SPLUSHV` | recent S-PLUS HV characterization (optional) |
| `Piffl2014RAVEvesc` | escape-speed prior literature for caveats |
| `Monari2018Vesc` | Gaia-era escape speed |
| `McMillan2017MWMass` | alternative potential / mass model |

## Forbidden uses

- Do **not** cite `Brown2005FirstHVS` to claim "we discovered a new HVS".
  Brown+ 2005 is for Introduction context only.
- Do **not** mis-cite `Nelson2024ExtremeVelChem` as evidence that any
  specific Top-3 source is *confirmed*. Use it to provide chemistry-context
  framing only.

## Acknowledgements line (paste verbatim)

> This work has made use of data from the European Space Agency mission
> *Gaia* (\url{https://www.cosmos.esa.int/gaia}), processed by the
> *Gaia* Data Processing and Analysis Consortium. Funding for the DPAC has
> been provided by national institutions, in particular the institutions
> participating in the *Gaia* Multilateral Agreement. Guoshoujing Telescope
> (the Large Sky Area Multi-Object Fiber Spectroscopic Telescope, LAMOST) is
> a National Major Scientific Project built by the Chinese Academy of
> Sciences. This research has made use of the VizieR catalogue access tool,
> CDS, Strasbourg, France
> \citep{Ochsenbein2000VizieR}.
> Software: \texttt{astropy} \citep{Astropy2013, Astropy2018},
> \texttt{astroquery} \citep{Ginsburg2019Astroquery},
> \texttt{galpy} \citep{Bovy2015galpy}.

## Trim list (if word count over the regular-article limit)

If the manuscript needs to drop ~5 references to stay short, the safer
candidates to remove are:
1. `Quispe2024SPLUSHV` — tangential (different survey, included for breadth).
2. `Bromley2018NearbyHighSpeed` — superseded by `Marchetti2019Fastest`.
3. `Bromley2006EjectionVelocities` — theoretical background, optional.
4. `Du2018Origin` — duplicate of `Du2018LocalHalo` for our argument.
5. `Brown2014MMTSurvey` or `Brown2007BoundHVS` — keep one of the two.

That brings the bibliography from 40 down to ~35 entries, suitable for a
short CAOSP regular article.
