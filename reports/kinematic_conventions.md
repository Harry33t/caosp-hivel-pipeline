# Kinematic conventions

This note documents the precise reference frames, sign conventions, and
solar parameters used by the kinematic computations in
`src/caosp_hivel/kinematics.py`, so that figures and discussion in the paper
are unambiguous.

## 1. Solar parameters

| quantity | value | source |
|---|---|---|
| $R_\odot$ (Galactocentric distance) | **8.122 kpc** | GRAVITY Collaboration (2018) |
| $z_\odot$ (height above mid-plane) | **0.0208 kpc** | Bennett & Bovy (2019) |
| $\vec v_\odot$ (Galactocentric Cartesian) | **(12.9, 245.6, 7.78) km/s** | Reid & Brunthaler (2020), Schönrich+ (2010) for peculiar component |

The solar Galactocentric velocity vector $(U_\odot, V_\odot, W_\odot)$ here is
*absolute*, not peculiar. It is the velocity of the Sun in the Galactocentric
frame: $V_\odot = V_\mathrm{LSR} + V_{\odot,\mathrm{pec}} \approx 233 + 12.6$.

## 2. Galactocentric frame (`R_gc`, `z_gc`, `v_esc`)

The columns `x_gc`, `y_gc`, `z_gc`, `R_gc`, `v_esc`, `v_over_vesc`,
`V_GSR`, `V_total` are computed via
`astropy.coordinates.Galactocentric` instantiated with the parameters above.
This frame is the standard right-handed Galactocentric Cartesian frame:

- $x_\mathrm{gc}$: from the Galactic centre toward the Sun
  (the Sun sits at $x_\mathrm{gc} = R_\odot \approx 8.12$ kpc).
- $y_\mathrm{gc}$: in the direction of Galactic rotation at the Sun's position.
- $z_\mathrm{gc}$: toward the North Galactic Pole.
- $R_\mathrm{gc} = \sqrt{x_\mathrm{gc}^2 + y_\mathrm{gc}^2}$ (cylindrical radius).
- $V_\mathrm{GSR} = \sqrt{v_x^2 + v_y^2 + v_z^2}$ (Galactic standard of rest
  speed magnitude — i.e., speed in the Galactocentric inertial frame).
- $v_\mathrm{esc}$ is the planar escape speed at the star's $R_\mathrm{gc}$
  under `galpy.potential.MWPotential2014`, evaluated in the disk plane
  ($z = 0$). $v_\mathrm{esc}(R_\odot) \approx 511$ km/s.
- `v_over_vesc` = $V_\mathrm{GSR} / v_\mathrm{esc}$.

Off-plane corrections to $v_\mathrm{esc}$ are small (a few percent) compared
to the spread of the high-velocity sample and are folded into the global
"potential model" systematic that the paper acknowledges.

## 3. Heliocentric Galactic Cartesian (`U`, `V`, `W`)

The columns `U`, `V`, `W`, `V_total` come from
`astropy.coordinates.SkyCoord(...).transform_to("galactic").velocity.d_x/d_y/d_z`.
The astropy `galactic` frame is **heliocentric**, i.e., Sun-centred, with the
same axis directions as the Galactocentric frame above:

- $U > 0$ toward the **Galactic centre**.
- $V > 0$ in the direction of **Galactic rotation** at the Sun.
- $W > 0$ toward the **North Galactic Pole**.

Important: these velocities are **NOT LSR-corrected**. They are the velocity
of the star in the Sun's instantaneous rest frame, expressed in Galactic
Cartesian axes. To convert to the Local Standard of Rest (LSR), one would
add the solar peculiar motion $(U_{\odot,\mathrm{pec}}, V_{\odot,\mathrm{pec}}, W_{\odot,\mathrm{pec}})$
$= (11.1, 12.24, 7.25)$ km/s (Schönrich+ 2010).

Numerically, on `final_kinematics_gaia_only_clean` (N=675 high-velocity
candidates) the heliocentric $V$ has median $\approx -328$ km/s. A halo
population at rest in the GSR frame would have heliocentric $V \approx -V_{\odot,y} \approx -245$ km/s; our sample is more negative because it is
explicitly pre-selected for high $V_\mathrm{GSR}$. For a typical disk star at
rest in the LSR, heliocentric $V \approx -V_{\odot,\mathrm{pec},y} \approx -12$ km/s,
not 0 — so when we say "LSR-uncorrected" we mean the ~12 km/s shift, not the
220 km/s shift of the rotation curve.

## 4. Toomre diagram (Fig. 4)

Axes: $V$ (heliocentric Galactic Cartesian, *not* LSR-corrected) versus
$\sqrt{U^2 + W^2}$. Reference circles at total peculiar speed
$v_\mathrm{tot,helio} = \sqrt{U^2 + V^2 + W^2}$ of 200, 300 and 500 km/s,
centred at $(V, \sqrt{U^2+W^2}) = (0, 0)$ — i.e., the heliocentric frame.

The 12-km/s LSR offset is far below the spread of the high-velocity sample
(typical $V$ scatter > 200 km/s), so the visual interpretation of the
Toomre figure (halo-like stars far from $V \approx -245$, disk-like stars
clustering nearer the Sun's reference) is robust.

If the paper requires an explicit LSR-frame Toomre figure, replace
$V \to V + 12.24$ km/s, $U \to U + 11.1$, $W \to W + 7.25$. We have not
applied this correction in the current figures.

## 5. RV conventions

- **Gaia DR3 `radial_velocity`**: heliocentric, in km/s. Used as the primary
  RV in Step 6B's MC.
- **LAMOST DR9 `rv`**: heliocentric, in km/s. LAMOST DR9 LRS is known to have
  a small zero-point (~−5 km/s; see Wang et al. 2024 and our Step 5
  cross-match summary, where median (LAMOST − Gaia) = −5.7 km/s in the
  common-RV subset). We do **not** apply a zero-point correction in the
  primary kinematic solution; the Step 6B sensitivity check (final strict,
  N=356) shows median $\Delta V_\mathrm{GSR} = 0.00$ km/s and p90
  $|\Delta V_\mathrm{GSR}| = 5.7$ km/s, so the zero-point bias does not
  propagate into a meaningful $V_\mathrm{GSR}$ change.

## 6. Suggested phrasing for the paper

> Velocities are computed with `astropy.coordinates.Galactocentric` using
> $R_\odot = 8.122$ kpc (GRAVITY Collaboration 2018), $z_\odot = 0.0208$ kpc
> (Bennett & Bovy 2019), and $\vec v_\odot = (12.9, 245.6, 7.78)$ km/s
> (Reid & Brunthaler 2020 with the Schönrich+ 2010 peculiar motion). The
> $(U, V, W)$ components reported in Table 3 and Fig. 4 are heliocentric
> Galactic Cartesian, with $U$ positive toward the Galactic centre, $V$
> positive toward Galactic rotation, and $W$ positive toward the North
> Galactic Pole. Peculiar motions relative to the LSR can be obtained by
> adding $(11.1, 12.24, 7.25)$ km/s; this offset is small compared with
> the velocity dispersion of our high-velocity sample. The Galactocentric
> speed $V_\mathrm{GSR}$ and the local escape speed $v_\mathrm{esc}$ at
> each star's $R_\mathrm{gc}$ under `galpy`'s `MWPotential2014`
> (Bovy 2015) are used for the unbound classification.
