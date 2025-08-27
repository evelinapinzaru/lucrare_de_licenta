import os
import sys
import time
import pathlib
import subprocess
import signal

ROOT = pathlib.Path(__file__).parent.resolve()
APP_ROOT = ROOT / "aplicatie_web"
BACKEND = APP_ROOT / "backend"
FRONTEND = APP_ROOT / "frontend"
CERTS = APP_ROOT / "certs"

CERT = CERTS / "dev-cert.pem"
KEY = CERTS / "dev-key.pem"

BACKEND_PORT = os.getenv("PORT", "8081")
FRONTEND_PORT = os.getenv("FRONTEND_PORT", "5173")

CREATE_NEW_PROCESS_GROUP = 0x00000200

env = os.environ.copy()
env.setdefault("VITE_API_BASE_URL", f"https://localhost:{BACKEND_PORT}")

def spawn(cmd: list[str], cwd: str) -> subprocess.Popen:
    if os.name == "nt":
        return subprocess.Popen(cmd, cwd=cwd, env=env, creationflags=CREATE_NEW_PROCESS_GROUP)
    return subprocess.Popen(cmd, cwd=cwd, env=env, preexec_fn=os.setsid)

def pnpm_cmd() -> list[str]:
    return ["npm.cmd", "exec", "pnpm"] if os.name == "nt" else ["npm", "exec", "pnpm"]

def graceful_stop(p: subprocess.Popen) -> None:
    if p.poll() is not None:
        return

    try:
        if os.name == "nt":
            os.kill(p.pid, signal.CTRL_BREAK_EVENT)  # works on Windows
        else:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
    except PermissionError as e:
        print(f"[warn] No permission to signal PID {p.pid}: {e}")
    except OSError as e:
        print(f"[warn] OS error signaling PID {p.pid}: {e}")

def force_stop(p: subprocess.Popen) -> None:
    if p.poll() is not None:
        return
    try:
        p.terminate()
    except (ProcessLookupError, PermissionError) as e:
        print(f"[warn] terminate failed for PID {p.pid}: {e}")
    except OSError as e:
        print(f"[warn] OS error on terminate for PID {p.pid}: {e}")

    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(p.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False
            )
        else:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass
    except FileNotFoundError:
        print("[warn] 'taskkill' not found on PATH")
    except PermissionError as e:
        print(f"[warn] No permission to hard-kill PID {p.pid}: {e}")
    except OSError as e:
        print(f"[warn] OS error hard-killing PID {p.pid}: {e}")


def main() -> int:
    if not (CERT.exists() and KEY.exists()):
        print(f"[start] Missing TLS certs:\n  {CERT}\n  {KEY}\nCreate them and retry.")
        return 1

    backend_cmd = [
        sys.executable, "-m", "uvicorn", "main:app", "--reload",
        "--port", BACKEND_PORT,
        "--ssl-certfile", str(CERT),
        "--ssl-keyfile",  str(KEY),
    ]

    frontend_cmd = pnpm_cmd() + ["run", "dev"]

    procs = [
        spawn(backend_cmd, str(BACKEND)),
        spawn(frontend_cmd, str(FRONTEND)),
    ]

    print(f"[start] Backend : https://localhost:{BACKEND_PORT}")
    print(f"[start] Frontend: https://localhost:{FRONTEND_PORT}  (set in vite.config.ts)")

    try:
        while True:
            if any(p.poll() is not None for p in procs):
                break
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n[stop] Caught Ctrl+C, shutting down...")
    finally:
        for p in procs:
            graceful_stop(p)

        deadline = time.time() + 5.0
        while time.time() < deadline and any(p.poll() is None for p in procs):
            time.sleep(0.1)

        for p in procs:
            force_stop(p)

        for p in procs:
            try:
                p.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                pass

    return 0

if __name__ == "__main__":
    raise SystemExit(main())