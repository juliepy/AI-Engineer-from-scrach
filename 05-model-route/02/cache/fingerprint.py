import hashlib
import json


def request_fingerprint(system: str, user: str, model: str) -> str:
    raw = json.dumps({"system": system, "user": user, "model": model}, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
