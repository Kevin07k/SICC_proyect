#!/usr/bin/env python3
"""Aplica datos demo operacionales (5 activos + 5 incidentes por sede). Idempotente en PG."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Reutiliza runners de init_databases
sys.path.insert(0, str(ROOT))
from init_databases import _run_mysql_file, _run_psql_file  # noqa: E402


def main() -> int:
    pg = ROOT / "postgres" / "03_seed_demo_operacional.sql"
    my = ROOT / "mysql" / "03_seed_demo_operacional.sql"
    if not pg.exists() or not my.exists():
        print("ERROR: faltan archivos 03_seed_demo_operacional.sql", file=sys.stderr)
        return 1
    print("Aplicando demo PostgreSQL (Santa Cruz)...")
    _run_psql_file(pg)
    print("Aplicando demo MySQL (Cochabamba)...")
    _run_mysql_file(my)
    print("\nListo. Demo: 5 activos + 5 incidentes por sede (cada incidente vinculado a 1 activo).")
    print("Cochabamba: entrar como analista.cb@test.sicc (dev switch) o test123")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
