from sqlalchemy import text, Connection
from fastapi import HTTPException
from app import schemas


# ==========================================
#           OBTENER UNO (BY ID)
# ==========================================
def get_activo(conn: Connection, activo_id: int):
    # Asumimos que la PK es id_activo
    query = text("""
        SELECT a.id_activo, a.hostname, a.direccion_ip, a.tipo_activo, a.propietario, a.id_sede, s.nombre_sede 
        FROM Activos a
        LEFT JOIN cat_Sedes s ON a.id_sede = s.id_sede
        WHERE a.id_activo = :id
    """)
    result = conn.execute(query, {"id": activo_id})
    return result.mappings().first()


# ==========================================
#           LISTADO (SELECT ALL)
# ==========================================
def get_activos(conn: Connection, skip: int = 0, limit: int = 100):
    query = text("""
                 SELECT a.id_activo, a.hostname, a.direccion_ip, a.tipo_activo, a.propietario, a.id_sede, s.nombre_sede
                 FROM Activos a
                 LEFT JOIN cat_Sedes s ON a.id_sede = s.id_sede
                 ORDER BY a.hostname ASC
                 OFFSET :skip ROWS FETCH NEXT :limit ROWS ONLY
                 """)
    result = conn.execute(query, {"skip": skip, "limit": limit})
    return result.mappings().all()


# ==========================================
#           CREAR (INSERT)
# ==========================================
def crear_activo(conn: Connection, activo: schemas.ActivoCreate):
    # CORRECCIÓN: Usamos 'tipo_activo' en la columna de la BD
    query = text("""
                 INSERT INTO Activos (hostname, direccion_ip, tipo_activo, propietario, id_sede)
                 VALUES (:hostname, :direccion_ip, :tipo_activo, :propietario, :id_sede)
                 """)

    try:
        # Al usar .model_dump(), obtenemos {'tipo_activo': 'Servidor', ...}
        # Esto coincide perfectamente con los parámetros :tipo_activo
        conn.execute(query, activo.model_dump())
        conn.commit()
        return activo

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear activo: {str(e)}")


# ==========================================
#           ACTUALIZAR (UPDATE)
# ==========================================
def actualizar_activo(
        conn: Connection,
        activo_id: int,
        activo_update: schemas.ActivoUpdate
):
    existing_asset = get_activo(conn, activo_id)
    if not existing_asset:
        raise HTTPException(status_code=404, detail="Activo no encontrado")

    update_data = activo_update.model_dump(exclude_unset=True)

    # Preparamos los parámetros mezclando datos nuevos con los viejos
    params = {
        "id": activo_id,
        "hostname": update_data.get("hostname", existing_asset.hostname),
        "direccion_ip": update_data.get("direccion_ip", existing_asset.direccion_ip),

        # CORRECCIÓN: Mapeamos directo a 'tipo_activo'
        # Nota: Usamos getattr para leer de la BD por si acaso
        "tipo_activo": update_data.get("tipo_activo", getattr(existing_asset, 'tipo_activo', None)),

        "propietario": update_data.get("propietario", existing_asset.propietario),
        "id_sede": update_data.get("id_sede", existing_asset.id_sede)
    }

    # CORRECCIÓN: SET tipo_activo = :tipo_activo
    query = text("""
                 UPDATE Activos
                 SET hostname     = :hostname,
                     direccion_ip = :direccion_ip,
                     tipo_activo  = :tipo_activo,
                     propietario  = :propietario,
                     id_sede      = :id_sede
                 WHERE id_activo = :id
                 """)

    try:
        conn.execute(query, params)
        conn.commit()
        return get_activo(conn, activo_id)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
#           ELIMINAR (DELETE)
# ==========================================
def eliminar_activo(conn: Connection, activo_id: int):
    if not get_activo(conn, activo_id):
        raise HTTPException(status_code=404, detail="Activo no encontrado")

    # Optimización: Usar EXISTS en lugar de IN o dejar que falle la FK para verificar incidentes
    check_query = text("""
        SELECT 1 
        WHERE EXISTS (
            SELECT 1 FROM Incidentes_Activos WHERE id_activo = :id
        )
    """)
    if conn.execute(check_query, {"id": activo_id}).scalar():
        raise HTTPException(status_code=400, detail="No se puede eliminar: El activo está vinculado a incidentes (Verificado con EXISTS).")

    query = text("DELETE FROM Activos WHERE id_activo = :id")

    try:
        conn.execute(query, {"id": activo_id})
        conn.commit()
        return {"mensaje": "Activo eliminado correctamente"}
    except Exception as e:
        conn.rollback()
        if "FK" in str(e) or "REFERENCE" in str(e):
            raise HTTPException(status_code=400, detail="No se puede eliminar: El activo está vinculado a incidentes.")
        raise HTTPException(status_code=500, detail=str(e))