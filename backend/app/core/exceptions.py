from fastapi import HTTPException, status

from core.const import PWD_SPECIAL_CHARS

CREDENTIALS_EXCEPTION_INVALID = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

CREDENTIALS_EXCEPTION_TYPE = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate type Token",
    headers={"WWW-Authenticate": "Bearer"},
)

CREDENTIALS_EXCEPTION_EXPIRED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Access Token expired",
    headers={"WWW-Authenticate": "Bearer"},
)
CREDENTIALS_EXCEPTION_USER = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token dont have an user",
    headers={"WWW-Authenticate": "Bearer"},
)
CREDENTIALS_EXCEPTION_USER_DB = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="User dont exist already in db",
    headers={"WWW-Authenticate": "Bearer"},
)
CREDENTIALS_EXCEPTION_LOGOUT = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Logout failed",
    headers={"WWW-Authenticate": "Bearer"},
)
CREDENTIALS_EXCEPTION_LOGIN = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Login failed",
    headers={"WWW-Authenticate": "Bearer"},
)

USER_EXCEPTION_WRONG_PARAMETER = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Wrong parameter",
)
USER_EXCEPTION_CONFLICT_USERNAME_SIGNUP = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Username already registered",
)
USER_EXCEPTION_CONFLICT_EMAIL_SIGNUP = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Email already exist",
)
USER_EXCEPTION_USERNAME = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Username must consist of English characters or numbers",
)
USER_EXCEPTION_EMAIL = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Wrong email format",
)
USER_EXCEPTION_CONFIRMATION_PASSWORD = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Password and confirmation password do not match",
)
USER_EXCEPTION_PASSWORD_WEAK = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Insecure password.\n"
    + "Password must be at least 8 characters and "
    + "contain at least one lower, one upper case letter, one digit, and one special sign "
    + f"{PWD_SPECIAL_CHARS}",
)
USER_EXCEPTION_NOT_FOUND_USER = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found",
)
USER_EXCEPTION_NOT_FOUND_USER_EMAIL = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Email not found",
)
USER_EXCEPTION_NOT_FOUND_PAGE = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User Page not found ",
)
USER_EXCEPTION_INACTIVE_USER = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Inactive user",
)
USER_EXCEPTION_PERMISSION_REQUIRED = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Superuser permission required",
)

EXCEPTION_UPLOAD_IMAGE = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Upload image error",
)
EXCEPTION_ID_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Not Found",
)
