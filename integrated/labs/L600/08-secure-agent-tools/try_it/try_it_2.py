"""Try it 2: an agent tries to WIDEN its own token by attenuating it with a bigger tool list."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adapters import T0, FakeClock  # noqa: E402
from capability import CapabilityError, TokenService, attenuate, parse, verify  # noqa: E402


def run():
    svc = TokenService(FakeClock(), root_key=b"\x08" * 32)
    token = svc.session_token("s-1", ["search_docs"], ttl=60)
    wider = attenuate(token, "tool in search_docs,send_email")  # no key needed to ADD a caveat ...
    try:
        verify(wider, svc.root_key, {"session": "s-1", "now": T0 + 1, "tool": "send_email", "args": {}})
        result = "accepted"
    except CapabilityError as err:  # ... but every caveat must hold, the old one included
        result = str(err)
    return {"caveats": parse(wider)[1], "send_email": result}


if __name__ == "__main__":
    print(run())
