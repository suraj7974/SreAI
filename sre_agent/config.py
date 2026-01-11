"""
SRE Agent Configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # ==========================================================================
    # Prometheus Configuration
    # ==========================================================================
    prometheus_url: str = "http://localhost:9090"
    prometheus_query_timeout: int = 30

    # ==========================================================================
    # Grafana Configuration
    # ==========================================================================
    grafana_url: str = "http://localhost:3001"
    grafana_api_key: Optional[str] = None

    # ==========================================================================
    # SSH Configuration (for remediation actions)
    # ==========================================================================
    ssh_key_path: Optional[str] = None
    ssh_user: str = "sre-agent"
    ssh_port: int = 22
    ssh_timeout: int = 30

    # ==========================================================================
    # Target VMs Configuration
    # ==========================================================================
    target_vms: str = ""  # Comma-separated list of VM IPs

    @property
    def target_vm_list(self) -> List[str]:
        """Parse target VMs from comma-separated string"""
        if not self.target_vms:
            return []
        return [vm.strip() for vm in self.target_vms.split(",") if vm.strip()]

    # ==========================================================================
    # LLM Configuration
    # ==========================================================================
    google_api_key: str = ""
    google_model: str = "gemini-2.0-flash-exp"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 4000

    # ==========================================================================
    # Agent Configuration
    # ==========================================================================
    monitoring_interval: int = 60  # seconds between monitoring checks
    alert_cooldown: int = 300  # seconds before re-alerting on same issue
    max_agent_iterations: int = 10  # max reasoning loops per agent

    # Thresholds for automatic incident detection
    cpu_warning_threshold: float = 80.0
    cpu_critical_threshold: float = 95.0
    memory_warning_threshold: float = 85.0
    memory_critical_threshold: float = 95.0
    disk_warning_threshold: float = 80.0
    disk_critical_threshold: float = 95.0

    # ==========================================================================
    # Storage Configuration
    # ==========================================================================
    incident_storage_path: str = "./incidents"

    # ==========================================================================
    # API Configuration
    # ==========================================================================
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_auth_token: str = "dev-token-change-in-production"
    allowed_origins: str = (
        "http://localhost:3000,http://localhost:3001,http://localhost:8000"
    )

    # ==========================================================================
    # Notification Configuration
    # ==========================================================================
    slack_webhook_url: Optional[str] = None

    # ==========================================================================
    # Debug
    # ==========================================================================
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


settings = Settings()
