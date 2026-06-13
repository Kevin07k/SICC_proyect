from datetime import datetime, timezone
from typing import Any

from app.core.replicated_tables import REPLICATED_TABLES, ReplicatedTable
from app.db.engines import get_mysql_engine, get_postgres_engine
from app.db.session import get_connection
from app.repositories.sync_repo import SyncRepository
from app.schemas.sync import SyncManualResponse, SyncStatusResponse, SyncTableStatus


def _parse_ts(value: Any) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo:
            return value.replace(tzinfo=None)
        return value
    return datetime.fromisoformat(str(value))


def _row_wins(source: dict[str, Any], dest: dict[str, Any] | None) -> bool:
    if dest is None:
        return True
    if "updated_at" not in source:
        return True
    if "updated_at" not in dest:
        return True
    return _parse_ts(source["updated_at"]) >= _parse_ts(dest["updated_at"])


class SyncService:
    def __init__(self) -> None:
        self.repo = SyncRepository()

    def _pk_dict(self, table: ReplicatedTable, row: dict[str, Any]) -> dict[str, Any]:
        return {k: row[k] for k in table.pk_columns}

    def _apply_changes(
        self,
        source_rows: list[dict[str, Any]],
        src_dialect: str,
        dest_conn,
        dest_dialect: str,
        table: ReplicatedTable,
    ) -> int:
        applied = 0
        for row in source_rows:
            if table.logical_name == "Usuarios":
                dest_row = self.repo.fetch_by_email(dest_conn, dest_dialect, row["email"])
            else:
                pk = self._pk_dict(table, row)
                dest_row = self.repo.fetch_by_pk(dest_conn, dest_dialect, table, pk)
            if _row_wins(row, dest_row) and (
                dest_row is None
                or table.skip_updated_at_filter
                or "updated_at" not in row
                or "updated_at" not in dest_row
                or _parse_ts(row["updated_at"])
                >= _parse_ts(dest_row.get("updated_at", row["updated_at"]))
            ):
                self.repo.upsert_row(dest_conn, dest_dialect, table, row)
                applied += 1
        return applied

    def run_manual_sync(self) -> SyncManualResponse:
        with get_connection(get_postgres_engine()) as pg_conn, get_connection(
            get_mysql_engine()
        ) as mysql_conn:
            pg_sync = self.repo.get_last_sync(pg_conn, "postgres")
            my_sync = self.repo.get_last_sync(mysql_conn, "mysql")
            since = min(pg_sync, my_sync)
            total = 0
            processed: list[str] = []

            for table in REPLICATED_TABLES:
                pg_rows = self.repo.fetch_changes(pg_conn, "postgres", table, since)
                my_rows = self.repo.fetch_changes(mysql_conn, "mysql", table, since)
                total += self._apply_changes(pg_rows, "postgres", mysql_conn, "mysql", table)
                total += self._apply_changes(my_rows, "mysql", pg_conn, "postgres", table)
                processed.append(table.logical_name)

            now = datetime.now(timezone.utc).replace(tzinfo=None)
            self.repo.set_last_sync(pg_conn, "postgres", now, "postgres")
            self.repo.set_last_sync(mysql_conn, "mysql", now, "mysql")

        return SyncManualResponse(
            last_sync=now,
            tablas_procesadas=processed,
            registros_aplicados=total,
        )

    def get_status(self) -> SyncStatusResponse:
        with get_connection(get_postgres_engine()) as pg_conn, get_connection(
            get_mysql_engine()
        ) as mysql_conn:
            pg_sync = self.repo.get_last_sync(pg_conn, "postgres")
            my_sync = self.repo.get_last_sync(mysql_conn, "mysql")
            since = min(pg_sync, my_sync)
            tablas: list[SyncTableStatus] = []
            for table in REPLICATED_TABLES:
                if table.skip_updated_at_filter:
                    continue
                tablas.append(
                    SyncTableStatus(
                        tabla=table.logical_name,
                        pendientes_postgres=self.repo.count_pending(
                            pg_conn, "postgres", table, since
                        ),
                        pendientes_mysql=self.repo.count_pending(
                            mysql_conn, "mysql", table, since
                        ),
                    )
                )
        return SyncStatusResponse(
            last_sync_postgres=pg_sync,
            last_sync_mysql=my_sync,
            effective_last_sync=since,
            tablas=tablas,
        )
