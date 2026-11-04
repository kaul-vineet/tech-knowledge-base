"""Capstone milestone 6 (optional agent assist): a LOCAL model explains each vetted candidate to the team.

Code has already decided (planet_candidate or rejected, with reasons). The model gets only the facts block.
Its text is published only if (a) every number in it is one of the facts and (b) it does not call a rejected
candidate a planet. Same gate as lesson 18's alert explanations.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "_agent"))
from client import chat  # noqa: E402

MARKER = "[[ASTRO-CANDIDATE]]"
SYSTEM = "You explain exoplanet-search results to a science team. You never change a verdict."


def facts_block(facts):
    return "\n".join(f"{k}: {v}" for k, v in facts.items())


def check(text, facts):
    known = {n for v in facts.values() for n in re.findall(r"\d+(?:\.\d+)?", str(v))}
    unverified = [n for n in re.findall(r"(?<![\w.])\d+(?:\.\d+)?", text) if n not in known]
    overclaim = facts["verdict"] != "planet_candidate" and bool(re.search(r"\b(is|it's) a planet\b", text, re.I))
    return unverified, overclaim


def explain(facts, base_url=None, model=None):
    text = chat([{"role": "system", "content": SYSTEM},
                 {"role": "user", "content": f"{MARKER} Explain this result in 2 sentences. "
                                             f"<facts>\n{facts_block(facts)}\n</facts>"}], base_url=base_url, model=model)
    unverified, overclaim = check(text, facts)
    return {"star": facts["star"], "verdict": facts["verdict"], "unverified": unverified, "overclaim": overclaim,
            "publish": not unverified and not overclaim, "text": text}
