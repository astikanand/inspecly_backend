from pydantic_settings import BaseSettings


class CommonSettings(BaseSettings):
    APP_NAME: str = "Inspecly"
    DEBUG_MODE: bool = True


class ServerSettings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000


class DatabaseSettings(BaseSettings):
    DB_URL: str = "mongodb+srv://astikanand:test@cluster0.rm0qt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    # DB_URL: str = "mongodb://127.0.0.1:27017"
    DB_NAME: str = "nut_bolt_test_db" if CommonSettings().DEBUG_MODE else "nut_bolt_db"

    # DB Table Names
    # === Inspection Tables ===
    INSPECTIOIN_COLLECTION: str = "inspection"


class Settings(CommonSettings, ServerSettings, DatabaseSettings):
    pass


app_settings = Settings()
