from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from bson import ObjectId
from pymongo.database import Database


def _serialize_doc(doc: dict[str, Any]) -> dict[str, Any]:
    out = dict(doc)
    out["id"] = str(out.pop("_id"))
    if isinstance(out.get("incidente_uuid"), str):
        pass
    if isinstance(out.get("activo_uuid"), str):
        pass
    return out


class MongoDocumentRepository:
    def list_evidencias(self, db: Database, incidente_uuid: UUID) -> list[dict[str, Any]]:
        cursor = db.evidencias_incidente.find(
            {"incidente_uuid": str(incidente_uuid), "eliminado": False},
            sort=[("created_at", -1)],
        )
        return [_serialize_doc(d) for d in cursor]

    def create_evidencia(
        self,
        db: Database,
        incidente_uuid: UUID,
        autor_uuid: UUID,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        doc = {
            "incidente_uuid": str(incidente_uuid),
            "autor_uuid": str(autor_uuid),
            "created_at": datetime.now(UTC),
            "eliminado": False,
            **data,
        }
        result = db.evidencias_incidente.insert_one(doc)
        doc["_id"] = result.inserted_id
        return _serialize_doc(doc)

    def list_timeline(self, db: Database, incidente_uuid: UUID) -> list[dict[str, Any]]:
        cursor = db.timeline_eventos.find(
            {"incidente_uuid": str(incidente_uuid), "eliminado": False},
            sort=[("created_at", 1)],
        )
        return [_serialize_doc(d) for d in cursor]

    def create_timeline(
        self,
        db: Database,
        incidente_uuid: UUID,
        autor_uuid: UUID,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        doc = {
            "incidente_uuid": str(incidente_uuid),
            "autor_uuid": str(autor_uuid),
            "created_at": datetime.now(UTC),
            "eliminado": False,
            **data,
        }
        result = db.timeline_eventos.insert_one(doc)
        doc["_id"] = result.inserted_id
        return _serialize_doc(doc)

    def list_telemetria(self, db: Database, activo_uuid: UUID) -> list[dict[str, Any]]:
        cursor = db.telemetria_activo.find(
            {"activo_uuid": str(activo_uuid), "eliminado": False},
            sort=[("captured_at", -1)],
        )
        return [_serialize_doc(d) for d in cursor]

    def create_telemetria(
        self,
        db: Database,
        activo_uuid: UUID,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        doc = {
            "activo_uuid": str(activo_uuid),
            "captured_at": datetime.now(UTC),
            "eliminado": False,
            **data,
        }
        result = db.telemetria_activo.insert_one(doc)
        doc["_id"] = result.inserted_id
        return _serialize_doc(doc)

    def get_by_id(self, db: Database, collection: str, doc_id: str) -> dict[str, Any] | None:
        try:
            oid = ObjectId(doc_id)
        except Exception:
            return None
        doc = db[collection].find_one({"_id": oid, "eliminado": False})
        return _serialize_doc(doc) if doc else None
