from typing import Any, Callable
from fastapi import Request, FastAPI, status
from fastapi.responses import JSONResponse

from app.db.models import Product


class CustomException(Exception):
    """This is the base class for all exceptions"""
    pass


class EmailAlreadyExists(CustomException):
    """User has provided an email for a user who exists during sign up"""
    pass


class UsernameAlreadyExists(CustomException):
    """User has provided an username for a user who exists during sign up"""
    pass

class UserNotFound(CustomException):
    """User not found"""
    pass

class InvalidCredentials(CustomException):
    """User has provided wrong username/email or password during login"""
    pass

class InvalidToken(CustomException):
    """User has provided an invalid or expired token"""
    pass

class AccountNotVerified(CustomException):
    """Account not verified"""
    pass

class InsufficientPermission(CustomException):
    """User does not have the necessary permission to perform an action"""
    pass

class CategoryNotFound(CustomException):
    """Category not found"""
    pass

class ProductNotFound(CustomException):
    """Product not found"""
    pass

def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: Exception):
        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler

def create_exception_handler_with_headers(
        status_code: int, initial_detail: Any, headers: Any
) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: Exception):
        return JSONResponse(content=initial_detail, status_code=status_code, headers=headers)
    return exception_handler



def register_all_errors(app: FastAPI):
    """Register all exception handlers"""
    app.add_exception_handler(
        EmailAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "Email already registered",
                "error_code": "email_exists",
            },
        ),
    )

    app.add_exception_handler(
        UsernameAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "Username already registered. Please choose another username.",
                "error_code": "username_exists",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "error_code": "user_not_found"
            }
        )
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Username or password incorrect. Please try again.",
                "error_code": "username_or_password_incorrect",
            }
        )
    )

    app.add_exception_handler(
        InvalidToken,
        create_exception_handler_with_headers(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Could not validate credentials",
                "error_code": "invalid_token"
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    )

    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Account not verified",
                "hint": "Please check your email for verification details",
                "error_code": "account_not_verified"
            }
        )
    )

    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "You do not have enough permissions to perform this action",
                "error_code": "insufficient_permission",
            }
        )
    )

    app.add_exception_handler(
        CategoryNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Category not found",
                "error_code": "category_not_found"
            }
        )
    )

    app.add_exception_handler(
        ProductNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Product not found",
                "error_code": "Product_not_found"
            }
        )
    )

    # app.exception_handler(ValueError)
    # async def custom_value_error_handler(request: Request, exc: ValueError):
    #     error_message = str(exc).lower()
    #
    #     if "badly formed hexadecimal uuid string" in error_message:
    #         return JSONResponse(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             content={
    #                 "message": "Invalid UUID format. Please provided a valid UUID",
    #                 "error_code": "invalid_uuid_format"
    #             }
    #         )
    #     return JSONResponse(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         content={
    #             "message": "Oops!. An unknown ValueError occurred.",
    #             "detail": str(error_message),
    #             "error_code": "value_error"
    #         }
    #     )
