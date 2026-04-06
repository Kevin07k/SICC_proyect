from sqlalchemy import text, Connection


# ==========================================
#      ESTADÍSTICAS POR TIPO
# ==========================================

def get_conteo_incidentes_por_tipo(conn: Connection):
    query = text("""
                 SELECT t.nombre, COUNT(i.id_incidente) as total
                 FROM cat_Tipos_Incidente t
                          LEFT JOIN Incidentes i ON t.id_tipo = i.id_tipo AND i.eliminado = 0
                 WHERE t.eliminado = 0
                 GROUP BY t.nombre
                 """)

    result = conn.execute(query)

    # ANTES: return result.mappings().all()
    # AHORA: Convertimos explícitamente a dict
    return [dict(row) for row in result.mappings()]


# ==========================================
#    ESTADÍSTICAS POR PRIORIDAD
# ==========================================

def get_conteo_incidentes_por_prioridad(conn: Connection):
    query = text("""
                 SELECT p.nivel, COUNT(i.id_incidente) as total
                 FROM cat_Prioridades p
                          LEFT JOIN Incidentes i ON p.id_prioridad = i.id_prioridad AND i.eliminado = 0
                 WHERE p.eliminado = 0
                 GROUP BY p.nivel, p.valor_orden
                 ORDER BY p.valor_orden DESC
                 """)

    result = conn.execute(query)

    # ANTES: return result.mappings().all()
    # AHORA: Convertimos explícitamente a dict
    return [dict(row) for row in result.mappings()]


# ==========================================
#    ESTADÍSTICAS GENERALES (CRÍTICOS)
# ==========================================

def get_conteo_incidentes_criticos(conn: Connection):
    query = text("""
        SELECT COUNT(i.id_incidente) as total
        FROM Incidentes i
        INNER JOIN cat_Prioridades p ON i.id_prioridad = p.id_prioridad
        INNER JOIN cat_Estados e ON i.id_estado = e.id_estado
        WHERE p.nivel = 'Crítica' AND e.nombre <> 'Cerrado' AND i.eliminado = 0
    """)
    result = conn.execute(query).scalar()
    return result or 0