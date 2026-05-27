import json
import re
from pathlib import Path

_FILTERS_PATH = Path(__file__).parent / "filters.json"


def _load() -> dict:
    if not _FILTERS_PATH.exists():
        return {"always_trash": {"senders": [], "domains": [], "subject_keywords": []}}
    with open(_FILTERS_PATH, encoding="utf-8") as f:
        return json.load(f)


def _sender_address(sender: str) -> str:
    """Extract bare email address from a From header like 'Name <addr>'."""
    match = re.search(r"<([^>]+)>", sender)
    return (match.group(1) if match else sender).lower().strip()


def _sender_domain(sender: str) -> str:
    addr = _sender_address(sender)
    return addr.split("@")[-1] if "@" in addr else ""


def is_trash(sender: str, subject: str, recipient: str = "") -> bool:
    """Return True if the email matches any always_trash rule."""
    rules = _load().get("always_trash", {})
    addr = _sender_address(sender)
    domain = _sender_domain(sender)
    subject_lower = subject.lower()

    if addr in [s.lower() for s in rules.get("senders", [])]:
        return True
    if domain in [d.lower() for d in rules.get("domains", [])]:
        return True
    for kw in rules.get("subject_keywords", []):
        if kw.lower() in subject_lower:
            return True
    # Check To address — useful for catching spam sent to known throwaway addresses
    if recipient:
        recip_addr = _sender_address(recipient)
        if recip_addr in [r.lower() for r in rules.get("recipients", [])]:
            return True
    return False
