"""Capstone milestone 6b (optional agent assist): a LOCAL model explains the staffing recommendation.

The agent never decides: code has already chosen the plan. Every number in the explanation is compared with
the facts code computed; anything else is UNVERIFIED and the explanation is not published until fixed.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parents[1] / "_shared" / "local_agent"))
from client import chat  # noqa: E402

MARKER = "[[SIM-STAFF]]"
SYSTEM = "You explain staffing recommendations to a service-centre manager. You never change the plan."
PROMPT = (f"{MARKER} Explain this staffing recommendation in at most 4 sentences for the centre manager. Quote "
          "only numbers from the facts.\n<facts>\n{facts}\n</facts>")


def facts_text(facts):
    return "\n".join(f"{k}: {v}" for k, v in facts.items())


def fake_staff_explainer(user_text):
    """Fake-model rule: a fluent explanation with one invented number (a 9% saving)."""
    found = dict(re.findall(r"^(\w+): (.+)$", user_text, re.M))
    return (f"The plan needs {found.get('plan_agent_hours')} agent-hours, against {found.get('erlang_c_agent_hours')} "
            f"for the Erlang C plan, a 9% saving. The peak is {found.get('peak_agents')} agents at 11:00. "
            f"Today's surge was detected at {found.get('alarm_clock')}, so {found.get('extra_agent_hours')} extra "
            "agent-hours are added for the afternoon.")


def use_fake_rule(fake_model_server):
    if (MARKER, fake_staff_explainer) not in fake_model_server.EXTRA_RULES:
        fake_model_server.EXTRA_RULES.append((MARKER, fake_staff_explainer))


def check_numbers(text, facts):
    known = set()
    for v in facts.values():
        known.update(re.findall(r"\d+(?:\.\d+)?", str(v)))
    tokens = re.findall(r"\d+(?:\.\d+)?", text)
    return [t for t in tokens if t in known], [t for t in tokens if t not in known]


def explain(facts, base_url=None, model=None):
    text = chat([{"role": "system", "content": SYSTEM},
                 {"role": "user", "content": PROMPT.replace("{facts}", facts_text(facts))}], base_url=base_url, model=model)
    ok, unverified = check_numbers(text, facts)
    return {"text": text, "verified": ok, "unverified": unverified, "publish": not unverified}
