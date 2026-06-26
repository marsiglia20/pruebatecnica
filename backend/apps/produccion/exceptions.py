from rest_framework import status


class DomainException(Exception):
    code = 'DOMAIN_ERROR'
    message = 'Error de dominio'
    http_status = status.HTTP_400_BAD_REQUEST

    def __init__(self, message=None):
        if message:
            self.message = message
        super().__init__(self.message)


class VentanaNoEncontradaException(DomainException):
    code = 'VENTANA_NO_ENCONTRADA'
    http_status = status.HTTP_404_NOT_FOUND

    def __init__(self, identificador=None):
        msg = f"Ventana '{identificador}' no encontrada." if identificador else "Ventana no encontrada."
        super().__init__(msg)


class EstacionInvalidaException(DomainException):
    code = 'ESTACION_INVALIDA'
    http_status = status.HTTP_409_CONFLICT

    def __init__(self, detail='La estación destino no es la siguiente en la secuencia.'):
        super().__init__(detail)


class VentanaYaEmpacadaException(DomainException):
    code = 'VENTANA_YA_EMPACADA'
    http_status = status.HTTP_409_CONFLICT

    def __init__(self):
        super().__init__('La ventana ya fue empacada y no puede avanzar.')


class EstacionNoEncontradaException(DomainException):
    code = 'ESTACION_NO_ENCONTRADA'
    http_status = status.HTTP_404_NOT_FOUND

    def __init__(self, estacion_id=None):
        msg = f"Estación {estacion_id} no existe." if estacion_id else "Estación no encontrada."
        super().__init__(msg)


class OrdenNoEncontradaException(DomainException):
    code = 'ORDEN_NO_ENCONTRADA'
    http_status = status.HTTP_404_NOT_FOUND

    def __init__(self, orden_id=None):
        msg = f"Orden {orden_id} no encontrada." if orden_id else "Orden no encontrada."
        super().__init__(msg)
