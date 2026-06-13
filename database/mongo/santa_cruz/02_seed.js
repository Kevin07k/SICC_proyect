// SICC — Seed demo MongoDB Santa Cruz
// Cubre los 5 incidentes y 5 activos de postgres/03_seed_demo_operacional.sql

db = db.getSiblingDB('sicc_sc');

const ANALISTA_SC = '11111111-1111-1111-1111-111111111102';
const ADMIN = '11111111-1111-1111-1111-111111111101';

const INCIDENTES = [
  {
    uuid: 'a1000001-0001-4000-8000-000000000001',
    evidencias: [
      {
        tipo: 'ioc',
        metadata: { fuente: 'EDR', severidad_detectada: 'media' },
        iocs: [
          { tipo: 'hash_sha256', valor: 'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456' },
          { tipo: 'dominio', valor: 'login-seguro-sc.demo.ejemplo' },
          { tipo: 'ip', valor: '198.51.100.10' },
        ],
        autor_uuid: ANALISTA_SC,
        created_at: new Date('2026-06-01T08:30:00Z'),
      },
      {
        tipo: 'log',
        metadata: { fuente: 'correo', asunto: 'Actualizacion urgente de credenciales' },
        lineas: [
          '2026-06-01T08:15:00Z Usuario abrio enlace desde Outlook',
          '2026-06-01T08:16:12Z Proxy bloqueo descarga .html sospechosa',
        ],
        autor_uuid: ANALISTA_SC,
        created_at: new Date('2026-06-01T08:45:00Z'),
      },
    ],
    timeline: [
      {
        tipo_evento: 'reporte_usuario',
        payload: { texto: 'Usuario reporto correo de phishing interno' },
        autor_uuid: ANALISTA_SC,
        created_at: new Date('2026-06-01T08:00:00Z'),
      },
      {
        tipo_evento: 'analisis_inicial',
        payload: { texto: 'Enlace a dominio externo; muestra preservada' },
        autor_uuid: ANALISTA_SC,
        created_at: new Date('2026-06-01T09:00:00Z'),
      },
    ],
  },
  {
    uuid: 'a1000001-0001-4000-8000-000000000002',
    evidencias: [
      {
        tipo: 'ioc',
        metadata: { fuente: 'antivirus', hostname: 'sc-ws-01.demo' },
        iocs: [{ tipo: 'hash_sha256', valor: 'malware-demo-sc-ws-01-hash-ejemplo' }],
        autor_uuid: ANALISTA_SC,
        created_at: new Date('2026-06-02T13:00:00Z'),
      },
    ],
    timeline: [
      {
        tipo_evento: 'deteccion_edr',
        payload: { hostname: 'sc-ws-01.demo', proceso: 'sospechoso.exe', accion: 'cuarentena' },
        autor_uuid: ANALISTA_SC,
        created_at: new Date('2026-06-02T14:00:00Z'),
      },
      {
        tipo_evento: 'nota_analista',
        payload: { texto: 'Muestra enviada a sandbox; pendiente confirmacion de familia' },
        autor_uuid: ADMIN,
        created_at: new Date('2026-06-02T15:20:00Z'),
      },
    ],
  },
  {
    uuid: 'a1000001-0001-4000-8000-000000000003',
    evidencias: [
      {
        tipo: 'log',
        metadata: { fuente: 'vpn_gateway' },
        lineas: [
          '2026-06-03T02:10:00Z 12 intentos fallidos desde 203.0.113.88',
          '2026-06-03T02:11:00Z Cuenta bloqueada automaticamente',
        ],
        autor_uuid: ADMIN,
        created_at: new Date('2026-06-03T02:30:00Z'),
      },
    ],
    timeline: [
      {
        tipo_evento: 'bloqueo_cuenta',
        payload: { usuario: 'vpn-demo-sc', intentos: 12 },
        autor_uuid: ADMIN,
        created_at: new Date('2026-06-03T02:15:00Z'),
      },
    ],
  },
  {
    uuid: 'a1000001-0001-4000-8000-000000000004',
    evidencias: [
      {
        tipo: 'captura',
        metadata: { fuente: 'ids_perimetro', pico_mbps: 850 },
        iocs: [{ tipo: 'ip', valor: '198.18.0.50' }],
        autor_uuid: ANALISTA_SC,
        created_at: new Date('2026-06-04T11:00:00Z'),
      },
    ],
    timeline: [
      {
        tipo_evento: 'alerta_dos',
        payload: { texto: 'Pico anomalo en sc-fw-01; regla rate-limit aplicada' },
        autor_uuid: ANALISTA_SC,
        created_at: new Date('2026-06-04T11:05:00Z'),
      },
    ],
  },
  {
    uuid: 'a1000001-0001-4000-8000-000000000005',
    evidencias: [
      {
        tipo: 'adjunto',
        metadata: {
          nombre_archivo: 'informe_confidencial.pdf',
          hash_sha256: 'fuga-doc-sc-demo-hash-ejemplo-000005',
        },
        autor_uuid: ADMIN,
        created_at: new Date('2026-06-05T16:00:00Z'),
      },
    ],
    timeline: [
      {
        tipo_evento: 'contencion',
        payload: { texto: 'Acceso al share revocado; auditoria de copias USB iniciada' },
        autor_uuid: ADMIN,
        created_at: new Date('2026-06-05T16:30:00Z'),
      },
    ],
  },
];

const ACTIVOS = [
  {
    uuid: 'b1000001-0001-4000-8000-000000000001',
    telemetria: {
      tipo_escaneo: 'configuracion',
      captured_at: new Date('2026-06-03T10:30:00Z'),
      hallazgos: [{ severidad: 'baja', descripcion: 'TLS 1.0 deshabilitado correctamente' }],
      snapshot: { puertos_abiertos: [22, 443], servicios: ['sshd', 'nginx'] },
    },
  },
  {
    uuid: 'b1000001-0001-4000-8000-000000000002',
    telemetria: {
      tipo_escaneo: 'vulnerabilidades',
      captured_at: new Date('2026-06-03T11:00:00Z'),
      hallazgos: [{ cve: 'CVE-2024-0200', severidad: 'media', descripcion: 'OpenSSL parche pendiente' }],
      snapshot: { os: 'Linux', hostname: 'sc-srv-02.demo' },
    },
  },
  {
    uuid: 'b1000001-0001-4000-8000-000000000003',
    telemetria: {
      tipo_escaneo: 'vulnerabilidades',
      captured_at: new Date('2026-06-03T09:00:00Z'),
      hallazgos: [
        { cve: 'CVE-2024-0001', severidad: 'alta', descripcion: 'Parche pendiente en navegador' },
        { cve: 'CVE-2024-0002', severidad: 'media', descripcion: 'Servicio SMB expuesto localmente' },
      ],
      snapshot: { os: 'Windows 11', agente_edr: 'activo' },
    },
  },
  {
    uuid: 'b1000001-0001-4000-8000-000000000004',
    telemetria: {
      tipo_escaneo: 'configuracion',
      captured_at: new Date('2026-06-04T08:00:00Z'),
      hallazgos: [{ severidad: 'media', descripcion: 'Regla NAT sin documentar en sc-fw-01' }],
      snapshot: { firmware: '12.1.2', reglas_activas: 138 },
    },
  },
  {
    uuid: 'b1000001-0001-4000-8000-000000000005',
    telemetria: {
      tipo_escaneo: 'configuracion',
      captured_at: new Date('2026-06-04T09:00:00Z'),
      hallazgos: [{ severidad: 'baja', descripcion: 'Backups verificados OK' }],
      snapshot: { motor: 'PostgreSQL 16', rol: 'replica_logica_off' },
    },
  },
];

function seedEvidencias(incidenteUuid, docs) {
  const existentes = db.evidencias_incidente.countDocuments({ incidente_uuid: incidenteUuid });
  if (existentes >= docs.length) return;
  const faltantes = docs.slice(existentes);
  if (faltantes.length === 0) return;
  db.evidencias_incidente.insertMany(
    faltantes.map((d) => ({
      incidente_uuid: incidenteUuid,
      eliminado: false,
      ...d,
    })),
  );
}

function seedTimeline(incidenteUuid, docs) {
  const existentes = db.timeline_eventos.countDocuments({ incidente_uuid: incidenteUuid });
  if (existentes >= docs.length) return;
  const faltantes = docs.slice(existentes);
  if (faltantes.length === 0) return;
  db.timeline_eventos.insertMany(
    faltantes.map((d) => ({
      incidente_uuid: incidenteUuid,
      eliminado: false,
      ...d,
    })),
  );
}

function seedTelemetria(activoUuid, doc) {
  if (db.telemetria_activo.countDocuments({ activo_uuid: activoUuid }) > 0) return;
  db.telemetria_activo.insertOne({ activo_uuid: activoUuid, eliminado: false, ...doc });
}

INCIDENTES.forEach((inc) => {
  seedEvidencias(inc.uuid, inc.evidencias);
  seedTimeline(inc.uuid, inc.timeline);
});

ACTIVOS.forEach((act) => {
  seedTelemetria(act.uuid, act.telemetria);
});

print('OK sicc_sc: seed demo — 5 incidentes + 5 activos con documentos Mongo');
