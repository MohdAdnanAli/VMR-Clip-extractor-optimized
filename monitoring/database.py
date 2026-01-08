"""Database operations for the monitoring system."""
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

from .models import LogEntry, PerformanceMetrics, LogFilters, TimeRange
from .config import config_manager


class DatabaseManager:
    """Manages SQLite database operations for monitoring data."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config_manager.get_config().database_path
        self._lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database tables."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                # Create log entries table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS log_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        function_name TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        duration REAL,
                        parameters TEXT,
                        result_summary TEXT,
                        error_details TEXT,
                        memory_usage INTEGER,
                        metadata TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create performance metrics table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        function_name TEXT NOT NULL,
                        execution_time REAL NOT NULL,
                        memory_peak INTEGER NOT NULL,
                        cpu_usage REAL DEFAULT 0.0,
                        api_calls_count INTEGER DEFAULT 0,
                        db_queries_count INTEGER DEFAULT 0,
                        success_rate REAL DEFAULT 1.0,
                        session_id TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better query performance
                conn.execute('CREATE INDEX IF NOT EXISTS idx_log_timestamp ON log_entries(timestamp)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_log_session ON log_entries(session_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_log_function ON log_entries(function_name)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_perf_timestamp ON performance_metrics(timestamp)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_perf_function ON performance_metrics(function_name)')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
            except Exception as e:
                self.logger.error(f"Error initializing database: {e}")
                conn.rollback()
                raise
            finally:
                conn.close()
    
    def insert_log_entry(self, entry: LogEntry) -> None:
        """Insert a log entry into the database."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                data = entry.to_dict()
                conn.execute('''
                    INSERT INTO log_entries 
                    (timestamp, session_id, function_name, event_type, duration, 
                     parameters, result_summary, error_details, memory_usage, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['timestamp'], data['session_id'], data['function_name'],
                    data['event_type'], data['duration'], data['parameters'],
                    data['result_summary'], data['error_details'], 
                    data['memory_usage'], data['metadata']
                ))
                conn.commit()
                
            except Exception as e:
                self.logger.error(f"Error inserting log entry: {e}")
                conn.rollback()
                raise
            finally:
                conn.close()
    
    def insert_performance_metrics(self, metrics: PerformanceMetrics) -> None:
        """Insert performance metrics into the database."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                data = metrics.to_dict()
                conn.execute('''
                    INSERT INTO performance_metrics 
                    (timestamp, function_name, execution_time, memory_peak, 
                     cpu_usage, api_calls_count, db_queries_count, success_rate, session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['timestamp'], data['function_name'], data['execution_time'],
                    data['memory_peak'], data['cpu_usage'], data['api_calls_count'],
                    data['db_queries_count'], data['success_rate'], data['session_id']
                ))
                conn.commit()
                
            except Exception as e:
                self.logger.error(f"Error inserting performance metrics: {e}")
                conn.rollback()
                raise
            finally:
                conn.close()
    
    def query_log_entries(self, filters: LogFilters) -> List[LogEntry]:
        """Query log entries with optional filters."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            try:
                query = "SELECT * FROM log_entries WHERE 1=1"
                params = []
                
                if filters.session_id:
                    query += " AND session_id = ?"
                    params.append(filters.session_id)
                
                if filters.function_name:
                    query += " AND function_name = ?"
                    params.append(filters.function_name)
                
                if filters.event_type:
                    query += " AND event_type = ?"
                    params.append(filters.event_type)
                
                if filters.time_range:
                    query += " AND timestamp BETWEEN ? AND ?"
                    params.extend([
                        filters.time_range.start.isoformat(),
                        filters.time_range.end.isoformat()
                    ])
                
                query += " ORDER BY timestamp DESC"
                
                if filters.limit:
                    query += " LIMIT ?"
                    params.append(filters.limit)
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                return [LogEntry.from_dict(dict(row)) for row in rows]
                
            except Exception as e:
                self.logger.error(f"Error querying log entries: {e}")
                raise
            finally:
                conn.close()
    
    def query_performance_metrics(self, time_range: TimeRange = None, 
                                function_name: str = None) -> List[PerformanceMetrics]:
        """Query performance metrics with optional filters."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            try:
                query = "SELECT * FROM performance_metrics WHERE 1=1"
                params = []
                
                if time_range:
                    query += " AND timestamp BETWEEN ? AND ?"
                    params.extend([
                        time_range.start.isoformat(),
                        time_range.end.isoformat()
                    ])
                
                if function_name:
                    query += " AND function_name = ?"
                    params.append(function_name)
                
                query += " ORDER BY timestamp DESC"
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                return [PerformanceMetrics.from_dict(dict(row)) for row in rows]
                
            except Exception as e:
                self.logger.error(f"Error querying performance metrics: {e}")
                raise
            finally:
                conn.close()
    
    def cleanup_old_data(self) -> None:
        """Clean up old data based on retention policies."""
        config = config_manager.get_config()
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                # Calculate cutoff dates
                log_cutoff = datetime.now() - timedelta(days=config.log_retention_days)
                summary_cutoff = datetime.now() - timedelta(days=config.summary_retention_days)
                
                # Delete old log entries
                conn.execute(
                    "DELETE FROM log_entries WHERE timestamp < ?",
                    (log_cutoff.isoformat(),)
                )
                
                # Delete old performance metrics (keep summary data longer)
                conn.execute(
                    "DELETE FROM performance_metrics WHERE timestamp < ?",
                    (summary_cutoff.isoformat(),)
                )
                
                conn.commit()
                self.logger.info("Old data cleanup completed")
                
            except Exception as e:
                self.logger.error(f"Error during data cleanup: {e}")
                conn.rollback()
                raise
            finally:
                conn.close()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM log_entries")
                log_count = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM performance_metrics")
                metrics_count = cursor.fetchone()[0]
                
                # Get database file size
                db_size = Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
                
                return {
                    'log_entries_count': log_count,
                    'performance_metrics_count': metrics_count,
                    'database_size_bytes': db_size,
                    'database_path': self.db_path
                }
                
            except Exception as e:
                self.logger.error(f"Error getting database stats: {e}")
                return {}
            finally:
                conn.close()


# Global database manager instance
db_manager = DatabaseManager()