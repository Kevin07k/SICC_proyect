// Consultas de defensa — mismas que usa la API (mongo_repo.py)
// Santa Cruz. Cochabamba: sicc_cb + UUID a200... / b200...

db = db.getSiblingDB('sicc_sc');

// --- Evidencias (como GET /incidentes/{uuid}/evidencias) ---
// Cambia el incidente_uuid para otro caso
print('');
print('=== evidencias incidente 1 ===');
db.evidencias_incidente.find(
  { incidente_uuid: 'a1000001-0001-4000-8000-000000000001', eliminado: false },
).sort({ created_at: -1 });

// --- Timeline (como GET /incidentes/{uuid}/timeline) ---
print('');
print('=== timeline incidente 1 ===');
db.timeline_eventos.find(
  { incidente_uuid: 'a1000001-0001-4000-8000-000000000001', eliminado: false },
).sort({ created_at: 1 });

// --- Telemetría (como GET /activos/{uuid}/telemetria) ---
// Cambia activo_uuid — el 003 tiene severidad alta
print('');
print('=== telemetria activo 3 ===');
db.telemetria_activo.find(
  { activo_uuid: 'b1000001-0001-4000-8000-000000000003', eliminado: false },
).sort({ captured_at: -1 });

// --- Buscar por IoC (no está en la web, sí en mongosh) ---
// Cambia la IP o pon un dominio del seed
print('');
print('=== buscar por IoC ===');
db.evidencias_incidente.find({ 'iocs.valor': '198.51.100.10', eliminado: false });

// --- Hallazgos graves (tampoco en la web) ---
// Cambia 'alta' por 'media' o 'baja'
print('');
print('=== severidad alta ===');
db.telemetria_activo.find({ 'hallazgos.severidad': 'alta', eliminado: false });

// --- Solo tipo ioc ---
// Cambia tipo: log | captura | adjunto
print('');
print('=== solo evidencias ioc ===');
db.evidencias_incidente.find({ tipo: 'ioc', eliminado: false });

// --- EXPLAIN: en la salida busca IXSCAN e indexName ---
print('');
print('=== explain evidencias ===');
db.evidencias_incidente
  .find({ incidente_uuid: 'a1000001-0001-4000-8000-000000000001', eliminado: false })
  .sort({ created_at: -1 })
  .explain('executionStats');

print('');
print('=== explain IoC ===');
db.evidencias_incidente
  .find({ 'iocs.valor': '198.51.100.10', eliminado: false })
  .explain('executionStats');

print('');
print('=== explain telemetria ===');
db.telemetria_activo
  .find({ activo_uuid: 'b1000001-0001-4000-8000-000000000003', eliminado: false })
  .sort({ captured_at: -1 })
  .explain('executionStats');

print('');
print('Listo.');
