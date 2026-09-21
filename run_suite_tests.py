#!/usr/bin/env python3
"""
Asgard Cyber Suite - Unified Test Runner & Verification Suite v2.4.0

Executes isolated test suites across all 9 cybersecurity modules:
  1. Heimdall (HIDS, Agent & Active Response)
  2. Mjolnir (Incident Response & Forensic Triage)
  3. Bifrost (Network Telemetry & Port Scanner)
  4. Yggdrasil (Identity, AD & Cloud M365 Security)
  5. Fenrir (Threat Intelligence & CTI Engine)
  6. Sleipnir (SOAR & Incident Automation)
  7. Forseti (Compliance NIS2, GDPR & DORA)
  8. Gjallarhorn (Centralized Alerting Hub)
  9. Ragnarök (AI SOC Orchestrator & RAG Engine)
"""

import os
import sys
import time
import argparse
import subprocess
from typing import List, Dict, Tuple, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ANSI Color Codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

MODULE_DEFINITIONS = [
    ("Heimdall", "HIDS & Active Response", "Heimdall/tests"),
    ("Mjolnir", "Forensic Triage & VirusTotal", "Mjolnir/tests"),
    ("Bifrost", "Network Scanner & Discovery", "Bifrost/tests"),
    ("Yggdrasil", "Identity, AD & Entra ID M365", "Yggdrasil/tests"),
    ("Fenrir", "Threat Intelligence CTI Engine", "Fenrir/tests"),
    ("Sleipnir", "SOAR Automation & Playbooks", "Sleipnir/tests"),
    ("Forseti", "Compliance NIS2 / GDPR / DORA", "Forseti/tests"),
    ("Gjallarhorn", "Centralized Alerting Hub", "Gjallarhorn/tests"),
    ("Ragnarok", "AI SOC Orchestrator & RAG", "Ragnarok/backend/tests"),
]

def check_local_dev_deps() -> None:
    """Pre-flight check for local (non-Docker) runs.

    Docker and CI install every module's requirements.txt automatically,
    but a local .venv created before a new dependency was added (e.g. msal
    for Yggdrasil's live Graph connector, yara-python for Mjolnir) fails
    with cryptic per-module errors. Warn early with the exact fix instead.
    Never blocks execution — CI/Docker already have everything.
    """
    missing = []
    for import_name, pip_name in (("msal", "msal"), ("yara", "yara-python")):
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)
    if missing:
        print(f"{YELLOW}[WARN] Dipendenze locali mancanti: {', '.join(missing)}{RESET}")
        print(f"{YELLOW}       Fix: .venv/Scripts/pip install {' '.join(missing)}{RESET}")
        print(f"{YELLOW}       (Docker/CI non sono affetti: installano già tutti i requirements.txt){RESET}\n")

def parse_pytest_output(stdout: str) -> Tuple[int, int, str]:
    """Extract passed test count, warning count, and last summary line."""
    lines = stdout.strip().split("\n")
    last_line = lines[-1] if lines else "No output"
    passed = 0
    warnings = 0
    import re
    passed_match = re.search(r"(\d+)\s+passed", last_line)
    if passed_match:
        passed = int(passed_match.group(1))
    warn_match = re.search(r"(\d+)\s+warning", last_line)
    if warn_match:
        warnings = int(warn_match.group(1))
    return passed, warnings, last_line

def run_suite(target_module: Optional[str] = None, verbose: bool = False) -> bool:
    root_dir = os.path.dirname(os.path.abspath(__file__))
    check_local_dev_deps()
    
    print(f"{CYAN}{BOLD}" + "=" * 75 + f"{RESET}")
    print(f"{CYAN}{BOLD}  🛡️  ASGARD CYBER SUITE — GLOBAL VERIFICATION TEST RUNNER v2.4.0{RESET}")
    print(f"{CYAN}{BOLD}" + "=" * 75 + f"{RESET}")
    print(f"{BOLD}Root Directory:{RESET} {root_dir}")
    print(f"{BOLD}Python Engine :{RESET} {sys.version.split()[0]} ({sys.executable})")
    print(f"{CYAN}" + "-" * 75 + f"{RESET}\n")

    modules_to_run = MODULE_DEFINITIONS
    if target_module:
        modules_to_run = [m for m in MODULE_DEFINITIONS if m[0].lower() == target_module.lower()]
        if not modules_to_run:
            print(f"{RED}[ERROR] Modulo '{target_module}' non trovato. Disponibili:{RESET}")
            for m in MODULE_DEFINITIONS:
                print(f"  - {m[0]}")
            return False

    results = []
    start_total = time.time()

    for name, desc, test_path in modules_to_run:
        full_test_path = os.path.join(root_dir, test_path)
        print(f"[{CYAN}RUNNING{RESET}] {BOLD}{name:12}{RESET} ({desc}) ... ", end="", flush=True)

        t0 = time.time()
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["ASGARD_ROOT"] = root_dir

        cmd = [sys.executable, "-m", "pytest", test_path, "-q"]
        if verbose:
            cmd.append("-v")

        proc = None
        for attempt in range(3):
            try:
                proc = subprocess.run(
                    cmd,
                    cwd=root_dir,
                    capture_output=True,
                    text=True,
                    env=env
                )
                break
            except PermissionError:
                time.sleep(0.5)
        if proc is None:
            proc = subprocess.run(cmd, cwd=root_dir, capture_output=True, text=True, env=env)
        duration = time.time() - t0

        passed, warnings, summary = parse_pytest_output(proc.stdout)
        success = (proc.returncode == 0)

        if success:
            print(f"{GREEN}{BOLD}PASSED{RESET} ({passed} test in {duration:.2f}s)")
            results.append((name, desc, True, passed, warnings, duration, None))
        else:
            print(f"{RED}{BOLD}FAILED{RESET} (in {duration:.2f}s)")
            err_msg = proc.stderr or proc.stdout
            results.append((name, desc, False, passed, warnings, duration, err_msg))

    total_time = time.time() - start_total

    # Summary Table
    print(f"\n{CYAN}{BOLD}" + "=" * 75 + f"{RESET}")
    print(f"{CYAN}{BOLD}  📊 ASGARD TEST SUITE EXECUTION SUMMARY{RESET}")
    print(f"{CYAN}{BOLD}" + "=" * 75 + f"{RESET}")
    print(f" {'MODULE':<14} {'ROLE / COMPONENT':<32} {'STATUS':<10} {'TESTS':<8} {'TIME':<8}")
    print(f" {'-'*12:<14} {'-'*30:<32} {'-'*8:<10} {'-'*6:<8} {'-'*6:<8}")

    total_tests = 0
    all_passed = True

    for name, desc, ok, count, warns, dur, err in results:
        status_str = f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"
        if not ok:
            all_passed = False
        total_tests += count
        print(f" {BOLD}{name:<14}{RESET} {desc:<32} {status_str:<19} {count:<8} {dur:.2f}s")

    print(f"{CYAN}" + "-" * 75 + f"{RESET}")
    status_banner = f"{GREEN}{BOLD}ALL TESTS PASSED (100% OPERATIONAL){RESET}" if all_passed else f"{RED}{BOLD}SOME TESTS FAILED{RESET}"
    print(f"  {BOLD}Total Modules:{RESET} {len(results)}  |  {BOLD}Total Tests:{RESET} {total_tests}  |  {BOLD}Duration:{RESET} {total_time:.2f}s")
    print(f"  {BOLD}Overall Status:{RESET} {status_banner}")
    print(f"{CYAN}{BOLD}" + "=" * 75 + f"{RESET}\n")

    # If any failures, print details
    if not all_passed:
        print(f"{RED}{BOLD}Detailed Failure Logs:{RESET}")
        for name, desc, ok, count, warns, dur, err in results:
            if not ok and err:
                print(f"\n{RED}--- {name} Failure ---{RESET}\n{err}\n")

    return all_passed

def install_all_requirements() -> bool:
    """Installa tutte le dipendenze dei 9 moduli nel Python corrente.

    Replica la logica di CI (.github/workflows/suite-ci.yml) e Dockerfile:
    ogni modulo è padrone del suo requirements.txt, qui li installiamo tutti
    in un comando solo. È il fix strutturale al bug di oggi (venv locale
    senza msal/yara-python mentre Docker/CI erano verdi).
    Uso: python run_suite_tests.py --setup
    """
    import glob
    root_dir = os.path.dirname(os.path.abspath(__file__))
    req_files = sorted(glob.glob(os.path.join(root_dir, "*", "requirements.txt")))
    for extra in ("Ragnarok/backend/requirements.txt", "Ragnarok/backend/requirements-rag.txt"):
        full = os.path.join(root_dir, extra)
        if full not in req_files and os.path.isfile(full):
            req_files.append(full)
    ok = True
    for req in req_files:
        rel = os.path.relpath(req, root_dir)
        print(f"[SETUP] pip install -r {rel} ... ", end="", flush=True)
        proc = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", req],
            cwd=root_dir,
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            print(f"{GREEN}OK{RESET}")
        else:
            ok = False
            print(f"{RED}FAILED{RESET}\n{proc.stderr or proc.stdout}")
    return ok

def main():
    parser = argparse.ArgumentParser(description="Asgard Cyber Suite - Global Test Runner")
    parser.add_argument("--module", "-m", help="Run tests only for a specific module (e.g. Heimdall, Yggdrasil)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose test execution output")
    parser.add_argument("--setup", action="store_true", help="Install all module requirements into the current Python env, then exit")
    args = parser.parse_args()

    if args.setup:
        success = install_all_requirements()
        sys.exit(0 if success else 1)

    success = run_suite(target_module=args.module, verbose=args.verbose)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
