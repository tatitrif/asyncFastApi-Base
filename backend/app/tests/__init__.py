from core.config import Settings


class TestSettings(Settings):
    SQLALCHEMY_DATABASE_URI: str = "sqlite+aiosqlite:///./test.db"


def get_test_settings():
    return TestSettings()


test_settings = get_test_settings()
