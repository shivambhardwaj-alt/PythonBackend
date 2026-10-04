from pydantic_settings import BaseSettings ,SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL :  str
    JWT_SECRET  : str
    JWT_ALGORITHM : str
    REDIS_HOST : str = 'localhost'
    REDIS_PORT : int  = 6379
    MAIL_PASSWORD : str
    MAIL_USERNAME : str 
    MAIL_FROM : str
    MAIL_PORT :  int
    MAIL_SERVER : str 
    model_config = SettingsConfigDict(
        env_file = '.env',
        extra = "ignore"
        
        
        
    )
Config = Settings()