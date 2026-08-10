import json
import re
import secrets
import subprocess
from pathlib import Path
from ..config import settings

STATE = Path(settings.XRAY_CONFIG).parent / "reality.json"


def _parse_value(text: str, labels: list[str]) -> str:
    for raw in text.splitlines():
        line = raw.strip()
        for label in labels:
            if line.lower().startswith(label.lower() + ":"):
                return line.split(":", 1)[1].strip()
    return ""


def _parse_keypair(text: str):
    # Xray 26.6.x and newer changed the x25519 CLI output from
    # "Private key/Public key" to "PrivateKey/Password".
    private = _parse_value(text, ["PrivateKey", "Private key", "Private Key"])
    public = _parse_value(
        text,
        [
            "Password (PublicKey)",
            "Password (Public Key)",
            "PublicKey",
            "Public key",
            "Public Key",
            "Password",
        ],
    )
    return private, public


def _run_x25519(private: str | None = None):
    cmd = [settings.XRAY_PATH, "x25519"]
    if private:
        cmd.extend(["-i", private])
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    output = (p.stdout or "") + (p.stderr or "")
    if p.returncode != 0:
        raise RuntimeError(output.strip() or "xray x25519 failed")
    return output


def _save(data: dict):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def ensure_reality_keypair():
    if settings.REALITY_PRIVATE_KEY and settings.REALITY_PUBLIC_KEY:
        return settings.REALITY_PRIVATE_KEY, settings.REALITY_PUBLIC_KEY

    STATE.parent.mkdir(parents=True, exist_ok=True)
    if STATE.exists():
        try:
            data = json.loads(STATE.read_text(encoding="utf-8"))
            if data.get("privateKey") and data.get("publicKey"):
                return data["privateKey"], data["publicKey"]
        except Exception:
            pass

    output = _run_x25519()
    private, public = _parse_keypair(output)

    # If a future Xray build prints only the private key, derive the public
    # key from the same private key instead of generating a second pair.
    if private and not public:
        output2 = _run_x25519(private)
        _, public = _parse_keypair(output2)

    if not private or not public:
        raise RuntimeError(
            "Unable to parse Xray x25519 output. Output was: "
            + output[-2000:]
        )

    _save({"privateKey": private, "publicKey": public})
    return private, public


def reality_parameters():
    private, public = ensure_reality_keypair()

    # Persist shortId as part of the same REALITY state. The previous version
    # regenerated it on every request, which could make generated client links
    # disagree with the running Xray configuration.
    data = {}
    if STATE.exists():
        try:
            data = json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    short_id = settings.REALITY_SHORT_ID or data.get("shortId") or secrets.token_hex(8)
    server_name = settings.REALITY_SERVER_NAME or data.get("serverName") or "www.microsoft.com"
    target = server_name if ":" in server_name else f"{server_name}:443"

    data.update({
        "privateKey": private,
        "publicKey": public,
        "shortId": short_id,
        "serverName": server_name,
        "target": target,
    })
    _save(data)

    return {
        "privateKey": private,
        "publicKey": public,
        "shortId": short_id,
        "serverName": server_name,
        "target": target,
    }
