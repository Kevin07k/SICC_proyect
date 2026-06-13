-- Demo operacional: Santa Cruz (id_sede=1) — 5 activos + 5 incidentes
-- Idempotente: ON CONFLICT DO NOTHING

INSERT INTO Activos (uuid, hostname, direccion_ip, tipo_activo, propietario, id_sede)
VALUES
    ('b1000001-0001-4000-8000-000000000001', 'sc-srv-01.demo', '10.1.0.11', 'servidor', 'TI Central', 1),
    ('b1000001-0001-4000-8000-000000000002', 'sc-srv-02.demo', '10.1.0.12', 'servidor', 'TI Central', 1),
    ('b1000001-0001-4000-8000-000000000003', 'sc-ws-01.demo', '10.1.0.21', 'workstation', 'Finanzas SC', 1),
    ('b1000001-0001-4000-8000-000000000004', 'sc-fw-01.demo', '10.1.0.1', 'firewall', 'Seguridad SC', 1),
    ('b1000001-0001-4000-8000-000000000005', 'sc-db-01.demo', '10.1.0.30', 'base_datos', 'DBA SC', 1)
ON CONFLICT (uuid) DO NOTHING;

INSERT INTO Incidentes (
    uuid, titulo, descripcion, id_tipo, id_prioridad, id_estado,
    id_usuario_asignado, id_sede
)
VALUES
    (
        'a1000001-0001-4000-8000-000000000001',
        '[Demo SC] Phishing correo interno',
        'Correo sospechoso reportado en sede central',
        1, 2, 1,
        '11111111-1111-1111-1111-111111111102',
        1
    ),
    (
        'a1000001-0001-4000-8000-000000000002',
        '[Demo SC] Malware en estacion',
        'Antivirus detecto amenaza en sc-ws-01',
        2, 3, 2,
        '11111111-1111-1111-1111-111111111102',
        1
    ),
    (
        'a1000001-0001-4000-8000-000000000003',
        '[Demo SC] Intento acceso VPN',
        'Multiples fallos de autenticacion',
        3, 2, 1,
        '11111111-1111-1111-1111-111111111101',
        1
    ),
    (
        'a1000001-0001-4000-8000-000000000004',
        '[Demo SC] Pico trafico anomalo',
        'Posible DoS en perimetro',
        4, 4, 2,
        '11111111-1111-1111-1111-111111111102',
        1
    ),
    (
        'a1000001-0001-4000-8000-000000000005',
        '[Demo SC] Fuga documento prueba',
        'Archivo compartido sin autorizacion',
        5, 3, 3,
        '11111111-1111-1111-1111-111111111101',
        1
    )
ON CONFLICT (uuid) DO NOTHING;

-- Vinculos incidente ↔ activo (1 activo principal por incidente demo)
INSERT INTO Incidentes_Activos (
    uuid, id_incidente, id_activo, notas,
    tipo_activo_registrado, sede_registrada, hostname_registrado
)
VALUES
    (
        'c1000001-0001-4000-8000-000000000001',
        'a1000001-0001-4000-8000-000000000001',
        'b1000001-0001-4000-8000-000000000003',
        'Estacion donde se abrio el correo de phishing',
        'workstation', 'Sede Central - Santa Cruz', 'sc-ws-01.demo'
    ),
    (
        'c1000001-0001-4000-8000-000000000002',
        'a1000001-0001-4000-8000-000000000002',
        'b1000001-0001-4000-8000-000000000003',
        'Endpoint con deteccion de malware',
        'workstation', 'Sede Central - Santa Cruz', 'sc-ws-01.demo'
    ),
    (
        'c1000001-0001-4000-8000-000000000003',
        'a1000001-0001-4000-8000-000000000003',
        'b1000001-0001-4000-8000-000000000001',
        'Servidor VPN con intentos de autenticacion fallidos',
        'servidor', 'Sede Central - Santa Cruz', 'sc-srv-01.demo'
    ),
    (
        'c1000001-0001-4000-8000-000000000004',
        'a1000001-0001-4000-8000-000000000004',
        'b1000001-0001-4000-8000-000000000004',
        'Firewall de perimetro con pico de trafico anomalo',
        'firewall', 'Sede Central - Santa Cruz', 'sc-fw-01.demo'
    ),
    (
        'c1000001-0001-4000-8000-000000000005',
        'a1000001-0001-4000-8000-000000000005',
        'b1000001-0001-4000-8000-000000000005',
        'Servidor de datos con posible fuga de documento',
        'base_datos', 'Sede Central - Santa Cruz', 'sc-db-01.demo'
    )
ON CONFLICT (id_incidente, id_activo) DO NOTHING;

-- Vinculos incidente ↔ activo (1 activo principal por incidente demo)
INSERT INTO Incidentes_Activos (
    uuid, id_incidente, id_activo, notas,
    tipo_activo_registrado, sede_registrada, hostname_registrado
)
VALUES
    (
        'c1000001-0001-4000-8000-000000000001',
        'a1000001-0001-4000-8000-000000000001',
        'b1000001-0001-4000-8000-000000000003',
        'Estacion donde se abrio el correo de phishing',
        'workstation', 'Sede Central - Santa Cruz', 'sc-ws-01.demo'
    ),
    (
        'c1000001-0001-4000-8000-000000000002',
        'a1000001-0001-4000-8000-000000000002',
        'b1000001-0001-4000-8000-000000000003',
        'Endpoint con deteccion de malware',
        'workstation', 'Sede Central - Santa Cruz', 'sc-ws-01.demo'
    ),
    (
        'c1000001-0001-4000-8000-000000000003',
        'a1000001-0001-4000-8000-000000000003',
        'b1000001-0001-4000-8000-000000000001',
        'Servidor VPN con intentos de autenticacion fallidos',
        'servidor', 'Sede Central - Santa Cruz', 'sc-srv-01.demo'
    ),
    (
        'c1000001-0001-4000-8000-000000000004',
        'a1000001-0001-4000-8000-000000000004',
        'b1000001-0001-4000-8000-000000000004',
        'Firewall de perimetro con pico de trafico anomalo',
        'firewall', 'Sede Central - Santa Cruz', 'sc-fw-01.demo'
    ),
    (
        'c1000001-0001-4000-8000-000000000005',
        'a1000001-0001-4000-8000-000000000005',
        'b1000001-0001-4000-8000-000000000005',
        'Servidor de datos con posible fuga de documento',
        'base_datos', 'Sede Central - Santa Cruz', 'sc-db-01.demo'
    )
ON CONFLICT (id_incidente, id_activo) DO NOTHING;
