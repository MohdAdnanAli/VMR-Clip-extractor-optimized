"""Configuration management for the monitoring system."""
import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Any
from pathlib import Path


@dataclass
class AlertConfiguration:
    name: str
    condition: str  # Python expression
    threshold: float
    time_window: int  # minutes
    notification_channels: List[str]
    enabled: bool = True
    cooldown_period: int = 5  # minutes


@dataclass
class MonitoringConfig:
    log_level: str = "INFO"
    database_path: str = "monitoring.db"
    log_file_path: str = "monitoring.log"
    max_log_file_size: int = 10 * 1024 * 1024  # 10MB
    log_retention_days: int = 90
    summary_retention_days: int = 365
    dashboard_port: int = 5000
    dashboard_host: str = "localhost"
    update_interval: int = 5  # seconds
    performance_threshold_multiplier: float = 1.5
    error_rate_threshold: float = 0.1  # 10%
    error_rate_window: int = 10  # minutes
    alerts: List[AlertConfiguration] = None
    
    def __post_init__(self):
        if self.alerts is None:
            self.alerts = [
                AlertConfiguration(
                    name="fetch_failure",
                    condition="event_type == 'fetch_failed'",
                    threshold=1.0,
                    time_window=2,
                    notification_channels=["file", "console"]
                ),
                AlertConfiguration(
                    name="performance_degradation",
                    condition="execution_time > baseline * 1.5",
                    threshold=1.5,
                    time_window=10,
                    notification_channels=["file", "console"]
                ),
                AlertConfiguration(
                    name="high_error_rate",
                    condition="error_rate > 0.1",
                    threshold=0.1,
                    time_window=10,
                    notification_channels=["file", "console"]
                )
            ]


class ConfigManager:
    """Manages configuration loading, validation, and hot-reloading."""
    
    def __init__(self, config_path: str = "monitoring_config.json"):
        self.config_path = Path(config_path)
        self.config = MonitoringConfig()
        self.callbacks = []
        
    def load_config(self) -> MonitoringConfig:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            # Create default config file
            self.save_config()
            return self.config
            
        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            
            # Validate and create config object
            self.config = self._validate_config(config_data)
            return self.config
            
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"Error loading config: {e}. Using default configuration.")
            return self.config
    
    def save_config(self) -> None:
        """Save current configuration to JSON file."""
        config_dict = asdict(self.config)
        # Convert AlertConfiguration objects to dicts
        config_dict['alerts'] = [asdict(alert) for alert in self.config.alerts]
        
        with open(self.config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def _validate_config(self, config_data: Dict[str, Any]) -> MonitoringConfig:
        """Validate configuration data and create MonitoringConfig object."""
        # Extract alerts if present
        alerts = []
        if 'alerts' in config_data:
            for alert_data in config_data['alerts']:
                alerts.append(AlertConfiguration(**alert_data))
            config_data['alerts'] = alerts
        
        # Validate required fields and types
        valid_fields = {
            'log_level': str,
            'database_path': str,
            'log_file_path': str,
            'max_log_file_size': int,
            'log_retention_days': int,
            'summary_retention_days': int,
            'dashboard_port': int,
            'dashboard_host': str,
            'update_interval': int,
            'performance_threshold_multiplier': float,
            'error_rate_threshold': float,
            'error_rate_window': int
        }
        
        for field, expected_type in valid_fields.items():
            if field in config_data:
                if not isinstance(config_data[field], expected_type):
                    raise ValueError(f"Invalid type for {field}: expected {expected_type.__name__}")
        
        # Create config object with validated data
        return MonitoringConfig(**{k: v for k, v in config_data.items() 
                                 if k in MonitoringConfig.__dataclass_fields__})
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values and notify callbacks."""
        # Validate updates
        validated_updates = self._validate_config(updates)
        
        # Update config
        for key, value in asdict(validated_updates).items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Save updated config
        self.save_config()
        
        # Notify callbacks
        for callback in self.callbacks:
            callback(self.config)
    
    def register_callback(self, callback):
        """Register callback for configuration changes."""
        self.callbacks.append(callback)
    
    def get_config(self) -> MonitoringConfig:
        """Get current configuration."""
        return self.config


# Global config manager instance
config_manager = ConfigManager()