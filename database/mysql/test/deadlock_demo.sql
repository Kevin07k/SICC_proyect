-- =============================================================================
-- DEADLOCK — MySQL InnoDB (dos sesiones mysql)
-- Requiere demo: apply_demo_seed.py
-- Activos fijos Cochabamba:
--   A = b2000001-0001-4000-8000-000000000001
--   B = b2000001-0001-4000-8000-000000000002
-- =============================================================================

USE sicc_cochabamba;

-- ---------- SESIÓN A (terminal 1) ----------
-- START TRANSACTION;
-- UPDATE Activos SET propietario = 'Sesion A paso 1'
-- WHERE uuid = 'b2000001-0001-4000-8000-000000000001';
-- UPDATE Activos SET propietario = 'Sesion A paso 2'
-- WHERE uuid = 'b2000001-0001-4000-8000-000000000002';
-- ROLLBACK;

-- ---------- SESIÓN B (terminal 2) ----------
-- START TRANSACTION;
-- UPDATE Activos SET propietario = 'Sesion B paso 1'
-- WHERE uuid = 'b2000001-0001-4000-8000-000000000002';
-- UPDATE Activos SET propietario = 'Sesion B paso 2'
-- WHERE uuid = 'b2000001-0001-4000-8000-000000000001';
-- (ERROR 1213 Deadlock found)
-- ROLLBACK;
