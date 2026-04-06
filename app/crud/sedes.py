from sqlalchemy import text, Connection
from fastapi import HTTPException
from app import schemas

def get_sedes(conn: Connection, skip: int = 0, limit: int = 100):
    query = text("""
        SELECT * FROM cat_Sedes
        WHERE eliminado = 0
        ORDER BY nombre_sede ASC
        OFFSET :skip ROWS FETCH NEXT :limit ROWS ONLY
    """)
    result = conn.execute(query, {"skip": skip, "limit": limit})
    return result.mappings().all()

def get_sede(conn: Connection, sede_id: int):
    query = text("SELECT * FROM cat_Sedes WHERE id_sede = :id AND eliminado = 0")
    result = conn.execute(query, {"id": sede_id})
    return result.mappings().first()

def crear_sede(conn: Connection, sede: schemas.SedeCreate):
    query = text("""
        INSERT INTO cat_Sedes (nombre_sede, nivel_criticidad)
        VALUES (:nombre_sede, :nivel_criticidad)
    """)
    try:
        conn.execute(query, sede.model_dump())
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear Sede: {str(e)}")

def actualizar_sede(conn: Connection, sede_id: int, sede_update: schemas.SedeUpdate):
    existente = get_sede(conn, sede_id)
    if not existente:
        raise HTTPException(status_code=404, detail="Sede no encontrada")

    datos_nuevos = sede_update.model_dump(exclude_unset=True)
    params = {
        "id": sede_id,
        "nombre_sede": datos_nuevos.get("nombre_sede", existente.nombre_sede),
        "nivel_criticidad": datos_nuevos.get("nivel_criticidad", existente.nivel_criticidad)
    }

    query = text("""
        UPDATE cat_Sedes
        SET nombre_sede = :nombre_sede,
            nivel_criticidad = :nivel_criticidad
        WHERE id_sede = :id
    """)
    try:
        conn.execute(query, params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

def eliminar_sede(conn: Connection, sede_id: int):
    if not get_sede(conn, sede_id):
        raise HTTPException(status_code=404, detail="Sede no encontrada")

    query = text("UPDATE cat_Sedes SET eliminado = 1 WHERE id_sede = :id")
    try:
        conn.execute(query, {"id": sede_id})
        conn.commit()
    except Exception as e:
        conn.rollback()
        if "FK" in str(e) or "REFERENCE" in str(e):
            raise HTTPException(status_code=400, detail="No se puede eliminar: Esta Sede tiene activos vinculados.")
        raise HTTPException(status_code=500, detail=str(e))
