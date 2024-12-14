from typing import Self

# from core.const import PWD_SPECIAL_CHARS
from pydantic import BaseModel, EmailStr, field_validator, model_validator

from core import exceptions
from schemas.base import OutMixin


class ValidEmail(BaseModel):
    email: EmailStr | None = None


class ValidUsername(BaseModel):
    username: str

    @field_validator("username")
    def value(cls, value: str) -> str:
        value = value.lower().strip()
        if isinstance(value, str):
            if not (value.isalnum() and value.isascii()):
                raise exceptions.USER_EXCEPTION_USERNAME
        return value


class UserSchema(ValidEmail, ValidUsername):
    fullname: str | None = None

    @field_validator("username")
    def validate_lower(cls, value):
        if value:
            return value.lower()


class UserDBPasswords(BaseModel):
    hashed_password: str


class UserConfirmPasswords(BaseModel):
    password: str
    confirmation_password: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        print(self.password, self.confirmation_password)
        if self.password != self.confirmation_password:
            raise exceptions.USER_EXCEPTION_CONFIRMATION_PASSWORD
        return self

    # @field_validator("password")
    # def check_weak_password(cls, field: str) -> str:
    #     lower_count, upper_count, special_char_count, digit_count = 0, 0, 0, 0
    #     if len(field) >= 8:
    #         for char in field:
    #             lower_count += int(char.islower())
    #             upper_count += int(char.isupper())
    #             digit_count += int(char.isdigit())
    #             special_char_count += int(char in PWD_SPECIAL_CHARS)
    #     checks = [lower_count, upper_count, digit_count, special_char_count]
    #     if not all(checks):
    #         raise exceptions.USER_EXCEPTION_PASSWORD_WEAK
    #     return field


class UserCreateSchema(UserConfirmPasswords, UserSchema):
    pass


class UserCreateDBSchema(UserDBPasswords, UserSchema):
    pass


class UserUpdateSchema(ValidEmail):
    fullname: str | None = None


class UserFilterSchema(ValidEmail):
    username: str | None = None
    fullname: str | None = None

    @field_validator("username")
    def validate_lower(cls, value):
        if value:
            return value.lower()


class UserResponse(UserSchema, OutMixin):
    image: str | None = None


class UserListResponse:
    data: list[UserResponse]
