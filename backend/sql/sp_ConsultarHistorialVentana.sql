-- ============================================================
-- sp_ConsultarHistorialVentana
-- Retorna el historial completo de una ventana ordenado por
-- fecha de movimiento ascendente.
-- ============================================================
USE TecnoglassDB;
GO

CREATE OR ALTER PROCEDURE [dbo].[sp_ConsultarHistorialVentana]
    @identificador_unico UNIQUEIDENTIFIER
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (
        SELECT 1 FROM dbo.produccion_ventana
        WHERE identificador_unico = @identificador_unico
    )
        THROW 50001, N'VENTANA_NO_ENCONTRADA: La ventana indicada no existe.', 1;

    SELECT
        mv.id,
        mv.fecha_movimiento,
        mv.observaciones,
        e.id               AS estacion_id,
        e.nombre           AS estacion_nombre,
        e.orden_secuencial AS estacion_orden,
        u.id               AS usuario_id,
        u.username         AS usuario_responsable,
        LTRIM(RTRIM(ISNULL(u.first_name, '') + ' ' + ISNULL(u.last_name, '')))
                           AS nombre_completo
    FROM dbo.produccion_movimientoventana AS mv
    JOIN dbo.produccion_ventana           AS v  ON mv.ventana_id            = v.id
    JOIN dbo.produccion_estacion          AS e  ON mv.estacion_id           = e.id
    JOIN dbo.usuarios_usuario             AS u  ON mv.usuario_responsable_id = u.id
    WHERE v.identificador_unico = @identificador_unico
    ORDER BY mv.fecha_movimiento ASC;
END
GO
