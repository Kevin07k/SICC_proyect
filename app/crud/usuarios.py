from sqlalchemy import text, Connection
from fastapi import HTTPException
from app import schemas


# ==========================================
#           OBTENER UNO (BY ID)
# ==========================================

def get_usuario(conn: Connection, usuario_id: int):
    # CORRECCIÓN: id -> id_usuario
    query = text("SELECT * FROM Usuarios WHERE id_usuario = :id AND eliminado = 0")
    result = conn.execute(query, {"id": usuario_id})
    return result.mappings().first()


# ==========================================
#           LISTADO (SELECT ALL)
# ==========================================

def get_usuarios(conn: Connection, skip: int = 0, limit: int = 100):
    # Aquí no hay WHERE, así que suele funcionar bien, 
    # pero el ORDER BY también podría fallar si usabas 'id'. 
    # Aquí ordenamos por nombre, así que está bien.
    query = text("""
                 SELECT *
                 FROM Usuarios
                 WHERE eliminado = 0
                 ORDER BY nombre_completo ASC
                 OFFSET :skip ROWS FETCH NEXT :limit ROWS ONLY
                 """)

    result = conn.execute(query, {"skip": skip, "limit": limit})
    return result.mappings().all()


# ==========================================
#           CREAR (INSERT)
# ==========================================

def crear_usuario(conn: Connection, usuario: schemas.UsuarioCreate):
    # El INSERT suele estar bien si especificaste las columnas correctas
    query = text("""
                 INSERT INTO Usuarios (nombre_completo, email, rol)
                 VALUES (:nombre_completo, :email, :rol)
                 """)

    try:
        conn.execute(query, usuario.model_dump())
        conn.commit()
        return usuario
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")


# ==========================================
#           ACTUALIZAR (UPDATE)
# ==========================================

def actualizar_usuario(
        conn: Connection,
        usuario_id: int,
        usuario_update: schemas.UsuarioUpdate
):
    usuario_actual = get_usuario(conn, usuario_id)
    if not usuario_actual:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    nuevos_datos = usuario_update.model_dump(exclude_unset=True)

    params = {
        "id": usuario_id,
        "nombre_completo": nuevos_datos.get("nombre_completo", usuario_actual.nombre_completo),
        "email": nuevos_datos.get("email", usuario_actual.email),
        "rol": nuevos_datos.get("rol", usuario_actual.rol)
    }

    # CORRECCIÓN: id -> id_usuario
    query = text("""
                 UPDATE Usuarios
                 SET nombre_completo = :nombre_completo,
                     email           = :email,
                     rol             = :rol
                 WHERE id_usuario = :id
                 """)

    try:
        conn.execute(query, params)
        conn.commit()
        return get_usuario(conn, usuario_id)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")


# ==========================================
#           ELIMINAR (DELETE)
# ==========================================

def eliminar_usuario(conn: Connection, usuario_id: int):
    if not get_usuario(conn, usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # CORRECCIÓN: id -> id_usuario
    query = text("UPDATE Usuarios SET eliminado = 1 WHERE id_usuario = :id")

    try:
        conn.execute(query, {"id": usuario_id})
        conn.commit()
        return {"mensaje": "Usuario eliminado correctamente"}

    except Exception as e:
        conn.rollback()
        if "FK" in str(e) or "REFERENCE" in str(e):
            raise HTTPException(status_code=400, detail="No se puede eliminar: Tiene incidentes asignados.")
        raise HTTPException(status_code=500, detail=str(e))