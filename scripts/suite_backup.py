#!/usr/bin/env python3
"""Backup centrale della suite Asgard (P0).

Raccoglie in un unico zip verificabile (manifest sha256) tutti gli store
SQLite dei moduli + un backup Ragnarok se disponibile:

  Heimdall/heimdall.db  Fenrir/fenrir.db  Gjallarhorn/gjallarhorn.db
  Ragnarok/backend/ragnarok_auth.db  ragnarok_audit.db
  Ragnarok/backend/backups/ragnarok_backup_*.zip (ultimo, opzionale)

Uso:
  python scripts/suite_backup.py --out backups [--keep 14] [--verify-only FILE]
"""
import argparse
import hashlib
import json
import os
import sys
import time
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CANDIDATES = [
    ("heimdall_db", "Heimdall/heimdall.db"),
    ("fenrir_db", "Fenrir/fenrir.db"),
    ("gjallarhorn_db", "Gjallarhorn/gjallarhorn.db"),
    ("ragnarok_auth_db", "Ragnarok/backend/ragnarok_auth.db"),
    ("ragnarok_audit_db", "Ragnarok/backend/ragnarok_audit.db"),
]

MANIFEST = "manifest.json"


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_stores(root: str = ROOT):
    found = []
    for label, rel in CANDIDATES:
        full = os.path.join(root, rel)
        if os.path.isfile(full):
            found.append((label, full))
    # Ultimo backup Ragnarok (già verificabile di suo, lo includiamo tal quale)
    bdir = os.path.join(root, "Ragnarok", "backend", "backups")
    if os.path.isdir(bdir):
        zips = sorted(f for f in os.listdir(bdir) if f.endswith(".zip"))
        if zips:
            found.append(("ragnarok_backup", os.path.join(bdir, zips[-1])))
    return found


def create_suite_backup(out_dir: str, keep: int = 14) -> dict:
    stores = collect_stores()
    if not stores:
        raise RuntimeError("Nessuno store trovato: esegui prima i moduli/Ragnarok.")
    os.makedirs(out_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, f"asgard_suite_backup_{ts}.zip")
    manifest = {"created_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "entries": {}}
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for label, full in stores:
            arc = f"{label}{os.path.splitext(full)[1]}"
            zf.write(full, arc)
            manifest["entries"][arc] = {"sha256": _sha256(full), "size": os.path.getsize(full)}
        zf.writestr(MANIFEST, json.dumps(manifest, indent=2))
    # Retention per conteggio
    if keep > 0:
        zips = sorted(f for f in os.listdir(out_dir) if f.startswith("asgard_suite_backup_") and f.endswith(".zip"))
        for old in zips[:-keep]:
            try:
                os.remove(os.path.join(out_dir, old))
            except OSError:
                pass
    return {"path": path, "stores": [lb for lb, _ in stores], "bytes": os.path.getsize(path)}


def verify_suite_backup(path: str) -> dict:
    if not os.path.isfile(path):
        raise RuntimeError(f"Backup non trovato: {path}")
    with zipfile.ZipFile(path, "r") as zf:
        if MANIFEST not in zf.namelist():
            raise RuntimeError("manifest.json mancante.")
        manifest = json.loads(zf.read(MANIFEST))
        bad, checked = [], 0
        for arc, meta in manifest["entries"].items():
            if arc not in zf.namelist():
                bad.append(f"missing: {arc}")
                continue
            if hashlib.sha256(zf.read(arc)).hexdigest() != meta["sha256"]:
                bad.append(f"corrupted: {arc}")
                continue
            checked += 1
    if bad:
        raise RuntimeError("Verifica fallita: " + "; ".join(bad))
    return {"verified": True, "checked": checked}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "backups"))
    ap.add_argument("--keep", type=int, default=14)
    ap.add_argument("--verify-only", default=None)
    a = ap.parse_args()
    try:
        if a.verify_only:
            print(json.dumps(verify_suite_backup(a.verify_only), indent=2))
        else:
            res = create_suite_backup(a.out, keep=a.keep)
            print(json.dumps(verify_suite_backup(res["path"]) | res, indent=2))
    except RuntimeError as e:
        print(f"ERRORE: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
