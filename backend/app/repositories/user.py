from models.user import User
from repositories.base import SQLAlchemyRepository
from schemas.user import UserCreateDBSchema, UserUpdateSchema


class UserRepository(SQLAlchemyRepository):
    model = User
    create_schema: UserCreateDBSchema
    update_schema: UserUpdateSchema
