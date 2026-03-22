USE DB_GestionIncidentes;
GO

PRINT '--- 1. Creando cat_Sedes ---';
CREATE TABLE cat_Sedes (
    id_sede INT PRIMARY KEY IDENTITY(1,1),
    nombre_sede NVARCHAR(100) NOT NULL UNIQUE,
    nivel_criticidad NVARCHAR(50) NOT NULL
);
GO

PRINT '--- 2. Añadiendo id_sede a Activos e implementando Foreign Key ---';
ALTER TABLE Activos
ADD id_sede INT NULL;
GO

ALTER TABLE Activos
ADD CONSTRAINT FK_Activos_Sede FOREIGN KEY (id_sede) REFERENCES cat_Sedes(id_sede);
GO

PRINT '--- 3. Creando Vista vw_Auditoria_Incidentes_Sede ---';
GO
CREATE OR ALTER VIEW vw_Auditoria_Incidentes_Sede AS
SELECT 
    i.id_incidente,
    i.titulo AS titulo_incidente,
    i.fecha_creacion,
    e.nombre AS estado_incidente,
    a.hostname AS activo_afectado,
    a.tipo_activo,
    s.nombre_sede AS sede_afectada,
    s.nivel_criticidad AS criticidad_sede
FROM Incidentes i
INNER JOIN Incidentes_Activos ia ON i.id_incidente = ia.id_incidente
INNER JOIN Activos a ON ia.id_activo = a.id_activo
INNER JOIN cat_Estados e ON i.id_estado = e.id_estado
LEFT JOIN cat_Sedes s ON a.id_sede = s.id_sede;
GO

PRINT '--- 4. Insertando Datos de Prueba para Sedes ---';
INSERT INTO cat_Sedes (nombre_sede, nivel_criticidad) VALUES
('Sede Central - La Paz', 'Alta'),
('Sucursal El Alto', 'Media'),
('Data Center Externo', 'Crítica');

-- Asignar sedes de forma aleatoria/representativa a los activos existentes
UPDATE Activos SET id_sede = 1 WHERE id_activo IN (1, 3, 5);
UPDATE Activos SET id_sede = 2 WHERE id_activo IN (4);
UPDATE Activos SET id_sede = 3 WHERE id_activo IN (2, 6);
GO

PRINT '>> SPRINT 1: DDL y Vistas creados correctamente.';
GO
