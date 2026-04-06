from sqlalchemy import text, Connection
from fastapi import HTTPException
from app import schemas

# ==========================================
#           OBTENER UNA (READ)
# ==========================================

def get_bitacora(conn: Connection, bitacora_id: int):
    """
    Busca una bitácora por ID.
    """
    # CORRECCIÓN PREVENTIVA: id -> id_bitacora
    # (Siguiendo el patrón de tu base de datos)
    query = text("SELECT * FROM Bitacora_Investigacion WHERE id_bitacora = :id AND eliminado = 0")
    result = conn.execute(query, {"id": bitacora_id})

    # Devuelve la fila encontrada o None
    return result.mappings().first()


# ==========================================
#           CREAR (INSERT)
# ==========================================

def crear_bitacora(conn: Connection, bitacora: schemas.BitacoraCreate):
    """
    Crea una nueva entrada en la bitácora.
    """
    # CORRECCIÓN: Cambiamos 'fecha' por 'fecha_entrada'
    query = text("""
        INSERT INTO Bitacora_Investigacion (id_incidente, id_usuario, comentario, fecha_entrada)
        VALUES (:id_incidente, :id_usuario, :comentario, GETDATE());
    """)

    try:
        conn.execute(query, bitacora.model_dump())
        conn.commit()
        return bitacora

    except Exception as e:
        conn.rollback()
        if "FK" in str(e) or "REFERENCE" in str(e):
            raise HTTPException(status_code=400, detail="El ID de Incidente o Usuario no existe.")
        raise HTTPException(status_code=500, detail=f"Error al guardar bitácora: {str(e)}")


# ==========================================
#           ACTUALIZAR (UPDATE)
# ==========================================

def actualizar_bitacora(
        conn: Connection,
        bitacora_id: int,
        bitacora_update: schemas.BitacoraUpdate
):
    """
    Actualiza solo el comentario.
    """
    # 1. Verificar existencia
    if not get_bitacora(conn, bitacora_id):
        raise HTTPException(status_code=404, detail="Bitácora no encontrada")

    # 2. Query SQL
    # CORRECCIÓN PREVENTIVA: id -> id_bitacora
    query = text("""
                 UPDATE Bitacora_Investigacion
                 SET comentario = :comentario
                 WHERE id_bitacora = :id
                 """)

    try:
        conn.execute(query, {
            "comentario": bitacora_update.comentario,
            "id": bitacora_id
        })
        conn.commit()

        return get_bitacora(conn, bitacora_id)

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
#           ELIMINAR (DELETE)
# ==========================================

def eliminar_bitacora(conn: Connection, bitacora_id: int):
    """
    Elimina el registro de la bitácora.
    """
    if not get_bitacora(conn, bitacora_id):
        raise HTTPException(status_code=404, detail="Bitácora no encontrada")

    # CORRECCIÓN PREVENTIVA: id -> id_bitacora
    query = text("UPDATE Bitacora_Investigacion SET eliminado = 1 WHERE id_bitacora = :id")

    try:
        conn.execute(query, {"id": bitacora_id})
        conn.commit()
        return {"mensaje": "Bitácora eliminada correctamente"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))