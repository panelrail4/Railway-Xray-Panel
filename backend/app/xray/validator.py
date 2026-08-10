import subprocess
from pathlib import Path
from ..config import settings

def validate_config():
    if not Path(settings.XRAY_PATH).exists():
        return {"success": False, "output": f"Xray binary not found: {settings.XRAY_PATH}"}
    if not Path(settings.XRAY_CONFIG).exists():
        return {"success": False, "output": f"Xray config not found: {settings.XRAY_CONFIG}"}
    try:
        p = subprocess.run(
            [settings.XRAY_PATH, "run", "-test", "-config", settings.XRAY_CONFIG],
            capture_output=True, text=True, timeout=20
        )
    except Exception as e:
        return {"success": False, "output": str(e)}
    return {"success": p.returncode == 0, "output": (p.stdout or "") + (p.stderr or "")}
