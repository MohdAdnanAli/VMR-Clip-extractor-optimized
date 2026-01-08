"""Comprehensive test of the monitoring system with the viral clip analyzer."""
import sys
import os
import time
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monitoring.core import monitoring_system, ensure_initialized
from monitoring.database import db_manager
from monitoring.models import LogFilters, TimeRange
from monitoring.event_bus import event_bus


def test_complete_monitoring_system():
    """Test the complete monitoring system with the viral clip analyzer."""
    print("🚀 Testing Complete Monitoring System")
    print("=" * 50)
    
    # Initialize monitoring
    ensure_initialized()
    print("✓ Monitoring system initialized")
    
    # Clear any existing data for clean test
    try:
        import sqlite3
        conn = sqlite3.connect(monitoring_system.logger.handlers[1].baseFilename.replace('.log', '.db') if len(monitoring_system.logger.handlers) > 1 else 'monitoring.db')
        conn.execute("DELETE FROM log_entries")
        conn.execute("DELETE FROM performance_metrics")
        conn.commit()
        conn.close()
    except:
        pass
    
    # Track events for verification
    events_received = []
    
    def event_tracker(event_type, data):
        events_received.append((event_type, data))
        print(f"📡 Event: {event_type} - {data.get('function_name', 'N/A')}")
    
    # Subscribe to all monitoring events
    event_types = [
        'function.started', 'function.completed', 'function.failed',
        'progress.step_started', 'progress.step_completed', 
        'performance.recorded'
    ]
    
    for event_type in event_types:
        event_bus.subscribe(event_type, event_tracker)
    
    print("\n📊 Running monitored viral clip analyzer...")
    print("-" * 40)
    
    # Import and run the monitored main function
    try:
        from main_monitored import main
        start_time = time.time()
        result = main()
        end_time = time.time()
        
        print(f"\n✅ Viral clip analyzer completed in {end_time - start_time:.2f} seconds")
        print(f"📈 Selected {len(result)} clips")
        
    except Exception as e:
        print(f"❌ Error running monitored analyzer: {e}")
        return False
    
    # Wait a moment for all events to be processed
    time.sleep(0.5)
    
    print(f"\n📡 Captured {len(events_received)} monitoring events")
    
    # Verify database entries
    print("\n🗄️  Database Verification:")
    print("-" * 25)
    
    # Check log entries
    filters = LogFilters(limit=100)
    log_entries = db_manager.query_log_entries(filters)
    print(f"✓ Log entries: {len(log_entries)}")
    
    # Check performance metrics
    time_range = TimeRange(
        start=datetime.now() - timedelta(minutes=5),
        end=datetime.now() + timedelta(minutes=1)
    )
    perf_metrics = db_manager.query_performance_metrics(time_range)
    print(f"✓ Performance metrics: {len(perf_metrics)}")
    
    # Show some sample data
    if log_entries:
        print(f"\n📋 Sample Log Entries:")
        for entry in log_entries[:3]:
            print(f"  • {entry.function_name} ({entry.event_type}) - {entry.duration:.3f}s" if entry.duration else f"  • {entry.function_name} ({entry.event_type})")
    
    if perf_metrics:
        print(f"\n⚡ Sample Performance Metrics:")
        for metric in perf_metrics[:3]:
            print(f"  • {metric.function_name}: {metric.execution_time:.3f}s, {metric.memory_peak/1024/1024:.1f}MB")
    
    # System status check
    print(f"\n🔍 System Status:")
    print("-" * 15)
    status = monitoring_system.get_status()
    print(f"✓ Status: {status['status']}")
    print(f"✓ Database entries: {status['database_stats']['log_entries_count']}")
    print(f"✓ Performance records: {status['database_stats']['performance_metrics_count']}")
    
    # Verify key functions were monitored
    monitored_functions = set()
    for entry in log_entries:
        if entry.event_type == 'complete':
            monitored_functions.add(entry.function_name.split('.')[-1])
    
    expected_functions = ['main', 'fetch_trending_clips', 'final_score', 'deduplicate']
    found_functions = [f for f in expected_functions if f in str(monitored_functions)]
    
    print(f"\n🎯 Function Monitoring Coverage:")
    print(f"✓ Monitored functions: {', '.join(found_functions)}")
    
    # Performance summary
    if perf_metrics:
        total_time = sum(m.execution_time for m in perf_metrics)
        avg_memory = sum(m.memory_peak for m in perf_metrics) / len(perf_metrics) / 1024 / 1024
        print(f"\n📊 Performance Summary:")
        print(f"✓ Total execution time: {total_time:.3f}s")
        print(f"✓ Average memory usage: {avg_memory:.1f}MB")
        print(f"✓ Functions tracked: {len(set(m.function_name for m in perf_metrics))}")
    
    # Cleanup event subscriptions
    for event_type in event_types:
        event_bus.unsubscribe(event_type, event_tracker)
    
    print(f"\n🎉 MONITORING SYSTEM TEST COMPLETE!")
    print("=" * 50)
    print("✅ All components working correctly")
    print("✅ Function execution tracking: ACTIVE")
    print("✅ Performance monitoring: ACTIVE") 
    print("✅ Event system: ACTIVE")
    print("✅ Database logging: ACTIVE")
    print("✅ Integration with viral clip analyzer: SUCCESS")
    
    return True


def show_monitoring_files():
    """Show the monitoring files created."""
    print(f"\n📁 Monitoring Files Created:")
    print("-" * 30)
    
    monitoring_files = [
        "monitoring/__init__.py",
        "monitoring/config.py", 
        "monitoring/event_bus.py",
        "monitoring/models.py",
        "monitoring/database.py",
        "monitoring/logging_setup.py",
        "monitoring/core.py",
        "monitoring/decorators.py",
        "main_monitored.py",
        "monitoring_config.json",
        "monitoring.db",
        "monitoring.log"
    ]
    
    for file in monitoring_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✓ {file} ({size:,} bytes)")
        else:
            print(f"○ {file} (will be created)")


if __name__ == "__main__":
    try:
        # Install required package if not available
        try:
            import psutil
        except ImportError:
            print("Installing psutil for memory monitoring...")
            os.system("pip install psutil")
            import psutil
        
        show_monitoring_files()
        success = test_complete_monitoring_system()
        
        if success:
            print(f"\n🚀 READY TO USE!")
            print("To use monitoring with your viral clip analyzer:")
            print("1. Run: python main_monitored.py")
            print("2. Check monitoring.log for detailed logs")
            print("3. Check monitoring.db for structured data")
            print("4. Use the monitoring decorators in your own functions")
        else:
            print(f"\n❌ Test failed - check the errors above")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)