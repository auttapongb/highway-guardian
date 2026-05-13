#!/usr/bin/env python3
"""
HWAY GUARDIAN 2.0 — Health Check & Demo Script
Verifies all services are running.
"""

import sys
import json
try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests


def check(name: str, url: str, expected_key: str = "status") -> bool:
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        status = data.get(expected_key, "unknown")
        ok = resp.ok and status in ("ok", "active")
        print(f"  {'✓' if ok else '✗'} {name}: {url} → {status}")
        return ok
    except Exception as e:
        print(f"  ✗ {name}: {url} → {e}")
        return False


def main():
    print("=" * 50)
    print("HWAY GUARDIAN 2.0 — Health Check")
    print("=" * 50)
    print()

    base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost"

    results = [
        check("Backend API", f"{base}:8000/", "status"),
        check("Backend Health", f"{base}:8000/health", "status"),
        check("LINE Bot", f"{base}:5000/", "status"),
        check("Dashboard", f"{base}:80", None),
    ]

    if len(sys.argv) > 2 and sys.argv[2] == "--demo":
        print("\n[Demo Mode] Simulating incidents...")
        demo_payloads = [
            {"type": "pothole", "severity": "high", "confidence": 0.92,
             "position": {"lat": 13.7563, "lon": 100.5018}, "vehicle_id": "DOH-DEMO"},
            {"type": "crack", "severity": "medium", "confidence": 0.78,
             "position": {"lat": 13.76, "lon": 100.52}, "vehicle_id": "DOH-DEMO"},
            {"type": "wrong_way", "severity": "critical", "confidence": 0.95,
             "position": {"lat": 13.75, "lon": 100.48}, "vehicle_id": "DOH-DEMO"},
        ]
        for i, payload in enumerate(demo_payloads):
            try:
                resp = requests.post(f"{base}:8000/api/incidents", json=payload, timeout=5)
                print(f"  ✓ Demo incident #{i+1}: {payload['type']} ({payload['severity']}) → {resp.status_code}")
            except Exception as e:
                print(f"  ✗ Demo incident #{i+1}: {e}")

        print("\nOpen dashboard at:", f"{base}:80")
        print("See all incidents at:", f"{base}:8000/api/incidents?limit=10")
        print("Heatmap data at:", f"{base}:8000/api/map/heatmap?hours=24")

    print()
    passed = sum(results)
    total = len(results)
    print(f"{'=' * 50}")
    print(f"Result: {passed}/{total} services healthy")
    print(f"{'=' * 50}")

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
