#!/usr/bin/env python
"""
Quick setup script for the PU Merit Recommendation System
Run: python setup.py
"""

import os
import sys
import subprocess


def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"📝 {description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}\n")
    try:
        result = subprocess.run(cmd, check=True)
        print(f"✅ {description} completed successfully!\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {description} failed!")
        return False


def main():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║   PU MERIT RECOMMENDATION SYSTEM - Setup Script              ║
    ║   Django Version                                             ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    # Check Python version
    print(f"🐍 Python Version: {sys.version.split()[0]}")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)

    # Install dependencies
    print("\n📦 Step 1: Installing dependencies...")
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                       "Pip install"):
        sys.exit(1)

    # Run migrations
    print("\n🗄️  Step 2: Running database migrations...")
    if not run_command([sys.executable, "manage.py", "migrate"], 
                       "Database migrations"):
        sys.exit(1)

    # Collect static files
    print("\n📂 Step 3: Collecting static files...")
    if not run_command([sys.executable, "manage.py", "collectstatic", "--noinput"], 
                       "Static files collection"):
        pass  # Don't exit if this fails

    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║   ✅ SETUP COMPLETE!                                         ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║  To start the development server, run:                      ║
    ║                                                              ║
    ║    python manage.py runserver                               ║
    ║                                                              ║
    ║  Then open http://localhost:8000 in your browser            ║
    ║                                                              ║
    ║  To create admin user:                                      ║
    ║                                                              ║
    ║    python manage.py createsuperuser                         ║
    ║    Then visit http://localhost:8000/admin                   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
