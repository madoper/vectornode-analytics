__anchor__ = "seed-data"

from backend.shared.data.codes import koap, nk, uk
from backend.shared.data.government import pp_rf_307, pp_rf_804
from backend.shared.data.laws import fz115, fz173, fz223, fz224, fz273
from backend.shared.data.regulations import (
    cbr_375p,
    cbr_430u,
    cbr_431p,
    cbr_444p,
    cbr_445p,
    cbr_499p,
)

ALL_SEED_FRAGMENTS = (
    fz115.FRAGMENTS
    + fz173.FRAGMENTS
    + fz223.FRAGMENTS
    + fz224.FRAGMENTS
    + fz273.FRAGMENTS
    + cbr_375p.FRAGMENTS
    + cbr_430u.FRAGMENTS
    + cbr_431p.FRAGMENTS
    + cbr_444p.FRAGMENTS
    + cbr_445p.FRAGMENTS
    + cbr_499p.FRAGMENTS
    + koap.FRAGMENTS
    + nk.FRAGMENTS
    + uk.FRAGMENTS
    + pp_rf_307.FRAGMENTS
    + pp_rf_804.FRAGMENTS
)
