-- DBA en sede Cochabamba (PostgreSQL) — Password: test123

INSERT INTO Usuarios (uuid, email, password_hash, nombre_completo, id_sede, id_rol)
VALUES (
    '11111111-1111-1111-1111-111111111105',
    'dba.cb@test.sicc',
    '$2b$12$HKNoZv4N06NNHe57GF4KdOrqcUBJx9hxN3dFzuRDngam/Xr.C/PEq',
    'DBA Cochabamba',
    (SELECT id_sede FROM cat_Sedes WHERE nombre_sede = 'Sucursal Cochabamba'),
    (SELECT id_rol FROM Roles WHERE nombre = 'DBA')
)
ON CONFLICT (uuid) DO NOTHING;
