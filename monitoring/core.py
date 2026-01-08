"""Core monitoring system initialization and management."""
import logging
import atexit
from .config import config_manager
from .database import db_manager
from .event_bus import event_bus
from .logging_setup import setup_logging


class MonitoringSystem:
    """Main monitoring system coordinator."""
    
    def __init__(self):
        self.logger = None
        self.initialized = False
    
    def initialize(self):
        """Initialize the monitoring system."""
        if self.initialized:
            return
        
        try:
            # Load configuration
            config_manager.load_config()
            
            # Setup logging
            self.logger = setup_logging()
            self.logger.info("Monitoring system initializing...")
            
            # Initialize database
            db_manager._init_database()
            
            # Register cleanup on exit
            atexit.register(self.shutdown)
            
            self.initialized = True
            self.logger.info("Monitoring system initialized successfully")
            
            # Publish system startup event
            event_bus.publish('system.startup', {
                'timestamp': str(db_manager._get_current_timestamp()),
                'config': config_manager.get_config().__dict__
            })
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize monitoring system: {e}")
            else:
                print(f"Failed to initialize monitoring system: {e}")
            raise
    
    def shutdown(self):
        """Shutdown the monitoring system gracefully."""
        if not self.initialized:
            return
        
        try:
            if self.logger:
                self.logger.info("Monitoring system shutting down...")
            
            # Publish shutdown event
            event_bus.publish('system.shutdown', {
                'timestamp': str(db_manager._get_current_timestamp())
            })
            
            # Cleanup old data
            db_manager.cleanup_old_data()
            
            # Clear event bus subscribers
            event_bus.clear_subscribers()
            
            self.initialized = False
            
            if self.logger:
                self.logger.info("Monitoring system shutdown complete")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during monitoring system shutdown: {e}")
    
    def is_initialized(self) -> bool:
        """Check if monitoring system is initialized."""
        return self.initialized
    
    def get_status(self) -> dict:
        """Get monitoring system status."""
        if not self.initialized:
            return {'status': 'not_initialized'}
        
        try:
            db_stats = db_manager.get_database_stats()
            config = config_manager.get_config()
            
            return {
                'status': 'running',
                'database_stats': db_stats,
                'config': {
                    'log_level': config.log_level,
                    'database_path': config.database_path,
                    'dashboard_port': config.dashboard_port,
                    'update_interval': config.update_interval
                },
                'event_bus_subscribers': {
                    event_type: event_bus.get_subscriber_count(event_type)
                    for event_type in ['function.started', 'function.completed', 
                                     'function.failed', 'progress.updated']
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }


# Global monitoring system instance
monitoring_system = MonitoringSystem()


def ensure_initialized():
    """Ensure monitoring system is initialized."""
    if not monitoring_system.is_initialized():
        monitoring_system.initialize()


# Add method to database manager for timestamp consistency
def _get_current_timestamp():
    """Get current timestamp for consistency."""
    from datetime import datetime
    return datetime.now()

db_manager._get_current_timestamp = _get_current_timestamp