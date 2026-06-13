#!/usr/bin/env python3
"""
Simula deadlock en PostgreSQL (Santa Cruz) con dos conexiones concurrentes.
Requiere: docker compose up, init_databases.py, apply_demo_seed.py

Uso:
  cd database
  .venv-init/bin/python scripts/simular_deadlock.py
  .venv-init/bin/python scripts/simular_deadlock.py --motor mysql
"""
from __future__ import annotations

import argparse
import os
import sys
import threading
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5432"))
PG_DB = os.getenv("PG_DB", "sicc_central")
PG_USER = os.getenv("PG_USER", "sicc_admin")
PG_PASSWORD = os.getenv("PG_PASSWORD", "sicc_pg_pass_2024")

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DB = os.getenv("MYSQL_DB", "sicc_cochabamba")
MYSQL_USER = os.getenv("MYSQL_USER", "sicc_admin")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "sicc_mysql_pass_2024")

UUID_A_PG = "b1000001-0001-4000-8000-000000000001"
UUID_B_PG = "b1000001-0001-4000-8000-000000000002"
UUID_A_MY = "b2000001-0001-4000-8000-000000000001"
UUID_B_MY = "b2000001-0001-4000-8000-000000000002"

results: dict[str, str] = {}
barrier = threading.Barrier(2)


def _run_pg_session(name: str, first_uuid: str, second_uuid: str) -> None:
    import psycopg

    conn = psycopg.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
        autocommit=False,
    )
    try:
        barrier.wait(timeout=10)
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE Activos SET propietario = %s WHERE uuid = %s",
                (f"{name} paso1", first_uuid),
            )
        time.sleep(0.3)
        barrier.wait(timeout=10)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE Activos SET propietario = %s WHERE uuid = %s",
                    (f"{name} paso2", second_uuid),
                )
            conn.commit()
            results[name] = "COMMIT OK"
        except Exception as exc:
            conn.rollback()
            results[name] = f"ROLLBACK: {exc}"
    finally:
        conn.close()


def _run_mysql_session(name: str, first_uuid: str, second_uuid: str) -> None:
    import pymysql

    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        autocommit=False,
    )
    try:
        barrier.wait(timeout=10)
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE Activos SET propietario = %s WHERE uuid = %s",
                (f"{name} paso1", first_uuid),
            )
        time.sleep(0.3)
        barrier.wait(timeout=10)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE Activos SET propietario = %s WHERE uuid = %s",
                    (f"{name} paso2", second_uuid),
                )
            conn.commit()
            results[name] = "COMMIT OK"
        except Exception as exc:
            conn.rollback()
            results[name] = f"ROLLBACK: {exc}"
    finally:
        conn.close()


def simular(motor: str) -> int:
    if motor == "postgres":
        uuid_a, uuid_b = UUID_A_PG, UUID_B_PG
        target = _run_pg_session
    else:
        uuid_a, uuid_b = UUID_A_MY, UUID_B_MY
        target = _run_mysql_session

    print(f"Simulando deadlock en {motor.upper()}...")
    print(f"  Sesión A: lock {uuid_a} -> luego {uuid_b}")
    print(f"  Sesión B: lock {uuid_b} -> luego {uuid_a}")

    t_a = threading.Thread(target=target, args=("A", uuid_a, uuid_b))
    t_b = threading.Thread(target=target, args=("B", uuid_b, uuid_a))
    t_a.start()
    t_b.start()
    t_a.join()
    t_b.join()

    print("\nResultado:")
    for key in ("A", "B"):
        print(f"  {key}: {results.get(key, 'sin resultado')}")

    deadlocked = any(
        "deadlock" in (results.get(k) or "").lower() or "1213" in (results.get(k) or "")
        for k in ("A", "B")
    )
    if deadlocked:
        print("\nOK: el motor detectó deadlock y abortó una transacción.")
        return 0
    print("\nAVISO: no se detectó deadlock (reintentar o verificar datos demo).")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Simular deadlock SICC")
    parser.add_argument(
        "--motor",
        choices=("postgres", "mysql"),
        default="postgres",
        help="Base de datos donde ejecutar la simulación",
    )
    args = parser.parse_args()
    try:
        return simular(args.motor)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
