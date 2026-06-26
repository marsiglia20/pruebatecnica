-- ============================================================
-- 00_ddl_seed_estaciones.sql
-- Ejecutar DESPUÉS de: python manage.py migrate
-- Siembra catálogo de estaciones (idempotente)
-- ============================================================
USE TecnoglassDB;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.produccion_estacion WHERE orden_secuencial = 1)
BEGIN
    INSERT INTO dbo.produccion_estacion (nombre, orden_secuencial, descripcion)
    VALUES
        ('Corte',    1, 'Corte de perfiles de aluminio'),
        ('Troquel',  2, 'Troquelado y perforación de perfiles'),
        ('Ensamble', 3, 'Ensamble de marco y vidrio'),
        ('Empaque',  4, 'Empaque y etiquetado final');

    PRINT 'Estaciones sembradas correctamente.';
END
ELSE
    PRINT 'Estaciones ya existen. Seed omitido.';
GO
