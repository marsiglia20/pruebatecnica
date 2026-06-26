-- ============================================================
-- sp_AvanzarVentanaEstacion
-- Avanza una ventana a la siguiente estación en la secuencia.
-- Usa UPDLOCK + HOLDLOCK para bloqueo pesimista: evita que dos
-- operarios procesen la misma ventana simultáneamente.
-- Llama sp_CalcularAvanceOrden dentro de la misma transacción
-- para actualizar el estado de la orden de forma atómica.
-- ============================================================
USE TecnoglassDB;
GO

CREATE OR ALTER PROCEDURE [dbo].[sp_AvanzarVentanaEstacion]
    @identificador_unico  UNIQUEIDENTIFIER,
    @estacion_destino_id  INT,
    @usuario_id           INT,
    @observaciones        NVARCHAR(500) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;   -- rollback automático ante cualquier error

    BEGIN TRANSACTION;

    BEGIN TRY

        -- 1. Bloqueo pesimista: ninguna otra sesión puede leer ni
        --    modificar esta fila hasta que la transacción termine.
        DECLARE @ventana_id         INT,
                @orden_id           INT,
                @estacion_actual_id INT,
                @empacada           BIT;

        SELECT
            @ventana_id         = v.id,
            @orden_id           = v.orden_id,
            @estacion_actual_id = v.estacion_actual_id,
            @empacada           = v.empacada
        FROM dbo.produccion_ventana AS v WITH (UPDLOCK, HOLDLOCK)
        WHERE v.identificador_unico = @identificador_unico;

        -- 2. Validar existencia
        IF @ventana_id IS NULL
            THROW 50001, N'VENTANA_NO_ENCONTRADA: La ventana indicada no existe.', 1;

        -- 3. Validar que no está ya empacada
        IF @empacada = 1
            THROW 50002, N'VENTANA_YA_EMPACADA: La ventana ya fue empacada y no puede avanzar.', 1;

        -- 4. Validar que la estación destino existe
        DECLARE @orden_destino INT;
        SELECT @orden_destino = orden_secuencial
        FROM dbo.produccion_estacion
        WHERE id = @estacion_destino_id;

        IF @orden_destino IS NULL
            THROW 50003, N'ESTACION_NO_ENCONTRADA: La estación destino no existe.', 1;

        -- 5. Validar secuencia
        DECLARE @orden_actual INT = NULL;
        IF @estacion_actual_id IS NOT NULL
            SELECT @orden_actual = orden_secuencial
            FROM dbo.produccion_estacion
            WHERE id = @estacion_actual_id;

        IF @orden_actual IS NULL AND @orden_destino <> 1
            THROW 50004, N'ESTACION_INVALIDA: Ventana sin iniciar debe avanzar a la primera estación (Corte).', 1;

        IF @orden_actual IS NOT NULL AND @orden_destino <> (@orden_actual + 1)
            THROW 50004, N'ESTACION_INVALIDA: La estación destino no es la siguiente en la secuencia.', 1;

        -- 6. Determinar si destino es la estación final
        DECLARE @es_empaque BIT = 0;
        IF NOT EXISTS (
            SELECT 1 FROM dbo.produccion_estacion
            WHERE orden_secuencial = @orden_destino + 1
        )
            SET @es_empaque = 1;

        -- 7. Actualizar ventana
        UPDATE dbo.produccion_ventana
        SET
            estacion_actual_id = @estacion_destino_id,
            empacada           = @es_empaque
        WHERE id = @ventana_id;

        -- 8. Registrar movimiento en historial
        INSERT INTO dbo.produccion_movimientoventana
            (ventana_id, estacion_id, fecha_movimiento, usuario_responsable_id, observaciones)
        VALUES
            (@ventana_id, @estacion_destino_id, GETDATE(), @usuario_id, @observaciones);

        -- 9. Recalcular avance de la orden (atómico, misma transacción)
        EXEC dbo.sp_CalcularAvanceOrden @orden_id, @return_result = 0;

        COMMIT TRANSACTION;

        -- 10. Retornar estado actualizado de la ventana
        SELECT
            v.id,
            v.identificador_unico,
            v.empacada,
            v.orden_id,
            e.id               AS estacion_actual_id,
            e.nombre           AS estacion_actual_nombre,
            e.orden_secuencial AS estacion_orden_secuencial
        FROM dbo.produccion_ventana AS v
        JOIN dbo.produccion_estacion AS e ON v.estacion_actual_id = e.id
        WHERE v.id = @ventana_id;

    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO
