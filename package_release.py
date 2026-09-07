"""
Asgard Cyber Suite - Release Packaging & Distribution Builder v2.4.

Creates a clean, production-ready release package (.zip) ready for
commercial distribution to SMEs, MSPs, or GitHub Releases.
Excludes git histories, cache directories, temporary artifacts, and virtual environments.
Generates a SHA-256 integrity checksum manifest.
"""

import os
import sys
import zipfile
import hashlib
import time

IGNORE_DIRS = {
    ".git",
    ".github",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "node_modules",
    ".benchmarks",
    "output",
    "reports",
    "incidents",
    "target",
}

IGNORE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".log",
    ".db",
    ".sqlite",
    ".sqlite3",
}

def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def build_package():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(root_dir, "dist")
    os.makedirs(dist_dir, exist_ok=True)

    version = "2.4.0"
    zip_name = f"Asgard_Cyber_Suite_v{version}_Production_Release.zip"
    zip_path = os.path.join(dist_dir, zip_name)

    print("=" * 65)
    print(f"  Asgard Cyber Suite - Packaging Release v{version}")
    print("=" * 65)
    print(f"[*] Target Archive : {zip_path}")

    start_time = time.time()
    file_count = 0

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(root_dir):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]

            # Avoid packaging dist into itself
            if "dist" in root:
                continue

            for file in files:
                _, ext = os.path.splitext(file)
                if ext in IGNORE_EXTENSIONS:
                    continue

                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, root_dir)

                # Skip root temp / git files
                if rel_path.startswith(".") and not rel_path.startswith(".env.example"):
                    continue

                zf.write(full_path, arcname=os.path.join(f"Asgard_Suite_v{version}", rel_path))
                file_count += 1

    file_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    checksum = compute_sha256(zip_path)

    # Write checksum manifest
    checksum_file = os.path.join(dist_dir, f"{zip_name}.sha256")
    with open(checksum_file, "w", encoding="utf-8") as f:
        f.write(f"{checksum}  {zip_name}\n")

    elapsed = time.time() - start_time
    print(f"[+] Files Packaged : {file_count}")
    print(f"[+] Archive Size   : {file_size_mb:.2f} MB")
    print(f"[+] SHA-256 Hash   : {checksum}")
    print(f"[+] Time Elapsed   : {elapsed:.2f}s")
    print("=" * 65)
    print("[SUCCESS] Production release package built successfully!")
    print(f"Archive file: {zip_path}")
    print(f"Checksum file: {checksum_file}")

if __name__ == "__main__":
    build_package()
