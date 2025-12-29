import subprocess
import time
import psutil
import sys
import os


def start_application():
    """Start the application using the current Python executable."""
    project_root = os.path.abspath(os.path.dirname(__file__))
    cmd = [sys.executable, '-m', 'uvicorn', 'h3ru:app', '--host', '0.0.0.0', '--port', '8001']
    # If SSL env vars exist, pass them
    cert = os.environ.get('SSL_CERTFILE')
    key = os.environ.get('SSL_KEYFILE')
    if cert and key:
        cmd += ['--ssl-certfile', cert, '--ssl-keyfile', key]
    subprocess.Popen(cmd, cwd=project_root)


def is_application_running():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline') or []
            if any('uvicorn' in part for part in cmdline) and any('h3ru:app' in part for part in cmdline):
                return True
        except Exception:
            continue
    return False


if __name__ == '__main__':
    start_application()
    while True:
        time.sleep(600)
        if not is_application_running():
            start_application()