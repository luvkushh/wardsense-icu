#!/usr/bin/env python3
"""Unified Entrypoint for WardSense ICU (Web Server, Rich CLI Demo, and Pytest Suite)."""
import sys
import subprocess
import uvicorn
from src.config import settings
from src.database import init_db


def main() -> None:
    init_db()
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else "web"

    if cmd == "web":
        print(
            f"\n🏥 Launching WardSense ICU Platform at http://localhost:{settings.port}\n"
            f"   • Sign-In & Role Switcher : http://localhost:{settings.port}/login\n"
            f"   • Portal 1 (Hospital CMO) : http://localhost:{settings.port}/hospital\n"
            f"   • Portal 2 (Doctor MD)    : http://localhost:{settings.port}/doctor\n"
            f"   • Portal 3 (Nurse RN)     : http://localhost:{settings.port}/nurse\n"
        )
        uvicorn.run("src.server:app", host=settings.host, port=settings.port, reload=True)
    elif cmd in ("demo", "compare"):
        from src.cli_demo import run_terminal_demo
        run_terminal_demo()
    elif cmd == "test":
        raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", "-v"]))
    else:
        print("Usage: python3 run.py [web|demo|test]")


if __name__ == "__main__":
    main()
