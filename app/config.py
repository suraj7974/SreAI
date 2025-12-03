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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
