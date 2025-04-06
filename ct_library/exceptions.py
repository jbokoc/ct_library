from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, NoResultFound


class AwesomeException(Exception):
    """
    Base exception
    """


class Forbidden(AwesomeException):
    pass


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register exception handlers for the application.

    Args:
        app (FastAPI): The FastAPI application instance.
    """

    @app.exception_handler(NoResultFound)
    def object_not_found_exception_handler(
        request: Request, exc: NoResultFound
    ) -> JSONResponse:
        """
        Handle NoResultFound exceptions.
        Returns:
            JONResponse: A JSON response with the error message.
        """
        return JSONResponse(
            status_code=404,
            content={"detail": "Object not found"},
        )

    @app.exception_handler(Forbidden)
    def forbidden_exception_handler(request: Request, exc: Forbidden) -> JSONResponse:
        """
        Handle Forbidden.
        """
        return JSONResponse(
            status_code=403,
            content={"detail": "Forbidden"},
        )

    @app.exception_handler(IntegrityError)
    def integrity_error_exception_handler(
        request: Request, exc: IntegrityError
    ) -> JSONResponse:
        """
        Handle IntegrityError exceptions.
        Returns:
            JONResponse: A JSON response with the error message.
        """
        return JSONResponse(
            status_code=409,
            content={
                "detail": "Integrity error: Entity cannot be deleted as it is referenced elsewhere"
            },
        )
