// SICC — Seed demo MongoDB Cochabamba
// Cubre los 5 incidentes y 5 activos de mysql/03_seed_demo_operacional.sql

db = db.getSiblingDB('sicc_cb');

const ANALISTA_CB = '11111111-1111-1111-1111-111111111103';

const INCIDENTES = [
  {
    uuid: 'a2000001-0001-4000-8000-000000000001',
    evidencias: [
      {
        tipo: 'ioc',
        metadata: { fuente: 'correo_gateway', severidad_detectada: 'media' },
        iocs: [
          { tipo: 'dominio', valor: 'banco-falso-cb.demo.ejemplo' },
          { tipo: 'ip', valor: '203.0.113.55' },
        ],
        autor_uuid: ANALISTA_CB,
        created_at: new Date('2026-06-01T11:00:00Z'),
      },
      {
        tipo: 'adjunto',
        metadata: {
          nombre_archivo: 'factura_junio.pdf.exe',
          mime: 'application/octet-stream',
          hash_sha256: 'deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef',
        },
        autor_uuid: ANALISTA_CB,
        created_at: new Date('2026-06-01T11:15:00Z'),
      },
    ],
    timeline: [
      {
        tipo_evento: 'reporte_usuario',
        payload: { texto: 'Usuario reporto enlace malicioso en correo' },
        autor_uuid: ANALISTA_CB,
        created_at: new Date('2026-06-01T10:45:00Z'),
      },
    ],
  },
  {
    uuid: 'a2000001-0001-4000-8000-000000000002',
    evidencias: [
      {
        tipo: 'log',
        metadata: { fuente: 'edr', hostname: 'cb-ws-01.demo' },
        lineas: ['2026-06-02T16:30:00Z Heuristica ransomware en cb-ws-01'],
        autor_uuid: ANALISTA_CB,
        created_at: new Date('2026-06-02T16:35:00Z'),
      },
    ],
    timeline: [
      {
        tipo_evento: 'bloqueo_endpoint',
        payload: {
          hostname: 'cb-ws-01.demo',
          accion: 'aislamiento_red',
          regla: 'ransomware_heuristica',
        },
        autor_uuid: ANALISTA_CB,
        created_at: new Date('2026-06-02T16:40:00Z'),
      },
      {
        tipo_evento: 'escalamiento',
        payload: { texto: 'Notificado a central SC; backup verificado intacto' },
        autor_uuid: ANALISTA_CB,
        created_at: new Date('2026-06-02T17:05:00Z'),
      },
    ],
  },
  {
    uuid: 'a2000001-0001-4000-8000-000000000003',
    evidencias: [
      {
        tipo: 'ioc',
        iocs: [{ tipo: 'ip', valor: '192.0.2.44' }],
        metadata: { fuente: 'active_directory' },
        autor_uuid: ANALISTA_CB,
        created_at: new Date('2026-06-03T09:00:00Z'),
      },
    ],
    timeline: [
      {
        tipo_evento: 'bloqueo_cuenta',
        payload: { intentos: 8, origen: '192.0.2.44' },
        autor_uuid: ANALISTA_CB,
        created_at: new Date('2026-06-03T09:15:00Z'),
      },
    ],
  },
  {
    uuid: 'a2000001-0001-4000-8000-000000000004',
    evidencias: [
      {
        tipo: 'log',
        metadata: { servicio: 'portal_cb', duracion_min: 45 },
        lineas: ['2026-06-04T14:00:00Z HTTP 503 en portal sucursal'],
        autor_uuid: ANALISTA_CB,
        created_at: new Date('2026-06-04T14:10:00Z'),
      },
    ],
    timeline: [
      {
        tipo_evento: 'restablecimiento',
        payload: { texto: 'Servicio web restablecido; causa bajo investigacion' },
        autor_uuid: ANALISTA_CB,
        created_at: new Date('2026-06-04T15:00:00Z'),
      },
    ],
  },
  {
    uuid: 'a2000001-0001-4000-8000-000000000005',
    evidencias: [
      {
        tipo: 'adjunto',
        metadata: { dispositivo: 'USB', politica: 'DLP' },
        autor_uuid: ANALISTA_CB,
        created_at: new Date('2026-06-05T12:00:00Z'),
      },
    ],
    timeline: [
      {
        tipo_evento: 'contencion',
        payload: { texto: 'USB bloqueado; revision de logs DLP completada' },
        autor_uuid: ANALISTA_CB,
        created_at: new Date('2026-06-05T12:30:00Z'),
      },
    ],
  },
];

const ACTIVOS = [
  {
    uuid: 'b2000001-0001-4000-8000-000000000001',
    telemetria: {
      tipo_escaneo: 'vulnerabilidades',
      captured_at: new Date('2026-06-04T07:30:00Z'),
      hallazgos: [{ cve: 'CVE-2024-0300', severidad: 'media', descripcion: 'Parche kernel pendiente' }],
      snapshot: { os: 'Linux', hostname: 'cb-srv-01.demo' },
    },
  },
  {
    uuid: 'b2000001-0001-4000-8000-000000000002',
    telemetria: {
      tipo_escaneo: 'configuracion',
      captured_at: new Date('2026-06-04T07:45:00Z'),
      hallazgos: [{ severidad: 'baja', descripcion: 'SSH solo por clave' }],
      snapshot: { servicios: ['sshd', 'nginx'] },
    },
  },
  {
    uuid: 'b2000001-0001-4000-8000-000000000003',
    telemetria: {
      tipo_escaneo: 'vulnerabilidades',
      captured_at: new Date('2026-06-04T08:00:00Z'),
      hallazgos: [
        { cve: 'CVE-2024-0100', severidad: 'alta', descripcion: 'RCE en cliente PDF' },
      ],
      snapshot: { os: 'Windows 10', parches_pendientes: 3 },
    },
  },
  {
    uuid: 'b2000001-0001-4000-8000-000000000004',
    telemetria: {
      tipo_escaneo: 'configuracion',
      captured_at: new Date('2026-06-04T07:00:00Z'),
      hallazgos: [{ severidad: 'media', descripcion: 'Regla NAT legacy sin documentar' }],
      snapshot: { firmware: '12.1.3', reglas_activas: 142 },
    },
  },
  {
    uuid: 'b2000001-0001-4000-8000-000000000005',
    telemetria: {
      tipo_escaneo: 'configuracion',
      captured_at: new Date('2026-06-04T09:00:00Z'),
      hallazgos: [{ severidad: 'baja', descripcion: 'Replica MySQL sincronizada' }],
      snapshot: { motor: 'MySQL 8.0', backups: 'diarios' },
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

print('OK sicc_cb: seed demo — 5 incidentes + 5 activos con documentos Mongo');
