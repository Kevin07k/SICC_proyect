-- SICC — Seed Data: Catálogos + Usuarios (PostgreSQL)
INSERT INTO cat_Prioridades (nivel, valor_orden) VALUES
    ('Baja', 1),
    ('Media', 2),
    ('Alta', 3),
    ('Critica', 4);

INSERT INTO cat_Estados (nombre) VALUES
    ('Nuevo'),
    ('En Investigacion'),
    ('Contenido'),
    ('Erradicado'),
    ('Cerrado'),
    ('Falso Positivo');

INSERT INTO cat_Tipos_Incidente (nombre, descripcion) VALUES
    ('Phishing', 'Intento de adquirir informacion sensible mediante suplantacion'),
    ('Malware', 'Software malicioso en sistemas de la sede'),
    ('Acceso No Autorizado', 'Intrusion o intento de acceso sin credenciales validas'),
    ('DoS', 'Denegacion de servicio que afecta disponibilidad'),
    ('Exfiltracion de Datos', 'Fuga o extraccion no autorizada de informacion');

INSERT INTO cat_Sedes (nombre_sede, nivel_criticidad) VALUES
    ('Sede Central - Santa Cruz', 'Alta'),
    ('Sucursal Cochabamba', 'Media');

INSERT INTO Roles (nombre, descripcion) VALUES
    ('Administrador', 'Acceso total al sistema'),
    ('Analista', 'Gestion de incidentes y activos'),
    ('DBA', 'Administracion de bases de datos');

INSERT INTO Permisos (nombre, codigo, descripcion) VALUES
    ('Gestionar Usuarios', 'usuarios.gestionar', 'Crear, modificar y desactivar usuarios'),
    ('Ver Usuarios',       'usuarios.ver',       'Visualizar lista y detalles de usuarios'),
    ('Gestionar Incidentes', 'incidentes.gestionar', 'Crear, modificar y cerrar incidentes'),
    ('Ver Incidentes',     'incidentes.ver',     'Visualizar incidentes'),
    ('Gestionar Activos',  'activos.gestionar',  'Crear, modificar y transferir activos'),
    ('Ver Activos',        'activos.ver',        'Visualizar activos'),
    ('Gestionar Catalogos', 'catalogos.gestionar', 'Modificar catalogos del sistema'),
    ('Ver Reportes',       'reportes.ver',       'Acceder a reportes globales'),
    ('Sincronizar',        'sync.ejecutar',      'Ejecutar sincronizacion manual'),
    ('Ver Bitacora',       'bitacora.ver',       'Visualizar bitacora de investigacion'),
    ('Ver Documentos NoSQL', 'documentos.ver', 'Visualizar evidencias, timeline y telemetria MongoDB'),
    ('Gestionar Documentos NoSQL', 'documentos.gestionar', 'Registrar documentos MongoDB en incidentes y activos');

INSERT INTO Roles_Permisos (id_rol, id_permiso)
SELECT r.id_rol, p.id_permiso
FROM Roles r, Permisos p
WHERE r.nombre = 'Administrador';

INSERT INTO Roles_Permisos (id_rol, id_permiso)
SELECT r.id_rol, p.id_permiso
FROM Roles r, Permisos p
WHERE r.nombre = 'Analista'
  AND p.codigo IN ('incidentes.gestionar', 'incidentes.ver',
                   'activos.gestionar', 'activos.ver', 'bitacora.ver',
                   'documentos.ver', 'documentos.gestionar');

INSERT INTO Roles_Permisos (id_rol, id_permiso)
SELECT r.id_rol, p.id_permiso
FROM Roles r, Permisos p
WHERE r.nombre = 'DBA'
  AND p.codigo IN ('catalogos.gestionar', 'sync.ejecutar',
                   'reportes.ver', 'usuarios.ver',
                   'incidentes.ver', 'activos.ver', 'bitacora.ver',
                   'documentos.ver', 'documentos.gestionar');

-- UUIDs fijos para sync y switcher de prueba (/dev/switch)
-- admin123: $2b$12$IGJe7k/OGX4KJzZ8HFc0Cehn9iYldLE.hFOR55rAcdMXicRINlUxm
-- test123:  $2b$12$HKNoZv4N06NNHe57GF4KdOrqcUBJx9hxN3dFzuRDngam/Xr.C/PEq

INSERT INTO Usuarios (uuid, email, password_hash, nombre_completo, id_sede, id_rol)
VALUES (
    '11111111-1111-1111-1111-111111111101',
    'admin@sicc.com',
    '$2b$12$IGJe7k/OGX4KJzZ8HFc0Cehn9iYldLE.hFOR55rAcdMXicRINlUxm',
    'Administrador del Sistema',
    (SELECT id_sede FROM cat_Sedes WHERE nombre_sede = 'Sede Central - Santa Cruz'),
    (SELECT id_rol FROM Roles WHERE nombre = 'Administrador')
);

INSERT INTO Usuarios (uuid, email, password_hash, nombre_completo, id_sede, id_rol)
VALUES (
    '11111111-1111-1111-1111-111111111102',
    'analista.sc@test.sicc',
    '$2b$12$HKNoZv4N06NNHe57GF4KdOrqcUBJx9hxN3dFzuRDngam/Xr.C/PEq',
    'Analista Santa Cruz',
    (SELECT id_sede FROM cat_Sedes WHERE nombre_sede = 'Sede Central - Santa Cruz'),
    (SELECT id_rol FROM Roles WHERE nombre = 'Analista')
);

INSERT INTO Usuarios (uuid, email, password_hash, nombre_completo, id_sede, id_rol)
VALUES (
    '11111111-1111-1111-1111-111111111103',
    'analista.cb@test.sicc',
    '$2b$12$HKNoZv4N06NNHe57GF4KdOrqcUBJx9hxN3dFzuRDngam/Xr.C/PEq',
    'Analista Cochabamba',
    (SELECT id_sede FROM cat_Sedes WHERE nombre_sede = 'Sucursal Cochabamba'),
    (SELECT id_rol FROM Roles WHERE nombre = 'Analista')
);

INSERT INTO Usuarios (uuid, email, password_hash, nombre_completo, id_sede, id_rol)
VALUES (
    '11111111-1111-1111-1111-111111111104',
    'dba@test.sicc',
    '$2b$12$HKNoZv4N06NNHe57GF4KdOrqcUBJx9hxN3dFzuRDngam/Xr.C/PEq',
    'DBA Central',
    (SELECT id_sede FROM cat_Sedes WHERE nombre_sede = 'Sede Central - Santa Cruz'),
    (SELECT id_rol FROM Roles WHERE nombre = 'DBA')
);

INSERT INTO Usuarios (uuid, email, password_hash, nombre_completo, id_sede, id_rol)
VALUES (
    '11111111-1111-1111-1111-111111111105',
    'dba.cb@test.sicc',
    '$2b$12$HKNoZv4N06NNHe57GF4KdOrqcUBJx9hxN3dFzuRDngam/Xr.C/PEq',
    'DBA Cochabamba',
    (SELECT id_sede FROM cat_Sedes WHERE nombre_sede = 'Sucursal Cochabamba'),
    (SELECT id_rol FROM Roles WHERE nombre = 'DBA')
);

INSERT INTO sync_control (id, last_sync, nodo_origen)
VALUES (1, '1970-01-01 00:00:00', 'postgres')
ON CONFLICT (id) DO NOTHING;
