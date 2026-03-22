from sqlalchemy import text, Connection


# ==========================================
#      ESTADÍSTICAS POR TIPO
# ==========================================

def get_conteo_incidentes_por_tipo(conn: Connection):
    query = text("""
                 SELECT t.nombre, COUNT(i.id_incidente) as total
                 FROM cat_Tipos_Incidente t
                          LEFT JOIN Incidentes i ON t.id_tipo = i.id_tipo
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
                          LEFT JOIN Incidentes i ON p.id_prioridad = i.id_prioridad
                 GROUP BY p.nivel, p.valor_orden
                 ORDER BY p.valor_orden DESC
                 """)

    result = conn.execute(query)

    # ANTES: return result.mappings().all()
    # AHORA: Convertimos explícitamente a dict
    return [dict(row) for row in result.mappings()]