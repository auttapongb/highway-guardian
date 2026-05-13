#!/usr/bin/env python3
"""
HWAY GUARDIAN 2.0 — One-command setup for prototype.
"""

import subprocess
import sys
import os

BANNER = """
╔══════════════════════════════════════════════╗
║        HWAY GUARDIAN 2.0 — ทางหลวงพิทักษ์     ║
║   AI Edge Safety + Maintenance + Citizen     ║
║   DOH Hackathon 2026 · C3+C4+C6             ║
╚══════════════════════════════════════════════╝
"""


def run(cmd, check=True, capture=True):
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if result.stdout and capture:
        for line in result.stdout.strip().split('\n')[:5]:
            print(f"    {line}")
    if result.returncode != 0 and check:
        print(f"  ✗ ERROR: {result.stderr[:300] if capture else 'see above'}")
        sys.exit(1)
    return result


def main():
    print(BANNER)
    print("Setting up HWAY GUARDIAN prototype...\n")

    # 1. Check prerequisites
    print("[1/6] Checking prerequisites...")
    run("python3 --version")
    run("pip3 --version")
    run("docker --version", check=False)
    run("docker compose version", check=False)

    # 2. Install Python dependencies
    print("\n[2/6] Installing Python dependencies...")
    run("pip3 install -r backend/requirements.txt", check=False)
    run("pip3 install flask requests gunicorn", check=False)

    # 3. Check for .env
    print("\n[3/6] Checking configuration...")
    if os.path.exists(".env"):
        print("  ✓ .env file found")
    else:
        print("  ⚠ No .env found — copying from .env.example")
        if os.path.exists(".env.example"):
            run("cp .env.example .env")
        else:
            print("  ! Create .env with LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET")

    # 4. Create directories
    print("\n[4/6] Creating directories...")
    for d in ["uploads", "models", "data/sample-footage"]:
        os.makedirs(d, exist_ok=True)
        print(f"  ✓ {d}/")

    # 5. Download sample models (placeholder)
    print("\n[5/6] Model setup...")
    print("  ℹ In production, download Hailo-compiled YOLOv11 models:")
    print("    - models/pothole_yolov11n_seg.hailo (road surface defect model)")
    print("    - models/safety_yolov11n.hailo (safety incident model)")
    print("    - For demo: using OpenCV fallback detection")

    # 6. Print next steps
    print("\n[6/6] Setup complete! 🎉")
    print("=" * 50)
    print("\nQuick Start:")
    print("  # Start all services with Docker:")
    print("  docker compose up -d")
    print()
    print("  # Or run individually:")
    print("  python backend/main.py &          # API at http://localhost:8000")
    print("  python line-bot/bot.py &          # LINE webhook at :5000/callback")
    print("  # Open dashboard/index.html       # Map dashboard")
    print()
    print("  # Test edge AI (with webcam):")
    print("  python ai-engine/detect.py")
    print()
    print("  # API documentation:")
    print("  http://localhost:8000/docs")
    print()
    print("  # LINE OA webhook URL:")
    print("  https://your-server.com/callback")
    print()
    print("  # Submit: 5-min video + 10-slide PDF")
    print("  # Deadline: 31 May 2026")


if __name__ == "__main__":
    main()
