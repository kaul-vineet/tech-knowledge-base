"""Lesson 24 - ATAM-style analysis for Library Loans: a utility tree, prioritised scenarios, a trade-off point.

Utility tree leaves follow the SEI ATAM report: a concrete scenario (stimulus, environment, response measure)
ranked by (importance to the business, difficulty / risk for the architecture) on H/M/L.
"""
RANK = {"H": 3, "M": 2, "L": 1}

UTILITY_TREE = [
    # (quality attribute, refinement, scenario, importance, difficulty)
    ("availability", "dependency failure", "Identity provider is down; members already signed in can still renew loans; "
     "new sign-ins fail with a clear message within 2 s", "H", "M"),
    ("availability", "database failover", "Primary database fails at peak; service restored within 5 min, no committed loan lost", "H", "H"),
    ("performance", "latency", "POST /loans at peak (120 req/s): p99 <= 300 ms over 30 days", "H", "M"),
    ("modifiability", "new rule", "Add a 'max 2 new releases per member' rule in <= 1 person-day, "
     "touching only the loans module", "M", "L"),
    ("modifiability", "new adapter", "Swap SQLite for PostgreSQL without changing domain.py", "M", "M"),
    ("security", "tenant isolation", "A librarian of library A requests a loan of library B: 403 and a decision log entry, 100% of probes", "H", "M"),
    ("interaction capability", "inclusivity", "A screen-reader user completes 'borrow a book' with keyboard only; "
     "WCAG 2.2 AA checks for the flow pass", "H", "M"),
    ("flexibility", "scalability", "Grow from 400 to 800 libraries with p99 still <= 300 ms by adding instances only", "M", "H"),
]


def prioritise(leaves=UTILITY_TREE):
    """Sort by importance, then difficulty: (H,H) first - those are where ATAM spends analysis time."""
    return sorted(leaves, key=lambda leaf: (-RANK[leaf[3]], -RANK[leaf[4]], leaf[0]))


def weighted_score(scores, w):
    """Two criteria, weights (w, 1 - w)."""
    return w * scores[0] + (1 - w) * scores[1]


def break_even(x, y):
    """Weight w* in (0,1) where options x and y score the same, or None if one dominates for every w.

    D(w) = w*d1 + (1-w)*d2 with d = x - y is affine, so it has at most one root: w* = d2 / (d2 - d1).
    """
    d1, d2 = x[0] - y[0], x[1] - y[1]
    if d1 == d2:
        return None
    w = d2 / (d2 - d1)
    return w if 0 < w < 1 else None


# Two storage options for Library Loans scored 0..1 on (availability, simplicity/modifiability) - stated judgements.
SINGLE_SQLITE = (0.40, 0.90)
REPLICATED_POSTGRES = (0.95, 0.50)
