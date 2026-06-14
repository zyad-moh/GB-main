from pydantic_settings import BaseSettings, SettingsConfigDict

class settings(BaseSettings):
    APP_NAME: str # that ia the app_name which inside ".env"
    APP_VERSION: str
   
    FILE_ALLOWED_TYPES:list
    FILE_MAX_SIZE:int 
    FILE_DEFULT_CHUNK_SIZE:int
    MONGODB_URL: str
    MONGODB_DATABASE: str    

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None
    COHERE_API_KEY: str = None
    

    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None
    INPUT_DAFAULT_MAX_CHARACTERS: int = None
    GENERATION_DAFAULT_MAX_TOKENS: int = None
    GENERATION_DAFAULT_TEMPERATURE: float = None
    
    VECTOR_DB_BAKEND : str 
    VECTOR_DB_PATH : str 
    VECTOR_DB_DISTANCE_METHOD : str = None
    PRIMARY_LANG: str = "en"
    DEFAULT_LANG : str = "en"
    GROQ_API_KEY: str = None
    
    # Google Calendar OAuth Configuration
    GOOGLE_CALENDAR_API_URL: str | None = None
    GOOGLE_CALENDAR_CLIENT_SECRETS_FILE: str | None = None
    GOOGLE_CALENDAR_TOKEN_STORAGE_PATH: str | None = None
    GOOGLE_CALENDAR_ID: str = "primary"
    
    # SMTP Email Configuration
    EMAIL_SMTP_HOST: str | None = None
    EMAIL_SMTP_PORT: int = 587
    EMAIL_SMTP_USERNAME: str | None = None
    EMAIL_SMTP_PASSWORD: str | None = None
    EMAIL_FROM_ADDRESS: str | None = None

    # Gmail Ingestion Configuration
    GMAIL_INGESTION_ENABLED: bool = False
    GMAIL_CLIENT_SECRETS_FILE: str | None = None
    GMAIL_TOKEN_STORAGE_PATH: str | None = None
    GMAIL_POLL_INTERVAL_SECONDS: int = 30
    GMAIL_LABEL_FILTER: str = "INBOX"
    GMAIL_QUERY: str = "is:unread"

    class Config():# path of .env, any thing in ".env" will be loaded and i will able to use it(data configration for validation)
        env_file=".env"

def get_settings(): 
    return settings()