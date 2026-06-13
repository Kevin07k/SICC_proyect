// SICC — MongoDB Cochabamba (sicc_cb)
// Colecciones documentales, índices y usuario de aplicación.
// Ejecutado en el primer arranque del contenedor mongo-cochabamba.

db = db.getSiblingDB('sicc_cb');

db.createCollection('evidencias_incidente');
db.createCollection('timeline_eventos');
db.createCollection('telemetria_activo');

db.evidencias_incidente.createIndex({ incidente_uuid: 1, created_at: -1 });
db.evidencias_incidente.createIndex({ 'iocs.valor': 1 });
db.evidencias_incidente.createIndex({ eliminado: 1 });

db.timeline_eventos.createIndex({ incidente_uuid: 1, created_at: 1 });
db.timeline_eventos.createIndex({ autor_uuid: 1 });

db.telemetria_activo.createIndex({ activo_uuid: 1, captured_at: -1 });
db.telemetria_activo.createIndex({ 'hallazgos.severidad': 1 });

db = db.getSiblingDB('admin');
db.createUser({
  user: 'sicc_mongo_api',
  pwd: 'sicc_mongo_api_pass_2024',
  roles: [{ role: 'readWrite', db: 'sicc_cb' }],
});

print('OK sicc_cb: colecciones, índices y usuario sicc_mongo_api');
