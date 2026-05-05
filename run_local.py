#!/usr/bin/env python
"""
Quick start script for local development
Run: python run_local.py
"""
import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("PU MERIT SYSTEM - LOCAL DEVELOPMENT SERVER")
print("=" * 70)

# Ensure dependencies
print("\n[1/3] Checking dependencies...")
result = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"])
if result.returncode == 0:
    print("      Dependencies OK")
else:
    print("      ERROR installing dependencies")
    sys.exit(1)

# Run migrations
print("\n[2/3] Running migrations...")
result = subprocess.run([sys.executable, "manage.py", "migrate", "--noinput"])
if result.returncode == 0:
    print("      Migrations OK")
else:
    print("      ERROR with migrations")
    sys.exit(1)

# Collect static files
print("\n[3/3] Collecting static files...")
result = subprocess.run([sys.executable, "manage.py", "collectstatic", "--noinput"])
if result.returncode == 0:
    print("      Static files OK")
else:
    print("      Warning: Static files collection had issues")

print("\n" + "=" * 70)
print("STARTING DEVELOPMENT SERVER")
print("=" * 70)
print("\nAccess the application at:")
print("  Homepage:       http://localhost:8000/")
print("  Program Finder: http://localhost:8000/program-finder/")
print("  Admin Panel:    http://localhost:8000/admin/")
print("  Debug CSV:      http://localhost:8000/debug-csv/")
print("\nPress Ctrl+C to stop the server")
print("=" * 70 + "\n")

# Start the development server
subprocess.run([sys.executable, "manage.py", "runserver", "0.0.0.0:8000"])
