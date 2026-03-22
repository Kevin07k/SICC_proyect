/*
================================================================================
 ARCHIVO 2: POBLADO DE DATOS MASIVOS (DML)
 PROYECTO: SICC - Gestión de Incidentes
 DESCRIPCIÓN: Genera incidentes, usuarios y activos para probar el Dashboard.
================================================================================
*/

USE DB_GestionIncidentes;
GO


PRINT '--- 1. Poblando más Usuarios (Analistas) ---';
INSERT INTO Usuarios
    (nombre_completo, email, rol)
VALUES
    ('Ana Lopez', 'ana.lopez@tuempresa.com', 'Analista Nivel 1'),
    ('Carlos Vera', 'carlos.vera@tuempresa.com', 'Analista Nivel 2');
GO

PRINT '--- 2. Poblando Activos (Equipos) ---';
-- Nota: Usamos 'propietario' en lugar de 'dueño_negocio' para coincidir con la estructura
INSERT INTO Activos
    (hostname, direccion_ip, tipo_activo, propietario)
VALUES
    ('SRV-WEB-01', '192.168.1.10', 'Servidor', 'TI'),
    ('SRV-DB-01', '192.168.1.11', 'Servidor', 'TI'),
    ('LAPTOP-FIN-015', '10.10.5.20', 'Laptop', 'Finanzas'),
    ('PC-MKT-002', '10.10.7.30', 'Desktop', 'Marketing'),
    ('LAPTOP-GER-001', '10.10.1.5', 'Laptop', 'Gerencia'),
    ('FW-PERIMETRAL-01', '200.50.10.1', 'Firewall', 'TI');
GO

PRINT '--- 3. Poblando Incidentes ---';
-- Incidente 1 (Crítico, Cerrado)
INSERT INTO Incidentes
    (titulo, descripcion_detallada, id_tipo, id_prioridad, id_estado, id_usuario_asignado, fecha_cierre)
VALUES
    ('Ransomware en SRV-DB-01', 'Se detectó y erradicó un ransomware en el servidor de base de datos.', 2, 4, 5, 1, GETDATE());

-- Incidente 2 (Alto, En Investigación)
INSERT INTO Incidentes
    (titulo, descripcion_detallada, id_tipo, id_prioridad, id_estado, id_usuario_asignado)
VALUES
    ('Campaña de Phishing a Finanzas', 'Múltiples usuarios de finanzas reportaron un correo sospechoso.', 1, 3, 2, 2);

-- Incidente 3 (Medio, Nuevo)
INSERT INTO Incidentes
    (titulo, descripcion_detallada, id_tipo, id_prioridad, id_estado, id_usuario_asignado)
VALUES
    ('Virus en PC de Marketing', 'El antivirus detectó un troyano en PC-MKT-002.', 2, 2, 1, 3);

-- Incidente 4 (Alto, Falso Positivo)
INSERT INTO Incidentes
    (titulo, descripcion_detallada, id_tipo, id_prioridad, id_estado, id_usuario_asignado, fecha_cierre)
VALUES
    ('Alerta de DoS en Firewall', 'La alerta del firewall fue un falso positivo por un backup.', 4, 3, 6, 1, GETDATE());

-- Incidente 5 (Crítico, En Investigación)
INSERT INTO Incidentes
    (titulo, descripcion_detallada, id_tipo, id_prioridad, id_estado, id_usuario_asignado)
VALUES
    ('Login sospechoso en Laptop Gerencia', 'Se detectó un login desde una IP desconocida en LAPTOP-GER-001.', 3, 4, 2, 2);

-- Incidente 6 (Bajo, Nuevo, Sin Asignar)
INSERT INTO Incidentes
    (titulo, descripcion_detallada, id_tipo, id_prioridad, id_estado, id_usuario_asignado)
VALUES
    ('SPAM Reportado', 'Usuario reporta SPAM genérico.', 1, 1, 1, NULL);

-- Incidente 7 (Medio, Cerrado)
INSERT INTO Incidentes
    (titulo, descripcion_detallada, id_tipo, id_prioridad, id_estado, id_usuario_asignado, fecha_cierre)
VALUES
    ('Intento de Phishing (Bloqueado)', 'El filtro de correo bloqueó un intento de phishing.', 1, 2, 5, 3, GETDATE());

-- Incidente 8 (Crítico, En Investigación)
INSERT INTO Incidentes
    (titulo, descripcion_detallada, id_tipo, id_prioridad, id_estado, id_usuario_asignado)
VALUES
    ('Posible Exfiltración de Datos', 'Tráfico anómalo saliendo de SRV-WEB-01.', 5, 4, 2, 1);
GO

PRINT '--- 4. Vinculando Incidentes y Activos ---';
INSERT INTO Incidentes_Activos
    (id_incidente, id_activo, notas_relacion)
VALUES
    (1, 2, 'Servidor de BD fue el paciente cero.'),
    (2, 3, 'Usuario en LAPTOP-FIN-015 reportó el correo.'),
    (3, 4, 'PC-MKT-002 está en cuarentena.'),
    (4, 6, 'Alerta generada por el FW-PERIMETRAL-01.'),
    (5, 5, 'Login detectado en el equipo del gerente.'),
    (8, 1, 'Tráfico anómalo saliendo de SRV-WEB-01.');
GO

PRINT '--- 5. Poblando Bitácora de Investigación ---';
-- Bitácoras para Ransomware
INSERT INTO Bitacora_Investigacion
    (id_incidente, id_usuario, comentario)
VALUES
    (1, 1, 'Alerta recibida. Servidor aislado de la red.'),
    (1, 1, 'Ransomware identificado. Aplicando parche y restaurando backup.'),
    (1, 1, 'Servidor limpio. Incidente cerrado.');

-- Bitácora para Phishing
INSERT INTO Bitacora_Investigacion
    (id_incidente, id_usuario, comentario)
VALUES
    (2, 2, 'Reporte recibido. Solicitando cabeceras del correo al usuario.');

-- Bitácora para Falso Positivo
INSERT INTO Bitacora_Investigacion
    (id_incidente, id_usuario, comentario)
VALUES
    (4, 1, 'Se investigó la alerta de DoS. Se confirma que era el proceso de backup nocturno. Cerrando como Falso Positivo.');

-- Bitácora para Login
INSERT INTO Bitacora_Investigacion
    (id_incidente, id_usuario, comentario)
VALUES
    (5, 2, 'IP de origen (X.X.X.X) parece ser un proxy. Contactando al gerente para verificar.');

-- Bitácora para Exfiltración
INSERT INTO Bitacora_Investigacion
    (id_incidente, id_usuario, comentario)
VALUES
    (8, 1, 'Iniciando captura de paquetes en SRV-WEB-01.');
GO

PRINT '>> Datos de prueba cargados correctamente.';
GO