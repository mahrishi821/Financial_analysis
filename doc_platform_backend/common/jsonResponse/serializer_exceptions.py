import http
from rest_framework.views import exception_handler
from rest_framework.response import Response

def serializer_exceptions(exc, context):
    """
    Custom serializer exception handler to format API responses.
    """
    # Call the default exception handler to get the standard response
    resp = exception_handler(exc, context)

    # If the exception handler returns a response, customize it
    if resp is not None:
        resp.data = {
            'success': False,
            'exception': {
                'code': 400,
                'message': "bad request",
                'description': str(exc),
            }
        }
        resp.status_code = http.HTTPStatus.OK  # Ensure the status code is 200

    # Handle exceptions that are not processed by the default exception handler
    else:
        resp = Response(
            {
                'success': False,
                'exception': {
                    'code': 400,
                    'message': "Error",
                    'description': str(exc),
                },
            },
            status=http.HTTPStatus.OK,  # Ensure the status code is 200
        )

    return resp
