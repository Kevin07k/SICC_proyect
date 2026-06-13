#!/usr/bin/env python3
"""Aplica o completa el seed demo MongoDB (5 incidentes + 5 activos por sede). Idempotente."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

MONGO_API_USER = os.getenv("MONGO_SC_USER", "sicc_mongo_api")
MONGO_API_PASS = os.getenv("MONGO_SC_PASSWORD", "sicc_mongo_api_pass_2024")


def _run_mongosh_local(host: str, port: str, db: str, script: Path) -> None:
    uri = f"mongodb://{MONGO_API_USER}:{MONGO_API_PASS}@{host}:{port}/{db}?authSource=admin"
    subprocess.run(["mongosh", uri, "--quiet", str(script)], check=True)


def _run_mongosh_docker(service: str, db: str, script_in_container: str) -> None:
    uri = (
        f"mongodb://{MONGO_API_USER}:{MONGO_API_PASS}@localhost:27017/{db}?authSource=admin"
    )
    subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            service,
            "mongosh",
            uri,
            "--quiet",
            script_in_container,
        ],
        cwd=ROOT,
        check=True,
    )


def main() -> int:
    sc_script = ROOT / "mongo" / "santa_cruz" / "02_seed.js"
    cb_script = ROOT / "mongo" / "cochabamba" / "02_seed.js"
    if not sc_script.exists() or not cb_script.exists():
        print("ERROR: faltan mongo/*/02_seed.js", file=sys.stderr)
        return 1

    use_docker = not shutil.which("mongosh")
    if use_docker:
        print("mongosh no en PATH; usando docker compose exec...")

    print("Aplicando seed Mongo Santa Cruz...")
    if use_docker:
        _run_mongosh_docker("mongo-santa-cruz", "sicc_sc", "/docker-entrypoint-initdb.d/02_seed.js")
    else:
        _run_mongosh_local(
            os.getenv("MONGO_SC_HOST", "localhost"),
            os.getenv("MONGO_SC_PORT", "27017"),
            "sicc_sc",
            sc_script,
        )

    print("Aplicando seed Mongo Cochabamba...")
    if use_docker:
        _run_mongosh_docker("mongo-cochabamba", "sicc_cb", "/docker-entrypoint-initdb.d/02_seed.js")
    else:
        _run_mongosh_local(
            os.getenv("MONGO_CB_HOST", "localhost"),
            os.getenv("MONGO_CB_PORT", "27018"),
            "sicc_cb",
            cb_script,
        )

    print("\nListo. Cada demo: evidencias + timeline (incidentes) y telemetría (activos).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
