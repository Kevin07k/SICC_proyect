-- Demo operacional: Cochabamba (id_sede=2) — 5 activos + 5 incidentes
-- Ejecutar en sicc_cochabamba; re-ejecutar puede duplicar si no hay UNIQUE en hostname

INSERT IGNORE INTO Activos (uuid, hostname, direccion_ip, tipo_activo, propietario, id_sede)
VALUES
    ('b2000001-0001-4000-8000-000000000001', 'cb-srv-01.demo', '10.2.0.11', 'servidor', 'TI Cochabamba', 2),
    ('b2000001-0001-4000-8000-000000000002', 'cb-srv-02.demo', '10.2.0.12', 'servidor', 'TI Cochabamba', 2),
    ('b2000001-0001-4000-8000-000000000003', 'cb-ws-01.demo', '10.2.0.21', 'workstation', 'Operaciones CB', 2),
    ('b2000001-0001-4000-8000-000000000004', 'cb-fw-01.demo', '10.2.0.1', 'firewall', 'Seguridad CB', 2),
    ('b2000001-0001-4000-8000-000000000005', 'cb-db-01.demo', '10.2.0.30', 'base_datos', 'DBA CB', 2);

INSERT IGNORE INTO Incidentes (
    uuid, titulo, descripcion, id_tipo, id_prioridad, id_estado,
    id_usuario_asignado, id_sede
)
VALUES
    (
        'a2000001-0001-4000-8000-000000000001',
        '[Demo CB] Phishing sucursal',
        'Usuario reporto enlace malicioso',
        1, 2, 1,
        '11111111-1111-1111-1111-111111111103',
        2
    ),
    (
        'a2000001-0001-4000-8000-000000000002',
        '[Demo CB] Ransomware intento',
        'Bloqueo en endpoint cb-ws-01',
        2, 4, 2,
        '11111111-1111-1111-1111-111111111103',
        2
    ),
    (
        'a2000001-0001-4000-8000-000000000003',
        '[Demo CB] Acceso no autorizado',
        'Cuenta bloqueada tras intentos fallidos',
        3, 3, 1,
        '11111111-1111-1111-1111-111111111103',
        2
    ),
    (
        'a2000001-0001-4000-8000-000000000004',
        '[Demo CB] Caida servicio web',
        'Indisponibilidad en portal sucursal',
        4, 3, 2,
        '11111111-1111-1111-1111-111111111103',
        2
    ),
    (
        'a2000001-0001-4000-8000-000000000005',
        '[Demo CB] Exfiltracion USB',
        'Posible copia no autorizada',
        5, 2, 3,
        '11111111-1111-1111-1111-111111111103',
        2
    );

-- Vinculos incidente ↔ activo (1 activo principal por incidente demo)
INSERT IGNORE INTO Incidentes_Activos (
    uuid, id_incidente, id_activo, notas,
    tipo_activo_registrado, sede_registrada, hostname_registrado
)
VALUES
    (
        'c2000001-0001-4000-8000-000000000001',
        'a2000001-0001-4000-8000-000000000001',
        'b2000001-0001-4000-8000-000000000003',
        'Estacion donde se reporto el enlace malicioso',
        'workstation', 'Sucursal Cochabamba', 'cb-ws-01.demo'
    ),
    (
        'c2000001-0001-4000-8000-000000000002',
        'a2000001-0001-4000-8000-000000000002',
        'b2000001-0001-4000-8000-000000000003',
        'Endpoint aislado por heuristica de ransomware',
        'workstation', 'Sucursal Cochabamba', 'cb-ws-01.demo'
    ),
    (
        'c2000001-0001-4000-8000-000000000003',
        'a2000001-0001-4000-8000-000000000003',
        'b2000001-0001-4000-8000-000000000001',
        'Servidor con cuenta bloqueada tras intentos fallidos',
        'servidor', 'Sucursal Cochabamba', 'cb-srv-01.demo'
    ),
    (
        'c2000001-0001-4000-8000-000000000004',
        'a2000001-0001-4000-8000-000000000004',
        'b2000001-0001-4000-8000-000000000002',
        'Servidor que aloja el portal web de sucursal',
        'servidor', 'Sucursal Cochabamba', 'cb-srv-02.demo'
    ),
    (
        'c2000001-0001-4000-8000-000000000005',
        'a2000001-0001-4000-8000-000000000005',
        'b2000001-0001-4000-8000-000000000003',
        'Estacion origen de posible exfiltracion por USB',
        'workstation', 'Sucursal Cochabamba', 'cb-ws-01.demo'
    );
