-- ============================================================
-- sp_CalcularAvanceOrden
-- Calcula % avance de una orden y actualiza su estado.
-- Set-based (sin cursores). Seguro como llamada interna desde
-- sp_AvanzarVentanaEstacion (respeta transacción activa) o
-- como llamada directa independiente.
-- ============================================================
USE TecnoglassDB;
GO

CREATE OR ALTER PROCEDURE [dbo].[sp_CalcularAvanceOrden]
    @orden_id     INT,
    @return_result BIT = 1   -- 0 cuando se llama desde otro SP
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @total_ventanas  INT,
            @empacadas       INT,
            @porcentaje      DECIMAL(5, 2),
            @tran_owned      BIT = 0;

    -- Participar en transacción existente o abrir una propia
    IF @@TRANCOUNT = 0
    BEGIN
        BEGIN TRANSACTION;
        SET @tran_owned = 1;
    END

    BEGIN TRY

        SELECT
            @total_ventanas = op.total_ventanas,
            @empacadas      = SUM(CASE WHEN v.empacada = 1 THEN 1 ELSE 0 END)
        FROM dbo.produccion_ordenproduccion op
        LEFT JOIN dbo.produccion_ventana v ON v.orden_id = op.id
        WHERE op.id = @orden_id
        GROUP BY op.total_ventanas;

        SET @porcentaje = CASE
            WHEN ISNULL(@total_ventanas, 0) > 0
            THEN (CAST(ISNULL(@empacadas, 0) AS DECIMAL(10, 2)) / @total_ventanas) * 100
            ELSE 0
        END;

        UPDATE dbo.produccion_ordenproduccion
        SET
            estado = CASE
                WHEN @porcentaje >= 100 THEN 'COMPLETADA'
                WHEN @porcentaje > 0    THEN 'EN_PROCESO'
                ELSE estado
            END,
            fecha_completada = CASE
                WHEN @porcentaje >= 100 AND estado <> 'COMPLETADA' THEN GETDATE()
                ELSE fecha_completada
            END
        WHERE id = @orden_id;

        IF @tran_owned = 1 COMMIT TRANSACTION;

        IF @return_result = 1
            SELECT
                @porcentaje        AS porcentaje_avance,
                ISNULL(@empacadas, 0) AS ventanas_empacadas,
                @total_ventanas    AS total_ventanas;

    END TRY
    BEGIN CATCH
        IF @tran_owned = 1 AND @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO
