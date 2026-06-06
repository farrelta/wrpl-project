"""
TicketHub — Launch both microservices simultaneously.

Usage:
    python run_all.py

Starts:
    - TicketHub Core on port 5001
    - PayVault on port 5002
"""

import subprocess
import sys
import os
import signal
import time

# Ensure emoji/unicode prints correctly on Windows consoles
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

services = [
    {
        "name": "PayVault",
        "port": 5002,
        "cwd": os.path.join(BASE_DIR, "payvault"),
        "cmd": [sys.executable, "app.py"],
    },
    {
        "name": "TicketHub Core",
        "port": 5001,
        "cwd": os.path.join(BASE_DIR, "tickethub_core"),
        "cmd": [sys.executable, "app.py"],
    },
]

processes = []


def start_services():
    """Start all microservices."""
    print("=" * 60)
    print("  🎫  TicketHub — Starting All Services")
    print("=" * 60)
    print()

    for svc in services:
        print(f"  ▸ Starting {svc['name']} on port {svc['port']}...")
        proc = subprocess.Popen(
            svc["cmd"],
            cwd=svc["cwd"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        processes.append((svc["name"], proc))
        time.sleep(1)  # small delay to let the service bind

    print()
    print("  ✅ All services started!")
    print()
    print("  ┌──────────────────────────────────────────┐")
    print("  │  TicketHub Core:  http://localhost:5001   │")
    print("  │  PayVault API:    http://localhost:5002   │")
    print("  └──────────────────────────────────────────┘")
    print()
    print("  Press Ctrl+C to stop all services.")
    print()


def stop_services():
    """Gracefully stop all services."""
    print("\n  🛑 Stopping all services...")
    for name, proc in processes:
        proc.terminate()
        try:
            proc.wait(timeout=5)
            print(f"  ✓ {name} stopped.")
        except subprocess.TimeoutExpired:
            proc.kill()
            print(f"  ✗ {name} killed (forced).")
    print("  Done. Goodbye!")


def main():
    start_services()
    try:
        # Stream output from all processes
        while True:
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"\n  ⚠️  {name} exited with code {proc.returncode}")
                    stop_services()
                    sys.exit(1)
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_services()


if __name__ == "__main__":
    main()
