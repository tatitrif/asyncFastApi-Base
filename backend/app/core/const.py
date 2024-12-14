import enum


class AppEnvironment(enum.Enum):
    LOCAL: str = "local"
    PRODUCTION: str = "production"
    TEST: str = "test"


# https://alembic.sqlalchemy.org/en/latest/naming.html
NAMING_CONVENTION = {
    # Index
    "ix": "ix_%(column_0_label)s",
    # Unique constraint
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    # Check
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    # Foreign key
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    # Primary key
    "pk": "pk_%(table_name)s",
}

PWD_SPECIAL_CHARS = ["@", "$", "_", "-", ".", "!", "#", "%", "^", "&", "*"]
