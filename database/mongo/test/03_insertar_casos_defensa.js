// Inserts para defensa — NO corre solo: copia cada bloque en mongosh o descomenta y ejecuta
// Base: sicc_sc (Santa Cruz). Conectar puerto 27017
//
// QUÉ VAS A INSERTAR:
//
//   1) INCIDENTE — evidencia IoC nueva en el caso phishing
//      incidente_uuid: a1000001-0001-4000-8000-000000000001
//      (incidente demo que ya existe en PostgreSQL)
//      Web: /incidentes/a1000001-0001-4000-8000-000000000001
//
//   2) ACTIVO — telemetría de escaneo en sc-ws-01
//      activo_uuid: b1000001-0001-4000-8000-000000000003
//      (activo demo que ya existe en PostgreSQL)
//      Web: /activos/b1000001-0001-4000-8000-000000000003
//
// Marca común: metadata.origen = 'defensa_viva' (para borrarlo después si quieres)

db = db.getSiblingDB('sicc_sc');

// =============================================================================
// INSERT 1 — Evidencia IoC en incidente phishing
// Ejecuta esto en la defensa cuando te pidan insertar en Mongo un incidente
// =============================================================================

db.evidencias_incidente.insertOne({
  incidente_uuid: 'a1000001-0001-4000-8000-000000000001',
  tipo: 'ioc',
  metadata: {
    origen: 'defensa_viva',
    fuente: 'analista_manual',
    nota: 'IoC agregado en vivo durante la defensa',
  },
  iocs: [
    { tipo: 'ip', valor: '203.0.113.99' },
    { tipo: 'dominio', valor: 'phishing-defensa.demo.ejemplo' },
  ],
  autor_uuid: '11111111-1111-1111-1111-111111111102',
  created_at: new Date(),
  eliminado: false,
});

// Ver que quedó (mismo incidente):
db.evidencias_incidente.find({ incidente_uuid: 'a1000001-0001-4000-8000-000000000001', eliminado: false }).sort({ created_at: -1 }).pretty();

// =============================================================================
// INSERT 2 — Telemetría en activo sc-ws-01
// Ejecuta esto cuando te pidan insertar algo ligado a un activo
// =============================================================================

db.telemetria_activo.insertOne({
  activo_uuid: 'b1000001-0001-4000-8000-000000000003',
  tipo_escaneo: 'vulnerabilidades',
  captured_at: new Date(),
  hallazgos: [
    {
      cve: 'CVE-DEFENSA-2026',
      severidad: 'alta',
      descripcion: 'Hallazgo insertado en vivo — demo defensa',
    },
  ],
  snapshot: {
    origen: 'defensa_viva',
    hostname: 'sc-ws-01.demo',
    os: 'Windows 11',
  },
  eliminado: false,
});

// Ver que quedó (mismo activo):
db.telemetria_activo.find({ activo_uuid: 'b1000001-0001-4000-8000-000000000003', eliminado: false }).sort({ captured_at: -1 }).pretty();

// =============================================================================
// Limpiar después de la defensa (opcional)
// =============================================================================

// db.evidencias_incidente.deleteMany({ 'metadata.origen': 'defensa_viva' });
// db.telemetria_activo.deleteMany({ 'snapshot.origen': 'defensa_viva' });

print('Archivo de inserts listo. Descomenta INSERT 1 o INSERT 2 y ejecuta en mongosh.');
