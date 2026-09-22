#!/usr/bin/env python3
"""Rotation/generazione chiavi API Asgard (P0).

Genera chiavi forti con secrets.token_urlsafe e:
  --check   esce 1 se trova default deboli (asgard-*-key) o chiavi corte in
            env o nei compose (fail-fast in prod, non in dev).
  --write FILE  scrive/aggiorna le chiavi in FILE (default .env) senza
            mai stamparle nei log oltre la prima generazione.

Chiavi gestite: RAGNAROK_API_KEY, RAGNAROK_AUTH_SECRET, HEIMDALL_API_KEY,
GJALLARHORN_API_KEY, BIFROST_API_KEY, MJOLNIR_API_KEY, YGGDRASIL_API_KEY,
FENRIR_API_KEY, SLEIPNIR_API_KEY.
"""
import argparse
import os
import re
import secrets
import sys

KEYS = [
    "RAGNAROK_API_KEY",
    "RAGNAROK_AUTH_SECRET",
    "HEIMDALL_API_KEY",
    "GJALLARHORN_API_KEY",
    "BIFROST_API_KEY",
    "MJOLNIR_API_KEY",
    "YGGDRASIL_API_KEY",
    "FENRIR_API_KEY",
    "SLEIPNIR_API_KEY",
]

# Default deboli spediti nei compose come placeholder (mai usare in prod).
# Pattern non ancorato: compare dentro ${VAR:-asgard-xxx-key} o come literal.
WEAK_RE = re.compile(r"asgard-[a-z][a-z-]*key\b", re.IGNORECASE)
# I placeholder ufficiali del repo dev (asgard-*-key) quando dichiarati come
# tali: --check-files --allow-dev-placeholders li accetta, blocca il resto.
WEAK_PLACEHOLDER_RE = re.compile(r"^asgard-[a-z][a-z-]*key$", re.IGNORECASE)


def is_weak(value: str | None) -> bool:
    if value is None:
        return True
    v = value.strip().strip('"').strip("'")
    if len(v) < 32:
        return True
    return bool(WEAK_RE.match(v))


def generate_key(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)


def check_env() -> list[str]:
    """Ritorna la lista delle chiavi deboli/mancanti (env + compose default)."""
    weak = []
    for k in KEYS:
        if is_weak(os.environ.get(k)):
            weak.append(k)
    return weak


def check_compose_defaults(allow_dev_placeholders: bool = False) -> list[str]:
    """Scansiona docker-compose*.yml per default weak hardcoded nei compose.

    Un gate CI deve fallire quando il codice committato contiene chiavi deboli
    (il deploy le prenderebbe), NON quando l'ambiente di build è semplicemente
    privo di `.env` (caso normale di CI). I default `${VAR:-asgard-xxx-key}`
    e i literal `asgard-*.key` nei compose sono il segnale che ci sta scivolando
    dentro un placeholder di sviluppo.

    Con allow_dev_placeholders=True i marker DIVULGATI del repo ufficiale
    (asgard-*-key, dichiarati DEV nei commenti dei compose) sono accettati;
    tutto il resto (chiavi corti, "change-this-*", valori lunghi hardcoded)
    fa fallire il gate, così il CI non si rompe sui placeholder ufficiali
    mentre blocca i leak veri.
    """
    import glob

    weak: list[str] = []
    for f in sorted(glob.glob(os.path.join("docker-compose*.yml"))) + sorted(
        glob.glob(os.path.join("monitoring", "docker-compose*.yml"))
    ):
        try:
            text = open(f, encoding="utf-8").read()
        except OSError:
            continue
        for m in WEAK_RE.finditer(text):
            val = m.group(0).strip().strip('"').strip("'")
            if not val:
                continue
            if allow_dev_placeholders and WEAK_PLACEHOLDER_RE.fullmatch(val):
                continue
            weak.append(f"{os.path.basename(f)}:{val}")
    return sorted(set(weak))


def upsert_env_file(path: str, only_missing: bool = True) -> dict:
    existing: dict[str, str] = {}
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^\s*([A-Z_]+)=(.*)\s*$", line)
                if m:
                    existing[m.group(1)] = m.group(2)
    updated = {}
    for k in KEYS:
        cur = existing.get(k, "")
        if only_missing and not is_weak(cur):
            continue
        updated[k] = generate_key(48 if "SECRET" in k else 32)
        existing[k] = updated[k]
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Asgard keys — generato da scripts/rotate_keys.py. NON committare.\n")
        for k in KEYS:
            if k in existing:
                f.write(f"{k}={existing[k]}\n")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return updated


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fallisce se chiavi deboli in env")
    ap.add_argument("--check-files", action="store_true", help="fallisce se i compose contengono default deboli (gate CI)")
    ap.add_argument(
        "--allow-dev-placeholders",
        action="store_true",
        help="con --check-files accetta i marker DEV ufficiali asgard-*-key (blocca il resto)",
    )
    ap.add_argument("--write", default=None, metavar="FILE", help="scrive chiavi forti in FILE")
    ap.add_argument("--only-missing", action="store_true", default=True)
    a = ap.parse_args()
    if a.check:
        weak = check_env()
        if weak:
            print(f"WEAK KEYS: {', '.join(weak)} (imposta var env forti >=32ch, vedi scripts/rotate_keys.py --write .env)", file=sys.stderr)
            return 1
        print("OK: nessuna chiave debole in env.")
        return 0
    if a.check_files:
        weak = check_compose_defaults(allow_dev_placeholders=a.allow_dev_placeholders)
        if weak:
            print(
                "WEAK DEFAULTS IN COMPOSE: "
                + ", ".join(weak)
                + " (sostituire con ${VAR} senza fallback, oppure forzare il valore via .env/sec. Vedi scripts/rotate_keys.py --write .env)",
                file=sys.stderr,
            )
            return 1
        print("OK: nessun default debole nei docker-compose.yml.")
        return 0
    if a.write:
        updated = upsert_env_file(a.write, only_missing=a.only_missing)
        print(f"Aggiornate {len(updated)} chiavi in {a.write}: {', '.join(sorted(updated)) or 'nessuna (già forti)'}")
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
