"""Sky cross-matching with astropy. Pure functions — well covered by tests."""
from __future__ import annotations
from typing import Tuple
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
import astropy.units as u

from .config import settings


def match_radec(
    left: pd.DataFrame, right: pd.DataFrame,
    *, ra_l: str = "ra", dec_l: str = "dec",
    ra_r: str = "ra", dec_r: str = "dec",
    radius_arcsec: float | None = None,
    suffix: Tuple[str, str] = ("_l", "_r"),
) -> pd.DataFrame:
    """Inner join left & right on nearest sky neighbour within radius.

    Returns a dataframe with all columns from both sides (suffixed on collision)
    plus ``sep_arcsec``. Empty matches yield an empty dataframe with the right
    schema so downstream code never has to special-case it.
    """
    if radius_arcsec is None:
        radius_arcsec = float(settings()["crossmatch"]["radius_arcsec"])

    if len(left) == 0 or len(right) == 0:
        return pd.DataFrame()

    cl = SkyCoord(left[ra_l].values * u.deg, left[dec_l].values * u.deg, frame="icrs")
    cr = SkyCoord(right[ra_r].values * u.deg, right[dec_r].values * u.deg, frame="icrs")
    idx, sep, _ = cl.match_to_catalog_sky(cr)
    keep = sep.arcsec <= radius_arcsec

    l = left.loc[keep].reset_index(drop=True)
    r = right.iloc[idx[keep]].reset_index(drop=True)

    overlap = set(l.columns) & set(r.columns)
    l = l.rename(columns={c: c + suffix[0] for c in overlap})
    r = r.rename(columns={c: c + suffix[1] for c in overlap})

    out = pd.concat([l, r], axis=1)
    out["sep_arcsec"] = sep.arcsec[keep]
    return out
