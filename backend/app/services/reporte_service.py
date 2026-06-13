import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from app.config import get_settings
from app.db.engines import get_mysql_engine, get_postgres_engine
from app.db.session import get_connection
from app.repositories.reporte_repo import ReporteRepository
from app.schemas.reportes import (
    ConteoItem,
    ReporteGlobalPayload,
    ReporteGlobalResponse,
    SedeMetricas,
)


class ReporteService:
    CACHE_KEY = "global"

    def __init__(self) -> None:
        self.repo = ReporteRepository()
        self.settings = get_settings()

    def get_global(self, *, force_refresh: bool = False) -> ReporteGlobalResponse:
        ttl = self.settings.reportes_cache_ttl_seconds
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        if not force_refresh:
            cached = self._read_cache(now)
            if cached:
                return cached

        started = time.perf_counter()
        payload = self._compute_payload()
        duration_ms = int((time.perf_counter() - started) * 1000)
        generated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        expires_at = generated_at + timedelta(seconds=ttl)

        with get_connection(get_postgres_engine()) as conn:
            self.repo.upsert_cache(
                conn,
                clave=self.CACHE_KEY,
                payload=payload.model_dump(),
                generated_at=generated_at,
                expires_at=expires_at,
                duration_ms=duration_ms,
            )

        return ReporteGlobalResponse(
            from_cache=False,
            generated_at=generated_at,
            expires_at=expires_at,
            ttl_seconds=ttl,
            duration_ms=duration_ms,
            payload=payload,
        )

    def _read_cache(self, now: datetime) -> ReporteGlobalResponse | None:
        with get_connection(get_postgres_engine()) as conn:
            row = self.repo.get_cache(conn, self.CACHE_KEY)
        if not row:
            return None
        expires_at = row["expires_at"]
        if isinstance(expires_at, datetime) and expires_at.tzinfo:
            expires_at = expires_at.replace(tzinfo=None)
        if expires_at <= now:
            return None
        payload = ReporteGlobalPayload.model_validate(row["payload"])
        return ReporteGlobalResponse(
            from_cache=True,
            generated_at=row["generated_at"],
            expires_at=expires_at,
            ttl_seconds=self.settings.reportes_cache_ttl_seconds,
            duration_ms=row.get("duration_ms"),
            payload=payload,
        )

    def _compute_payload(self) -> ReporteGlobalPayload:
        sedes: list[SedeMetricas] = []
        estado_map: dict[str, int] = defaultdict(int)
        prioridad_map: dict[str, int] = defaultdict(int)

        cochabamba_via_fdw = False
        with get_connection(get_postgres_engine()) as pg_conn:
            sc = self.repo.aggregate_sede(
                pg_conn,
                "postgres",
                self.settings.sede_central_id,
                "Santa Cruz (Central)",
                "postgres",
            )
            sedes.append(SedeMetricas(**sc))
            e_sc, p_sc = self.repo.aggregate_global_counts(
                pg_conn, "postgres", self.settings.sede_central_id
            )
            for item in e_sc:
                estado_map[item["nombre"]] += item["cantidad"]
            for item in p_sc:
                prioridad_map[item["nombre"]] += item["cantidad"]

            if self.repo.fdw_cochabamba_ready(pg_conn):
                cochabamba_via_fdw = True
                cb = self.repo.aggregate_sede_fdw(
                    pg_conn,
                    self.settings.sede_secundaria_id,
                    "Cochabamba",
                    "mysql_fdw",
                )
                sedes.append(SedeMetricas(**cb))
                e_cb, p_cb = self.repo.aggregate_global_counts_fdw(
                    pg_conn, self.settings.sede_secundaria_id
                )
                for item in e_cb:
                    estado_map[item["nombre"]] += item["cantidad"]
                for item in p_cb:
                    prioridad_map[item["nombre"]] += item["cantidad"]

        if not cochabamba_via_fdw:
            with get_connection(get_mysql_engine()) as my_conn:
                cb = self.repo.aggregate_sede(
                    my_conn,
                    "mysql",
                    self.settings.sede_secundaria_id,
                    "Cochabamba",
                    "mysql",
                )
                sedes.append(SedeMetricas(**cb))
                e_cb, p_cb = self.repo.aggregate_global_counts(
                    my_conn, "mysql", self.settings.sede_secundaria_id
                )
                for item in e_cb:
                    estado_map[item["nombre"]] += item["cantidad"]
                for item in p_cb:
                    prioridad_map[item["nombre"]] += item["cantidad"]

        totales = {
            "incidentes": sum(s.incidentes_total for s in sedes),
            "incidentes_abiertos": sum(s.incidentes_abiertos for s in sedes),
            "activos": sum(s.activos_total for s in sedes),
            "activos_activos": sum(s.activos_activos for s in sedes),
        }

        return ReporteGlobalPayload(
            sedes=sedes,
            incidentes_por_estado=[
                ConteoItem(nombre=k, cantidad=v)
                for k, v in sorted(estado_map.items(), key=lambda x: -x[1])
            ],
            incidentes_por_prioridad=[
                ConteoItem(nombre=k, cantidad=v)
                for k, v in sorted(prioridad_map.items(), key=lambda x: -x[1])
            ],
            totales=totales,
        )
