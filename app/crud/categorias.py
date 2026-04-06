from sqlalchemy import text, Connection
from fastapi import HTTPException
from app import schemas


# ==========================================
#               LISTADOS (SELECT)
# ==========================================

def get_tipos_incidente(conn: Connection):
    query = text("SELECT * FROM cat_Tipos_Incidente WHERE eliminado = 0")
    result = conn.execute(query)
    return result.mappings().all()


def get_prioridades(conn: Connection):
    # Ordena por valor_orden descendente (Mayor número = Más crítica)
    # Ajusta 'DESC' o 'ASC' según tu lógica de negocio
    query = text("SELECT * FROM cat_Prioridades WHERE eliminado = 0 ORDER BY valor_orden DESC")
    result = conn.execute(query)
    return result.mappings().all()


def get_estados(conn: Connection):
    query = text("SELECT * FROM cat_Estados WHERE eliminado = 0")
    result = conn.execute(query)
    return result.mappings().all()

def get_sedes(conn: Connection):
    query = text("SELECT * FROM cat_Sedes WHERE eliminado = 0 ORDER BY nombre_sede ASC")
    result = conn.execute(query)
    return result.mappings().all()


# ==========================================
#           OBTENER UNO SOLO (BY ID)
# ==========================================

def get_tipo_incidente(conn: Connection, tipo_id: int):
    # CORRECCIÓN: id -> id_tipo
    query = text("SELECT * FROM cat_Tipos_Incidente WHERE id_tipo = :id AND eliminado = 0")
    result = conn.execute(query, {"id": tipo_id})
    return result.mappings().first()

def get_prioridad(conn: Connection, prioridad_id: int):
    # CORRECCIÓN: id -> id_prioridad
    query = text("SELECT * FROM cat_Prioridades WHERE id_prioridad = :id AND eliminado = 0")
    result = conn.execute(query, {"id": prioridad_id})
    return result.mappings().first()

def get_estado(conn: Connection, estado_id: int):
    # CORRECCIÓN: id -> id_estado
    query = text("SELECT * FROM cat_Estados WHERE id_estado = :id AND eliminado = 0")
    result = conn.execute(query, {"id": estado_id})
    return result.mappings().first()


# ==========================================
#                  CREATE
# ==========================================

def crear_tipo_incidente(conn: Connection, tipo: schemas.TipoIncidenteCreate):
    # Asumo que el esquema tiene 'nombre' y 'descripcion'
    # Si tienes más campos, agrégalos aquí.
    query = text("""
                 INSERT INTO cat_Tipos_Incidente (nombre, descripcion)
                 VALUES (:nombre, :descripcion)
                 """)

    try:
        conn.execute(query, tipo.model_dump())
        conn.commit()
        return tipo  # Retornamos los datos enviados (simulando éxito)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear tipo: {str(e)}")


# ==========================================
#                  UPDATE
# ==========================================

def actualizar_tipo_incidente(
        conn: Connection,
        tipo_id: int,
        tipo_update: schemas.TipoIncidenteUpdate
):
    # 1. Verificar existencia
    existente = get_tipo_incidente(conn, tipo_id)
    if not existente:
        raise HTTPException(status_code=404, detail="Tipo de incidente no encontrado")

    # 2. Preparar datos (mantener valores viejos si no envían nuevos)
    datos_nuevos = tipo_update.model_dump(exclude_unset=True)

    # Preparamos el diccionario final de parámetros
    params = {
        "id": tipo_id,
        "nombre": datos_nuevos.get("nombre", existente.nombre),
        "descripcion": datos_nuevos.get("descripcion", existente.descripcion)
    }

    # 3. Query SQL
    query = text("""
                 UPDATE cat_Tipos_Incidente
                 SET nombre      = :nombre,
                     descripcion = :descripcion
                 WHERE id_tipo = :id
                 """)

    try:
        conn.execute(query, params)
        conn.commit()
        return get_tipo_incidente(conn, tipo_id)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")


# ==========================================
#                  DELETE
# ==========================================

def eliminar_tipo_incidente(conn: Connection, tipo_id: int):
    # 1. Verificar existencia (Asegúrate de que este también use id_tipo en su query interna)
    if not get_tipo_incidente(conn, tipo_id):
        raise HTTPException(status_code=404, detail="Tipo de incidente no encontrado")

    # CORRECCIÓN: Cambiamos 'id' por 'id_tipo'
    query = text("UPDATE cat_Tipos_Incidente SET eliminado = 1 WHERE id_tipo = :id")

    try:
        conn.execute(query, {"id": tipo_id})
        conn.commit()
        return {"mensaje": "Tipo de incidente eliminado"}
    except Exception as e:
        conn.rollback()
        if "FK" in str(e) or "REFERENCE" in str(e):
            raise HTTPException(status_code=400, detail="No se puede eliminar: Este tipo está en uso.")
        raise HTTPException(status_code=500, detail=str(e))