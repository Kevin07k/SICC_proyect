#!/usr/bin/env python3
"""
Inicializa PostgreSQL (central) y MySQL (secundaria) con schema + seed.
Idempotente: omite nodos que ya tienen tablas, salvo con --force.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB", "sicc_central")
PG_USER = os.getenv("PG_USER", "sicc_admin")
PG_PASSWORD = os.getenv("PG_PASSWORD", "sicc_pg_pass_2024")

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "sicc_cochabamba")
MYSQL_USER = os.getenv("MYSQL_USER", "sicc_admin")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "sicc_mysql_pass_2024")
MYSQL_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD", "sicc_root_pass_2024")

def _default_mysql_fdw_host() -> str:
    explicit = os.getenv("MYSQL_FDW_HOST")
    if explicit:
        return explicit
    # FDW se ejecuta dentro del contenedor PG: nombre del servicio en docker-compose
    return "mysql-secundaria"


MYSQL_FDW_HOST = _default_mysql_fdw_host()
MYSQL_FDW_USER = os.getenv("MYSQL_FDW_USER", "sicc_fdw_ro")
MYSQL_FDW_PASSWORD = os.getenv("MYSQL_FDW_PASSWORD", "sicc_fdw_ro_pass_2024")


def _table_exists_pg() -> bool:
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
                """
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'cat_sedes'
                """
            )
            return cur.fetchone() is not None
    finally:
        conn.close()


def _table_exists_mysql() -> bool:
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
                """
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = %s AND table_name = 'cat_Sedes'
                """,
                (MYSQL_DB,),
            )
            return cur.fetchone() is not None
    finally:
        conn.close()


def _run_psql_file(sql_path: Path) -> None:
    psql = shutil.which("psql")
    env = {**os.environ, "PGPASSWORD": PG_PASSWORD}
    if psql:
        subprocess.run(
            [
                psql,
                "-h",
                PG_HOST,
                "-p",
                PG_PORT,
                "-U",
                PG_USER,
                "-d",
                PG_DB,
                "-v",
                "ON_ERROR_STOP=1",
                "-f",
                str(sql_path),
            ],
            check=True,
            env=env,
        )
        return

    import psycopg

    sql = sql_path.read_text(encoding="utf-8")
    conn = psycopg.connect(
        host=PG_HOST,
        port=int(PG_PORT),
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
    finally:
        conn.close()


def _docker_mysql_running() -> bool:
    docker = shutil.which("docker")
    if not docker:
        return False
    try:
        proc = subprocess.run(
            [
                docker,
                "compose",
                "-f",
                str(ROOT / "docker-compose.yml"),
                "ps",
                "--status",
                "running",
                "--services",
            ],
            capture_output=True,
            text=True,
            check=False,
            cwd=ROOT,
        )
        return proc.returncode == 0 and "mysql-secundaria" in proc.stdout
    except OSError:
        return False


def _run_mysql_cli(
    sql: str,
    *,
    user: str,
    password: str,
    database: str,
    via: str | None = None,
) -> str:
    """Ejecuta SQL con cliente mysql local o docker compose exec. Devuelve canal usado."""
    mysql_bin = shutil.which("mysql")
    if mysql_bin:
        subprocess.run(
            [
                mysql_bin,
                "-h",
                MYSQL_HOST,
                "-P",
                str(MYSQL_PORT),
                "-u",
                user,
                f"-p{password}",
                database,
            ],
            input=sql,
            text=True,
            check=True,
        )
        return via or "mysql-cli"

    if _docker_mysql_running():
        docker_bin = shutil.which("docker")
        assert docker_bin
        subprocess.run(
            [
                docker_bin,
                "compose",
                "-f",
                str(ROOT / "docker-compose.yml"),
                "exec",
                "-T",
                "mysql-secundaria",
                "mysql",
                "-u",
                user,
                f"-p{password}",
                database,
            ],
            input=sql,
            text=True,
            check=True,
            cwd=ROOT,
        )
        return "docker-exec"

    raise FileNotFoundError("mysql CLI no encontrado y contenedor mysql-secundaria no está activo")


def _split_mysql_delimiter(sql: str) -> list[str]:
    """Divide SQL con bloques DELIMITER $$ ... END$$ (compatible con pymysql)."""
    statements: list[str] = []
    current: list[str] = []
    delimiter = ";"

    for line in sql.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("DELIMITER "):
            if current:
                blob = "\n".join(current).strip()
                if blob:
                    statements.append(blob)
                current = []
            parts = stripped.split(maxsplit=1)
            delimiter = parts[1] if len(parts) > 1 else ";"
            continue

        current.append(line)
        if stripped.endswith(delimiter):
            blob = "\n".join(current).strip()
            if blob:
                statements.append(blob)
            current = []

    if current:
        blob = "\n".join(current).strip()
        if blob:
            statements.append(blob)
    return statements


def _mysql_statement_executable(stmt: str) -> bool:
    """True si el bloque tiene al menos una línea SQL (no solo comentarios)."""
    for line in stmt.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("--"):
            return True
    return False


def _run_mysql_pymysql(
    sql: str,
    *,
    user: str,
    password: str,
    database: str,
) -> None:
    import pymysql

    uses_delimiter = "DELIMITER" in sql.upper()
    statements = (
        _split_mysql_delimiter(sql) if uses_delimiter else _split_mysql_statements(sql)
    )
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=int(MYSQL_PORT),
        user=user,
        password=password,
        database=database,
    )
    try:
        with conn.cursor() as cur:
            for statement in statements:
                stmt = statement.strip()
                if not stmt or stmt.upper().startswith("USE "):
                    continue
                if not _mysql_statement_executable(stmt):
                    continue
                cur.execute(stmt)
        conn.commit()
    finally:
        conn.close()


def _run_mysql_file(
    sql_path: Path,
    *,
    user: str | None = None,
    password: str | None = None,
    database: str | None = None,
) -> None:
    db_user = user or MYSQL_USER
    db_password = password or MYSQL_PASSWORD
    db_name = database or MYSQL_DB
    sql = sql_path.read_text(encoding="utf-8")

    try:
        channel = _run_mysql_cli(
            sql,
            user=db_user,
            password=db_password,
            database=db_name,
        )
        if channel == "docker-exec":
            print(f"    ({sql_path.name} via Docker mysql-secundaria)")
        return
    except FileNotFoundError:
        print(
            f"    ({sql_path.name} via pymysql; sin mysql local — "
            "levanta: docker compose up -d)"
        )
    except subprocess.CalledProcessError:
        print(f"    ({sql_path.name} fallback pymysql tras error del cliente mysql)")

    _run_mysql_pymysql(
        sql,
        user=db_user,
        password=db_password,
        database=db_name,
    )


def _fdw_configured_pg() -> bool:
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
                """
                SELECT 1 FROM information_schema.foreign_tables
                WHERE foreign_table_schema = 'sucursal_cochabamba'
                LIMIT 1
                """
            )
            return cur.fetchone() is not None
    finally:
        conn.close()


def _render_fdw_sql() -> str:
    template = (ROOT / "postgres" / "05_fdw_mysql.sql.template").read_text(
        encoding="utf-8"
    )
    return (
        template.replace("__MYSQL_FDW_HOST__", MYSQL_FDW_HOST)
        .replace("__MYSQL_FDW_DB__", MYSQL_DB)
        .replace("__MYSQL_FDW_USER__", MYSQL_FDW_USER)
        .replace("__MYSQL_FDW_PASSWORD__", MYSQL_FDW_PASSWORD)
    )


def setup_distribuido(*, force_fdw: bool = False) -> None:
    """Usuarios SQL + FDW (idempotente). Requiere esquema ya creado."""
    if not _table_exists_pg():
        print("SKIP distribuido (PostgreSQL sin esquema; ejecuta init primero)")
        return
    if not _table_exists_mysql():
        print("SKIP distribuido (MySQL sin esquema; ejecuta init primero)")
        return

    print("Configurando usuarios SQL y FDW...")
    print("  mysql: 04_usuarios_sql.sql (root)...")
    _run_mysql_file(
        ROOT / "mysql" / "04_usuarios_sql.sql",
        user="root",
        password=MYSQL_ROOT_PASSWORD,
        database=MYSQL_DB,
    )
    print("  postgres: 04_usuarios_sql.sql...")
    _run_psql_file(ROOT / "postgres" / "04_usuarios_sql.sql")

    if force_fdw or not _fdw_configured_pg():
        print(f"  postgres: 05_fdw_mysql (host={MYSQL_FDW_HOST})...")
        fdw_path = ROOT / ".fdw_rendered.sql"
        fdw_path.write_text(_render_fdw_sql(), encoding="utf-8")
        try:
            _run_psql_file(fdw_path)
        finally:
            fdw_path.unlink(missing_ok=True)
        print("OK FDW mysql_sucursal_cochabamba -> sucursal_cochabamba")
    else:
        print("SKIP FDW (ya configurado; usa --force-fdw para reimportar)")

    print("OK distribuido")


def apply_academico_extensions() -> None:
    """Vistas, SP, triggers (06) y transacciones (07). Idempotente; requiere esquema y usuarios SQL."""
    pg_academico = (
        "06_vistas_procedimientos.sql",
        "07_transacciones.sql",
    )
    if _table_exists_pg():
        for name in pg_academico:
            print(f"  postgres: {name}...")
            _run_psql_file(ROOT / "postgres" / name)
        print("OK postgres academico")
    else:
        print("SKIP postgres academico (sin esquema)")

    if _table_exists_mysql():
        for name in pg_academico:
            print(f"  mysql: {name}...")
            # Triggers/SP con DELIMITER: root evita ERROR 1419 (binlog + triggers)
            _run_mysql_file(
                ROOT / "mysql" / name,
                user="root",
                password=MYSQL_ROOT_PASSWORD,
            )
        print("OK mysql academico")
    else:
        print("SKIP mysql academico (sin esquema)")


def _split_mysql_statements(sql: str) -> list[str]:
    """Divide SQL MySQL respetando DELIMITER básico (sin procedimientos aquí)."""
    parts: list[str] = []
    current: list[str] = []
    for line in sql.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("USE "):
            continue
        current.append(line)
        if stripped.endswith(";"):
            parts.append("\n".join(current))
            current = []
    if current:
        blob = "\n".join(current).strip()
        if blob:
            parts.append(blob)
    return parts


def init_postgres(force: bool) -> None:
    if not force and _table_exists_pg():
        print("SKIP postgres (esquema ya existe; usa --force para re-ejecutar)")
        return
    for name in ("01_schema.sql", "02_seed.sql"):
        path = ROOT / "postgres" / name
        print(f"  postgres: {name}...")
        _run_psql_file(path)
    print("OK postgres")


def init_mysql(force: bool) -> None:
    if not force and _table_exists_mysql():
        print("SKIP mysql (esquema ya existe; usa --force para re-ejecutar)")
        return
    schema_path = ROOT / "mysql" / "01_schema.sql"
    print("  mysql: 01_schema.sql...")
    _run_mysql_file(schema_path)
    seed_path = ROOT / "mysql" / "02_seed.sql"
    print("  mysql: 02_seed.sql...")
    _run_mysql_file(seed_path)
    print("OK mysql")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inicializar BDs SICC")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-ejecutar SQL aunque el esquema exista (puede fallar si hay datos)",
    )
    parser.add_argument(
        "--only",
        choices=("postgres", "mysql", "all"),
        default="all",
        help="Nodo a inicializar",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Tras init (o en BD existente), cargar 5 activos + 5 incidentes por sede",
    )
    parser.add_argument(
        "--benchmark",
        type=int,
        nargs="?",
        const=10_000,
        metavar="N",
        help="Carga masiva para EXPLAIN (default N=10000 por sede principal; requiere esquema)",
    )
    parser.add_argument(
        "--distribuido",
        action="store_true",
        help="Solo usuarios SQL + FDW (sin 01/02 schema)",
    )
    parser.add_argument(
        "--force-fdw",
        action="store_true",
        help="Recrear servidor FDW e importar tablas de MySQL",
    )
    parser.add_argument(
        "--skip-distribuido",
        action="store_true",
        help="No ejecutar usuarios SQL ni FDW tras init",
    )
    parser.add_argument(
        "--academico",
        action="store_true",
        help="Solo vistas, procedimientos y triggers (06) en nodos con esquema",
    )
    parser.add_argument(
        "--skip-academico",
        action="store_true",
        help="No ejecutar 06_vistas_procedimientos.sql tras init/distribuido",
    )
    args = parser.parse_args()

    try:
        if args.academico:
            print("Aplicando extensiones academicas (06)...")
            apply_academico_extensions()
        elif args.distribuido:
            setup_distribuido(force_fdw=args.force_fdw)
            if not args.skip_academico:
                apply_academico_extensions()
        else:
            if args.only in ("postgres", "all"):
                print("Inicializando PostgreSQL...")
                init_postgres(args.force)
            if args.only in ("mysql", "all"):
                print("Inicializando MySQL...")
                init_mysql(args.force)
            if not args.skip_distribuido:
                setup_distribuido(force_fdw=args.force_fdw)
            if not args.skip_academico:
                apply_academico_extensions()
        if args.demo:
            from apply_demo_seed import main as demo_main

            demo_main()
        if args.benchmark is not None:
            from apply_benchmark_seed import run_benchmark

            rc = run_benchmark(count=args.benchmark, only=args.only)
            if rc != 0:
                return rc
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("\nListo. App: admin@sicc.com / admin123")
    print("API DB user: sicc_api (ver database/.env.example y backend/.env.example)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
