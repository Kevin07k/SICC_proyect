USE DB_GestionIncidentes;
GO

INSERT INTO cat_Prioridades (nivel, valor_orden) VALUES
('Baja', 1), ('Media', 2), ('Alta', 3), ('Crítica', 4);

INSERT INTO cat_Estados (nombre) VALUES
('Nuevo'), ('En Investigación'), ('Contenido'), ('Erradicado'), ('Cerrado'), ('Falso Positivo');

INSERT INTO cat_Tipos_Incidente (nombre, descripcion) VALUES
('Phishing', 'Ingeniería social vía correo electrónico.'),
('Malware', 'Software malicioso (virus, ransomware, troyano).'),
('Acceso No Autorizado', 'Inicio de sesión desde fuente desconocida.'),
('Denegación de Servicio (DoS)', 'Ataque de sobrecarga.'),
('Exfiltración de Datos', 'Fuga de información sensible.');

INSERT INTO cat_Sedes (nombre_sede, nivel_criticidad) VALUES
('Sede Central - La Paz', 'Alta'),
('Sucursal El Alto', 'Media'),
('Data Center Externo', 'Crítica');

INSERT INTO Usuarios (nombre_completo, email, rol) VALUES
('Admin Sistema', 'admin@sicc.com', 'Administrador');

PRINT '>> Catálogos Iniciales Cargados Correctamente.';
GO
