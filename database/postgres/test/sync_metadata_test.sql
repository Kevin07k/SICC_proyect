-- =============================================================================
-- TEST — Sincronización LWW (metadata replicada)
-- No ejecutar en producción. Solo desarrollo / laboratorio.
-- =============================================================================
-- Flujo sugerido:
--   1. Ejecutar UN bloque en PostgreSQL (central) O en MySQL (secundaria)
--   2. cd ../backend && curl -X POST http://localhost:8000/sync/manual -H "X-Usuario-UUID: <admin-uuid>"
--   3. Verificar con GET /sync/status
-- =============================================================================

-- --- TEST PG: marcar usuario analista SC con updated_at reciente ---
-- UPDATE Usuarios
-- SET nombre_completo = 'Analista SC (TEST sync ' || to_char(NOW(), 'HH24:MI:SS')),
--     updated_at = NOW()
-- WHERE email = 'analista.sc@test.sicc';

-- --- TEST MySQL: marcar usuario analista CB con updated_at reciente ---
-- UPDATE Usuarios
-- SET nombre_completo = CONCAT('Analista CB (TEST sync ', DATE_FORMAT(NOW(), '%H:%i:%s'), ')'),
--     updated_at = NOW()
-- WHERE email = 'analista.cb@test.sicc';

-- --- TEST PG: nuevo permiso temporal en catálogo (solo si quieres probar Roles_Permisos) ---
-- INSERT INTO Permisos (nombre, codigo, descripcion)
-- VALUES ('TEST Sync', 'test.sync', 'Registro de prueba sync')
-- ON CONFLICT (codigo) DO UPDATE SET updated_at = NOW();

-- --- TEST: consulta pendientes (PostgreSQL) ---
-- SELECT email, nombre_completo, updated_at FROM Usuarios ORDER BY updated_at DESC LIMIT 5;

-- --- TEST: consulta pendientes (MySQL) ---
-- SELECT email, nombre_completo, updated_at FROM Usuarios ORDER BY updated_at DESC LIMIT 5;
