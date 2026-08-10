import subprocess
import time
from pathlib import Path
from ..config import settings
from .validator import validate_config

class XrayManager:
    def __init__(self):
        self.process = None
        self.log_handle = None

    def available(self):
        return Path(settings.XRAY_PATH).exists()

    def start(self):
        if not self.available():
            return {"status": "unavailable", "error": f"Xray not found: {settings.XRAY_PATH}"}
        if self.process and self.process.poll() is None:
            return {"status": "running", "pid": self.process.pid}
        if not Path(settings.XRAY_CONFIG).exists():
            return {"status": "stopped", "error": "Xray config does not exist"}

        test = validate_config()
        if not test["success"]:
            return {"status": "error", "error": test["output"][-6000:]}

        Path(settings.XRAY_LOG).parent.mkdir(parents=True, exist_ok=True)
        self.log_handle = open(settings.XRAY_LOG, "a", buffering=1)
        self.process = subprocess.Popen(
            [settings.XRAY_PATH, "run", "-config", settings.XRAY_CONFIG],
            stdout=self.log_handle,
            stderr=self.log_handle,
            start_new_session=True,
        )
        time.sleep(0.35)
        if self.process.poll() is not None:
            code = self.process.returncode
            try:
                self.log_handle.flush()
            except Exception:
                pass
            return {"status": "error", "exit_code": code, "error": self._tail_log()}
        return {"status": "running", "pid": self.process.pid}

    def _tail_log(self):
        try:
            p = Path(settings.XRAY_LOG)
            return p.read_text(errors="replace")[-6000:] if p.exists() else ""
        except Exception:
            return ""

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        if self.log_handle:
            try:
                self.log_handle.close()
            except Exception:
                pass
            self.log_handle = None
        return {"status": "stopped"}

    def restart(self):
        self.stop()
        return self.start()

    def status(self):
        if self.process and self.process.poll() is None:
            return {"status": "running", "pid": self.process.pid}
        code = self.process.returncode if self.process else None
        result = {"status": "stopped", "exit_code": code}
        if code not in (None, 0):
            result["error"] = self._tail_log()
        return result

manager = XrayManager()
