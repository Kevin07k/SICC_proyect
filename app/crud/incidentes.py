from sqlalchemy import text, Connection
from fastapi import HTTPException
from app import schemas


# ==========================================
#           LISTADO SIMPLE (SELECT)
# ==========================================

# En crud/crud_incidentes.py

def get_incidentes(conn: Connection, skip: int = 0, limit: int = 100):
    query = text("""
                 SELECT i.id_incidente, i.titulo, i.fecha_creacion, i.fecha_cierre,
                        t.nombre          AS nombre_tipo,
                        p.nivel           AS nombre_prioridad,
                        e.nombre          AS nombre_estado,
                        u.nombre_completo AS nombre_usuario
                 FROM Incidentes i
                          LEFT JOIN cat_Tipos_Incidente t ON i.id_tipo = t.id_tipo
                          LEFT JOIN cat_Prioridades p ON i.id_prioridad = p.id_prioridad
                          LEFT JOIN cat_Estados e ON i.id_estado = e.id_estado
                     -- CORRECCIÓN AQUÍ ABAJO: cambiamos u.id por u.id_usuario
                          LEFT JOIN Usuarios u ON i.id_usuario_asignado = u.id_usuario
                 ORDER BY i.fecha_creacion DESC
                 OFFSET :skip ROWS FETCH NEXT :limit ROWS ONLY
                 """)

    result = conn.execute(query, {"skip": skip, "limit": limit})
    return [dict(row) for row in result.mappings()]


# ==========================================
#           LISTADO UNITARIO (BY ID)
# ==========================================

def get_incidente(conn: Connection, incidente_id: int):
    """
    Obtiene un incidente por ID, incluyendo los nombres de los catálogos.
    """
    query = text("""
                 SELECT i.id_incidente, i.titulo, i.descripcion_detallada, i.fecha_creacion, i.fecha_cierre, i.id_tipo, i.id_prioridad, i.id_estado, i.id_usuario_asignado,
                        t.nombre          AS nombre_tipo,
                        p.nivel           AS nombre_prioridad,
                        e.nombre          AS nombre_estado,
                        u.nombre_completo AS nombre_usuario
                 FROM Incidentes i
                          LEFT JOIN cat_Tipos_Incidente t ON i.id_tipo = t.id_tipo
                          LEFT JOIN cat_Prioridades p ON i.id_prioridad = p.id_prioridad
                          LEFT JOIN cat_Estados e ON i.id_estado = e.id_estado
                          LEFT JOIN Usuarios u ON i.id_usuario_asignado = u.id_usuario
                 WHERE i.id_incidente = :id
                 """)

    result = conn.execute(query, {"id": incidente_id})
    return result.mappings().first()


# ==========================================
#      EL MONSTRUO: DETALLE COMPLETO
# ==========================================

def get_incidente_con_detalles(conn: Connection, incidente_id: int):
    """
    Simula el 'joinedload' haciendo consultas manuales.
    """
    # 1. Obtener el Incidente principal
    incidente = get_incidente(conn, incidente_id)

    if not incidente:
        return None

    incidente_dict = dict(incidente)

    # 2. Obtener Bitácoras (CORREGIDO)
    # Cambios:
    # - b.usuario_id -> b.id_usuario
    # - u.id -> u.id_usuario
    # - b.incidente_id -> b.id_incidente
    query_bitacoras = text("""
        SELECT b.*, u.nombre_completo as nombre_usuario 
        FROM Bitacora_Investigacion b
        JOIN Usuarios u ON b.id_usuario = u.id_usuario
        WHERE b.id_incidente = :id
    """)
    result_bitacoras = conn.execute(query_bitacoras, {"id": incidente_id})
    incidente_dict["bitacoras"] = result_bitacoras.mappings().all()

    # 3. Obtener Activos relacionados (CORREGIDO)
    # Cambios:
    # - a.id -> a.id_activo
    # - ia.activo_id -> ia.id_activo
    # - ia.incidente_id -> ia.id_incidente
    query_activos = text("""
        SELECT a.*, ia.notas_relacion
        FROM Activos a
        JOIN Incidentes_Activos ia ON a.id_activo = ia.id_activo
        WHERE ia.id_incidente = :id
    """)
    result_activos = conn.execute(query_activos, {"id": incidente_id})
    incidente_dict["activos_asociados"] = result_activos.mappings().all()

    return incidente_dict


# ==========================================
#           CREAR INCIDENTE (INSERT)
# ==========================================

def crear_incidente(conn: Connection, incidente: schemas.IncidenteCreate):
    # Usamos OUTPUT INSERTED.id_incidente para obtener el ID recién creado en SQL Server
    query = text("""
                 INSERT INTO Incidentes (titulo, descripcion_detallada, id_tipo,
                                         id_prioridad, id_estado, id_usuario_asignado, fecha_creacion)
                 OUTPUT INSERTED.id_incidente
                 VALUES (:titulo, :descripcion_detallada, :id_tipo,
                         :id_prioridad, :id_estado, :id_usuario_asignado, GETDATE());
                 """)

    try:
        # Ejecutamos y obtenemos el ID generado
        result = conn.execute(query, incidente.model_dump())
        nuevo_id = result.scalar()  # scalar() obtiene el primer valor de la primera fila (el ID)

        conn.commit()

        # Devolvemos el incidente completo consultándolo de nuevo
        # Esto asegura que tengas la fecha exacta del servidor y el ID
        return get_incidente(conn, nuevo_id)

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear incidente: {str(e)}")


# ==========================================
#      VINCULAR ACTIVO A INCIDENTE
# ==========================================

def crear_incidente_activo(conn: Connection, vinculo: schemas.IncidenteActivoCreate):
    # CORRECCIÓN: incidente_id -> id_incidente, activo_id -> id_activo
    query = text("""
                 INSERT INTO Incidentes_Activos (id_incidente, id_activo, notas_relacion)
                 VALUES (:id_incidente, :id_activo, :notas_relacion)
                 """)

    try:
        conn.execute(query, vinculo.model_dump())
        conn.commit()
        return vinculo
    except Exception as e:
        conn.rollback()
        # Verificar duplicados
        if "PRIMARY KEY" in str(e) or "DUPLICATE" in str(e):
            raise HTTPException(status_code=400, detail="Este activo ya está vinculado a este incidente.")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
#           ACTUALIZAR (UPDATE)
# ==========================================

def actualizar_incidente(
        conn: Connection,
        incidente_id: int,
        incidente_update: schemas.IncidenteUpdate
):
    # 1. Obtener datos actuales
    actual = get_incidente(conn, incidente_id)
    if not actual:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    # 2. Preparar datos
    nuevos_datos = incidente_update.model_dump(exclude_unset=True)

    # Mezclamos datos (si no envían uno, usamos el que ya tenía)
    params = {
        "id": incidente_id,
        "titulo": nuevos_datos.get("titulo", actual.titulo),
        "descripcion": nuevos_datos.get("descripcion_detallada", actual.descripcion_detallada),
        "id_tipo": nuevos_datos.get("id_tipo", actual.id_tipo),
        "id_prioridad": nuevos_datos.get("id_prioridad", actual.id_prioridad),
        "id_estado": nuevos_datos.get("id_estado", actual.id_estado),
        "id_usuario_asignado": nuevos_datos.get("id_usuario_asignado", actual.id_usuario_asignado)
    }

    # 3. Query
    query = text("""
                 UPDATE Incidentes
                 SET titulo                = :titulo,
                     descripcion_detallada = :descripcion,
                     id_tipo               = :id_tipo,
                     id_prioridad          = :id_prioridad,
                     id_estado             = :id_estado,
                     id_usuario_asignado   = :id_usuario_asignado
                 WHERE id_incidente = :id
                 """)

    try:
        conn.execute(query, params)
        conn.commit()
        return get_incidente(conn, incidente_id)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
#           ELIMINAR (DELETE)
# ==========================================

def eliminar_incidente(conn: Connection, incidente_id: int):
    # Primero verificamos
    if not get_incidente(conn, incidente_id):
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    # OJO: Si tienes bitácoras o activos vinculados, SQL Server dará error de FK.
    # Podrías borrar primero las relaciones o dejar que falle para proteger datos.
    # Aquí intentamos borrar directo.
    query = text("DELETE FROM Incidentes WHERE id_incidente = :id")

    try:
        conn.execute(query, {"id": incidente_id})
        conn.commit()
        return {"mensaje": "Incidente eliminado"}
    except Exception as e:
        conn.rollback()
        if "FK" in str(e) or "REFERENCE" in str(e):
            raise HTTPException(status_code=400, detail="No se puede eliminar: Tiene bitácoras o activos asociados.")
        raise HTTPException(status_code=500, detail=str(e))


def eliminar_vinculo_incidente_activo(conn: Connection, incidente_id: int, activo_id: int):
    """
    Elimina la relación entre un incidente y un activo (Tabla intermedia).
    """
    # Usamos los nombres correctos: id_incidente y id_activo
    query = text("""
                 DELETE
                 FROM Incidentes_Activos
                 WHERE id_incidente = :id_incidente
                   AND id_activo = :id_activo
                 """)

    try:
        conn.execute(query, {
            "id_incidente": incidente_id,
            "id_activo": activo_id
        })
        conn.commit()

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al desvincular activo: {str(e)}")