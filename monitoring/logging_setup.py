"""Logging setup and configuration for the monitoring system."""
import logging
import logging.handlers
from pathlib import Path
from .config import config_manager


def setup_logging():
    """Set up logging configuration for the monitoring system."""
    config = config_manager.get_config()
    
    # Create logs directory if it doesn't exist
    log_path = Path(config.log_file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        config.log_file_path,
        maxBytes=config.max_log_file_size,
        backupCount=5
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger('monitoring').setLevel(getattr(logging, config.log_level.upper()))
    
    return logger


def update_log_level(new_level: str):
    """Update logging level dynamically."""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, new_level.upper(), logging.INFO))
    
    # Update monitoring loggers
    monitoring_logger = logging.getLogger('monitoring')
    monitoring_logger.setLevel(getattr(logging, new_level.upper()))
    
    logging.info(f"Log level updated to {new_level}")


# Register callback for configuration changes
def _on_config_change(config):
    """Handle configuration changes."""
    update_log_level(config.log_level)


config_manager.register_callback(_on_config_change)