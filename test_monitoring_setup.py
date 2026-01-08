"""Test script to verify monitoring system setup."""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monitoring.core import monitoring_system, ensure_initialized
from monitoring.event_bus import event_bus
from monitoring.database import db_manager
from monitoring.config import config_manager


def test_basic_setup():
    """Test basic monitoring system setup."""
    print("Testing monitoring system setup...")
    
    # Test initialization
    ensure_initialized()
    assert monitoring_system.is_initialized(), "Monitoring system should be initialized"
    print("✓ Monitoring system initialized")
    
    # Test configuration
    config = config_manager.get_config()
    assert config.log_level == "INFO", "Default log level should be INFO"
    print("✓ Configuration loaded")
    
    # Test event bus
    events_received = []
    
    def test_handler(event_type, data):
        events_received.append((event_type, data))
    
    event_bus.subscribe('test.event', test_handler)
    event_bus.publish('test.event', {'message': 'test'})
    
    assert len(events_received) == 1, "Should receive one event"
    assert events_received[0][0] == 'test.event', "Event type should match"
    print("✓ Event bus working")
    
    # Test database
    stats = db_manager.get_database_stats()
    assert 'log_entries_count' in stats, "Database stats should include log entries count"
    print("✓ Database operational")
    
    # Test system status
    status = monitoring_system.get_status()
    assert status['status'] == 'running', "System should be running"
    print("✓ System status check passed")
    
    print("\nAll basic setup tests passed! ✅")
    return True


if __name__ == "__main__":
    try:
        test_basic_setup()
        print("\nMonitoring system core infrastructure is ready!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)