#!/usr/bin/env python3
"""
Carga masiva de incidentes para pruebas de optimización (EXPLAIN).
Genera volumen suficiente para contrastar Seq Scan vs Index Scan.

Uso:
  .venv-init/bin/python apply_benchmark_seed.py
  .venv-init/bin/python apply_benchmark_seed.py --count 12000 --noise-ratio 0.35
  .venv-init/bin/python apply_benchmark_seed.py --clear
"""
from __future__ import annotations

import argparse
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from init_databases import (  # noqa: E402
    MYSQL_DB,
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
    PG_DB,
    PG_HOST,
    PG_PASSWORD,
    PG_PORT,
    PG_USER,
    _table_exists_mysql,
    _table_exists_pg,
)

BENCH_PREFIX = "[Bench]"
ANALYST_PG = "11111111-1111-1111-1111-111111111102"
ANALYST_MY = "11111111-1111-1111-1111-111111111104"
SEDE_PG = 1
SEDE_MY = 2
BATCH = 500


def _clear_pg() -> int:
    import psycopg

    conn = psycopg.connect(
        host=PG_HOST,
        port=int(PG_PORT),
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM Incidentes WHERE titulo LIKE %s",
                (f"{BENCH_PREFIX}%",),
            )
            deleted = cur.rowcount
        conn.commit()
        return deleted
    finally:
        conn.close()


def _clear_mysql() -> int:
    import pymysql

    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=int(MYSQL_PORT),
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM Incidentes WHERE titulo LIKE %s",
                (f"{BENCH_PREFIX}%",),
            )
            deleted = cur.rowcount
        conn.commit()
        return deleted
    finally:
        conn.close()


def _insert_pg(*, primary: int, noise: int) -> None:
    import psycopg

    conn = psycopg.connect(
        host=PG_HOST,
        port=int(PG_PORT),
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
    )
    base = datetime(2024, 1, 1)
    try:
        with conn.cursor() as cur:
            n = 0
            rows: list[tuple] = []

            def flush() -> None:
                nonlocal rows, n
                if not rows:
                    return
                cur.executemany(
                    """
                    INSERT INTO Incidentes (
                        uuid, titulo, descripcion, id_tipo, id_prioridad, id_estado,
                        id_usuario_asignado, id_sede, created_at, updated_at, eliminado
                    ) VALUES (
                        %s::uuid, %s, %s, %s, %s, %s, %s::uuid, %s, %s, %s, FALSE
                    )
                    """,
                    rows,
                )
                n += len(rows)
                rows = []

            for i in range(primary):
                rows.append(
                    _row_pg(i, SEDE_PG, base, ANALYST_PG),
                )
                if len(rows) >= BATCH:
                    flush()
            for i in range(noise):
                rows.append(
                    _row_pg(primary + i, SEDE_MY, base, ANALYST_PG),
                )
                if len(rows) >= BATCH:
                    flush()
            flush()
        conn.commit()
        print(f"  PostgreSQL: {n} incidentes bench (sede {SEDE_PG}={primary}, ruido sede {SEDE_MY}={noise})")
    finally:
        conn.close()

    import psycopg

    conn = psycopg.connect(
        host=PG_HOST,
        port=int(PG_PORT),
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
    )
    try:
        with conn.cursor() as cur:
            cur.execute("ANALYZE Incidentes")
        conn.commit()
    finally:
        conn.close()


def _row_pg(i: int, id_sede: int, base: datetime, analyst: str) -> tuple:
    return (
        str(uuid.uuid4()),
        f"{BENCH_PREFIX} incidente {i:06d} sede {id_sede}",
        "Carga sintética para EXPLAIN ANALYZE",
        (i % 5) + 1,
        (i % 4) + 1,
        (i % 6) + 1,
        analyst,
        id_sede,
        base + timedelta(hours=i % 8760),
        base + timedelta(hours=i % 8760),
    )


def _insert_mysql(*, primary: int, noise: int) -> None:
    import pymysql

    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=int(MYSQL_PORT),
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
    )
    base = datetime(2024, 1, 1)
    try:
        with conn.cursor() as cur:
            n = 0
            rows: list[tuple] = []

            def flush() -> None:
                nonlocal rows, n
                if not rows:
                    return
                cur.executemany(
                    """
                    INSERT INTO Incidentes (
                        uuid, titulo, descripcion, id_tipo, id_prioridad, id_estado,
                        id_usuario_asignado, id_sede, created_at, updated_at, eliminado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
                    """,
                    rows,
                )
                n += len(rows)
                rows = []

            for i in range(primary):
                rows.append(_row_mysql(i, SEDE_MY, base, ANALYST_MY))
                if len(rows) >= BATCH:
                    flush()
            for i in range(noise):
                rows.append(_row_mysql(primary + i, SEDE_PG, base, ANALYST_MY))
                if len(rows) >= BATCH:
                    flush()
            flush()
        conn.commit()
        print(
            f"  MySQL: {n} incidentes bench (sede {SEDE_MY}={primary}, ruido sede {SEDE_PG}={noise})"
        )
    finally:
        conn.close()

    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=int(MYSQL_PORT),
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
    )
    try:
        with conn.cursor() as cur:
            cur.execute("ANALYZE TABLE Incidentes")
        conn.commit()
    finally:
        conn.close()


def _row_mysql(i: int, id_sede: int, base: datetime, analyst: str) -> tuple:
    ts = base + timedelta(hours=i % 8760)
    return (
        str(uuid.uuid4()),
        f"{BENCH_PREFIX} incidente {i:06d} sede {id_sede}",
        "Carga sintética para EXPLAIN ANALYZE",
        (i % 5) + 1,
        (i % 4) + 1,
        (i % 6) + 1,
        analyst,
        id_sede,
        ts,
        ts,
    )


def run_benchmark(
    *,
    count: int = 10_000,
    noise_ratio: float = 0.4,
    only: str = "all",
    clear: bool = False,
) -> int:
    noise = int(count * noise_ratio)

    if clear:
        if only in ("postgres", "all") and _table_exists_pg():
            print(f"PostgreSQL: eliminados {_clear_pg()} filas bench")
        if only in ("mysql", "all") and _table_exists_mysql():
            print(f"MySQL: eliminados {_clear_mysql()} filas bench")
        return 0

    print(
        f"Cargando benchmark (~{count} + {noise} ruido por nodo). "
        f"Requiere 02_seed aplicado."
    )
    if only in ("postgres", "all"):
        if not _table_exists_pg():
            print("ERROR: PostgreSQL sin esquema (init_databases.py primero)", file=sys.stderr)
            return 1
        _insert_pg(primary=count, noise=noise)
    if only in ("mysql", "all"):
        if not _table_exists_mysql():
            print("ERROR: MySQL sin esquema (init_databases.py primero)", file=sys.stderr)
            return 1
        _insert_mysql(primary=count, noise=noise)

    print("\nListo. Ejecutá optimizacion_explain.sql en cada motor (DataGrip o psql/mysql).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Carga masiva para benchmarks de optimización (EXPLAIN)"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10_000,
        help="Incidentes de la sede principal por nodo (default: 10000)",
    )
    parser.add_argument(
        "--noise-ratio",
        type=float,
        default=0.4,
        help="Fracción extra de otra sede (default: 0.4 → 40%% más filas)",
    )
    parser.add_argument(
        "--only",
        choices=("postgres", "mysql", "all"),
        default="all",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Borrar solo filas bench ([Bench]...) y salir",
    )
    args = parser.parse_args()
    return run_benchmark(
        count=args.count,
        noise_ratio=args.noise_ratio,
        only=args.only,
        clear=args.clear,
    )


if __name__ == "__main__":
    raise SystemExit(main())
