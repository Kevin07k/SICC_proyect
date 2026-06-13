-- Permisos MongoDB + asignación Analista / DBA (BDs ya existentes)

INSERT INTO Permisos (nombre, codigo, descripcion) VALUES
    ('Ver Documentos NoSQL', 'documentos.ver', 'Visualizar evidencias, timeline y telemetria MongoDB'),
    ('Gestionar Documentos NoSQL', 'documentos.gestionar', 'Registrar documentos MongoDB en incidentes y activos')
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO Roles_Permisos (id_rol, id_permiso)
SELECT r.id_rol, p.id_permiso
FROM Roles r
JOIN Permisos p ON p.codigo IN ('documentos.ver', 'documentos.gestionar')
WHERE r.nombre = 'Analista'
ON CONFLICT DO NOTHING;

INSERT INTO Roles_Permisos (id_rol, id_permiso)
SELECT r.id_rol, p.id_permiso
FROM Roles r
JOIN Permisos p ON p.codigo IN (
    'incidentes.ver', 'activos.ver', 'bitacora.ver',
    'documentos.ver', 'documentos.gestionar'
)
WHERE r.nombre = 'DBA'
ON CONFLICT DO NOTHING;
