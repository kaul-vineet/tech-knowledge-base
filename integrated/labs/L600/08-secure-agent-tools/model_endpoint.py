"""Where the host may send model traffic: loopback only, unless the operator says otherwise (defence in depth).

Prompts carry the user's task, tool output and documents. A model URL that points off the machine sends all of that
across the network (plain HTTP to Ollama) and lets whoever runs that server choose the tool calls the policy will
see. The policy still decides every call, but where the data goes is decided here: anything that is not a loopback
address is refused unless allow_remote=True (run_project.py --allow-remote-model, injection_eval.py likewise).
The name "localhost" counts as loopback; other names are refused without a DNS lookup (a name can resolve anywhere).
"""
import ipaddress
from urllib.parse import urlsplit


class RemoteModelRefused(ValueError):
    pass


def host_of(url):
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise RemoteModelRefused(f"model URL must be http(s)://host[:port]/..., got {url!r}")
    return parts.hostname


def is_loopback(url):
    host = host_of(url)
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False  # a DNS name: do not resolve, do not trust


def check_model_url(url, allow_remote=False):
    """Return url if it may be used; raise RemoteModelRefused otherwise."""
    if is_loopback(url) or allow_remote:
        return url
    raise RemoteModelRefused(f"refusing non-loopback model URL {url!r}: prompts would leave this machine; "
                             f"pass --allow-remote-model if this is your trusted LAN model server")
