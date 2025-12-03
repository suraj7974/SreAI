"""Configuration management for AI Chaos Handler"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # SSH Configuration
    ai_chaos_ssh_key_path: str = ""
    ai_chaos_ssh_user: str = "sre-demo"
    ai_chaos_ssh_host: str = ""
    ai_chaos_ssh_port: int = 22
    
    # VM Configuration (for dashboard metrics)
    vm_host: Optional[str] = None
    vm_port: int = 22
    vm_user: str = "sre-demo"
    vm_key_path: Optional[str] = None
    
    # Storage
    incident_storage_path: str = "./incidents"
    
    # API Security
    api_auth_token: str = "dev-token-change-in-production"
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    
    # Optional Integrations
    slack_webhook_url: Optional[str] = None
    do_api_token: Optional[str] = None
    
    # VM Metrics
    metrics_port: int = 9090
    
    # Application
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # AI/LLM Configuration
    google_api_key: str = ""
    google_model: str = "gemini-2.0-flash-exp"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from .env


settings = Settings()
