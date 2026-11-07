#!/usr/bin/env python3
"""Main Entrypoint for SiteSense RFI: Zero-Rework Construction Agent."""
import sys
import uvicorn
from src.config import HOST, PORT


def print_help():
    print("""
SiteSense RFI - Zero-Rework Construction Agent
Powered by Vectorize Hindsight

Usage:
  python3 run.py web        Start the Web Dashboard and API server (http://localhost:8000)
  python3 run.py demo       Run the Rich CLI Interactive Simulation
  python3 run.py compare    View Stateless vs Hindsight side-by-side benchmark cases
  python3 run.py rfis       List all currently retained RFIs in memory
  python3 run.py test       Run automated verification test suite
  python3 run.py query "q"  Query the agent with custom field question
""")


def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd == "web":
        print(f"🚀 Starting SiteSense Web Server on http://{HOST}:{PORT} ...")
        uvicorn.run("src.server:app", host=HOST, port=PORT, reload=False)
    elif cmd in ["demo", "compare", "rfis", "query"]:
        from src.cli import main as cli_main
        sys.argv = [sys.argv[0]] + sys.argv[1:]
        cli_main()
    elif cmd == "test":
        import pytest
        sys.exit(pytest.main([]))
    else:
        print_help()


if __name__ == "__main__":
    main()
