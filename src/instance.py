"""instance.py - synthetic blood-allocation instance (no real patient or donor data).

Story: a non-profit blood bank holds red-cell stock in 3 storage "lots" and receives
5 urgent requests from partner centres. Decide which request is served from which lot.
"""
from dataclasses import dataclass

# Red-cell ABO/Rh compatibility: donor blood group -> recipient groups that can receive it
COMPATIBLE = {
    "O-": {"O-", "O+", "A+", "B+", "AB+"},
    "O+": {"O+", "A+", "B+", "AB+"},
    "A+": {"A+", "AB+"},
    "B+": {"B+", "AB+"},
}

@dataclass(frozen=True)
class Lot:
    name: str
    blood: str      # blood group of the stock
    stock: int      # units available
    days_left: int  # days to expiry

@dataclass(frozen=True)
class Request:
    center: str
    blood: str      # recipient blood group needed
    units: int
    urgency: int    # 1 routine, 2 urgent, 3 critical

LOTS = [
    Lot("Hub-O+",   "O+", 3, 4),
    Lot("North-O-", "O-", 2, 9),
    Lot("East-A+",  "A+", 1, 2),
]

REQUESTS = [
    Request("City Hospital",      "A+", 2, 3),
    Request("Rural Clinic",       "O+", 1, 1),
    Request("Trauma Centre",      "O-", 2, 3),
    Request("Oncology Day Care",  "B+", 1, 2),
    Request("Maternity Ward",     "A+", 1, 3),
]

# distance in km, rows = lots, columns = requests (synthetic numbers)
DIST = [
    [5, 40, 8, 12, 6],
    [18, 55, 10, 20, 16],
    [14, 35, 22, 9, 55],
]

# Objective weights (the competing objectives). Tuned by hand; see ablation in the report.
W_SERVE = 3.0     # reward per (urgency x unit) delivered   -> serve the sickest first
W_EXPIRY = 1.5    # cost for using long-life stock          -> use soon-to-expire units first (less waste)
W_DIST = 1.0      # cost for normalised delivery distance   -> fast, cheap delivery
W_MISMATCH = 0.3  # cost for giving a non-identical group   -> keep exact matches where possible
W_UNIVERSAL = 1.5 # extra cost for spending scarce O- on a non-O- patient -> protect universal-donor stock

def compatible_options(r_idx):
    """Lots that can legally serve request r_idx (type-compatible and enough stock)."""
    r = REQUESTS[r_idx]
    return [l for l, lot in enumerate(LOTS)
            if r.blood in COMPATIBLE[lot.blood] and r.units <= lot.stock]

def assignment_cost(r_idx, l_idx):
    """Cost (lower is better) of serving request r_idx entirely from lot l_idx."""
    r, lot = REQUESTS[r_idx], LOTS[l_idx]
    max_days = max(x.days_left for x in LOTS)
    max_dist = max(max(row) for row in DIST)
    c = -W_SERVE * r.urgency * r.units
    c += W_EXPIRY * (lot.days_left / max_days) * r.units
    c += W_DIST * DIST[l_idx][r_idx] / max_dist
    if lot.blood != r.blood:
        c += W_MISMATCH * r.units
        if lot.blood == "O-":
            c += W_UNIVERSAL * r.units
    return c
