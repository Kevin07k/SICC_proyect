// Muestra demo Mongo — Santa Cruz (sicc_sc). Cochabamba: sicc_cb puerto 27018
// Ver README.md para ejecutar con mongosh --file

db = db.getSiblingDB('sicc_sc');

print('');
print('--- Totales rápidos ---');
print('evidencias:', db.evidencias_incidente.countDocuments({ eliminado: false }));
print('timeline:  ', db.timeline_eventos.countDocuments({ eliminado: false }));
print('telemetria:', db.telemetria_activo.countDocuments({ eliminado: false }));
print('');

// =============================================================================
// CASO 1 — Incidente phishing (para la defensa / presentación)
// SQL y Mongo enlazados por: a1000001-0001-4000-8000-000000000001
// En la web: /incidentes/a1000001-0001-4000-8000-000000000001
// Qué mostrar: IoCs (IP, dominio, hash) + log del correo + timeline de la investigación
// =============================================================================

print('=== CASO 1: incidente phishing — evidencias ===');
db.evidencias_incidente
  .find({ incidente_uuid: 'a1000001-0001-4000-8000-000000000001', eliminado: false })
  .sort({ created_at: -1 })
  .pretty();

print('=== CASO 1: incidente phishing — timeline ===');
db.timeline_eventos
  .find({ incidente_uuid: 'a1000001-0001-4000-8000-000000000001', eliminado: false })
  .sort({ created_at: 1 })
  .pretty();

print('');

// =============================================================================
// CASO 2 — Activo con escaneo y vulnerabilidad ALTA (para la defensa / presentación)
// SQL y Mongo enlazados por: b1000001-0001-4000-8000-000000000003
// En la web: /activos/b1000001-0001-4000-8000-000000000003
// Qué mostrar: hallazgos con severidad alta + snapshot del equipo (Windows, EDR)
// =============================================================================

print('=== CASO 2: activo sc-ws-01 — telemetría ===');
db.telemetria_activo
  .find({ activo_uuid: 'b1000001-0001-4000-8000-000000000003', eliminado: false })
  .sort({ captured_at: -1 })
  .pretty();

print('');
print('Listo.');
