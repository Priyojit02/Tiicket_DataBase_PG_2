# ============================================
# CORE CONFIGURATION - Settings Module
# ============================================

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = Field(default="SAP Ticket Management System")
    app_version: str = Field(default="1.0.0")
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)
    secret_key: str = Field(default="change-me-in-production")
    api_version: str = Field(default="v1")
    allowed_hosts: str = Field(default="http://localhost:3000")

    # Server
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)
    
    # Database - Supabase PostgreSQL (separate params)
    db_host: str = Field(default="localhost")
    db_port: int = Field(default=5432)
    db_name: str = Field(default="postgres")
    db_user: str = Field(default="postgres")
    db_password: str = Field(default="password")
    
    # Supabase API (optional)
    supabase_url: str = Field(default="")
    supabase_key: str = Field(default="")
    
    @property
    def database_url(self) -> str:
        """Construct async database URL from parameters"""
        return "sqlite+aiosqlite:///./ticket.db"
    
    @property
    def database_sync_url(self) -> str:
        """Construct sync database URL for migrations"""
        from urllib.parse import quote_plus
        password = quote_plus(self.db_password)
        return f"postgresql://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    # Azure AD - SSO Authentication (Microsoft Login)
    azure_client_id: str = Field(default="033bcde2-d023-405e-8f84-ef33902bfb94")
    azure_tenant_id: str = Field(default="513294a0-3e20-41b2-a970-6d30bf1546fa")
    
    # Email - IMAP Settings
    email_imap_server: str = Field(default="outlook.office365.com")
    email_imap_port: int = Field(default=993)
    email_username: str = Field(default="")
    email_password: str = Field(default="")
    email_folder: str = Field(default="INBOX")
    email_fetch_days: int = Field(default=1)
    email_address: str = Field(default="ratnakar@dev365pwc.com")
    
    # LLM Configuration - Dynamic (just set provider name and API key)
    llm_provider: str = Field(default="openai")  # openai, anthropic, azure, ollama, groq, together, google
    llm_model: str = Field(default="gpt-4-turbo-preview")
    llm_api_key: str = Field(default="")
    llm_base_url: str = Field(default="")
    llm_temperature: float = Field(default=0.3)
    llm_max_tokens: int = Field(default=1000)
    
    # Data Source Mode - Controls what goes into tickets2.ts
    data_source_mode: str = Field(default="combined")  # llm, combined, dummy
    
    # Azure OpenAI specific (only if LLM_PROVIDER=azure)
    azure_openai_endpoint: str = Field(default="")
    azure_openai_deployment: str = Field(default="")
    azure_openai_api_version: str = Field(default="2024-02-15-preview")
    
    # Logging
    log_level: str = Field(default="INFO")

    # Scheduler
    scheduler_enabled: bool = Field(default=False)
    scheduler_email_hour: int = Field(default=8)
    scheduler_email_minute: int = Field(default=0)
    
    @property
    def allowed_origins(self) -> List[str]:
        """Parse allowed hosts into a list"""
        return [host.strip() for host in self.allowed_hosts.split(",")]
    
    @property
    def is_llm_configured(self) -> bool:
        """Check if LLM is properly configured with API key"""
        return bool(
            self.llm_api_key and 
            self.llm_api_key != "sk-your-api-key-here" and
            self.llm_api_key != ""
        )
    
    @property
    def is_development(self) -> bool:
        return self.app_env == "development"
    
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export singleton
settings = get_settings()
