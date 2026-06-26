from rest_framework.views import exception_handler as drf_handler
from rest_framework.response import Response
from apps.produccion.exceptions import DomainException


def custom_exception_handler(exc, context):
    if isinstance(exc, DomainException):
        return Response(
            {'error': exc.message, 'code': exc.code},
            status=exc.http_status,
        )
    return drf_handler(exc, context)
