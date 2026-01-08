"""Data models for the monitoring system."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
import json


@dataclass
class LogEntry:
    timestamp: datetime
    session_id: str
    function_name: str
    event_type: str  # 'start', 'complete', 'error'
    duration: Optional[float] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    result_summary: Optional[str] = None
    error_details: Optional[str] = None
    memory_usage: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'session_id': self.session_id,
            'function_name': self.function_name,
            'event_type': self.event_type,
            'duration': self.duration,
            'parameters': json.dumps(self.parameters) if self.parameters else None,
            'result_summary': self.result_summary,
            'error_details': self.error_details,
            'memory_usage': self.memory_usage,
            'metadata': json.dumps(self.metadata) if self.metadata else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        """Create LogEntry from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            session_id=data['session_id'],
            function_name=data['function_name'],
            event_type=data['event_type'],
            duration=data.get('duration'),
            parameters=json.loads(data['parameters']) if data.get('parameters') else {},
            result_summary=data.get('result_summary'),
            error_details=data.get('error_details'),
            memory_usage=data.get('memory_usage'),
            metadata=json.loads(data['metadata']) if data.get('metadata') else {}
        )


@dataclass
class PerformanceMetrics:
    timestamp: datetime
    function_name: str
    execution_time: float
    memory_peak: int
    cpu_usage: float = 0.0
    api_calls_count: int = 0
    db_queries_count: int = 0
    success_rate: float = 1.0
    session_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'function_name': self.function_name,
            'execution_time': self.execution_time,
            'memory_peak': self.memory_peak,
            'cpu_usage': self.cpu_usage,
            'api_calls_count': self.api_calls_count,
            'db_queries_count': self.db_queries_count,
            'success_rate': self.success_rate,
            'session_id': self.session_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceMetrics':
        """Create PerformanceMetrics from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            function_name=data['function_name'],
            execution_time=data['execution_time'],
            memory_peak=data['memory_peak'],
            cpu_usage=data.get('cpu_usage', 0.0),
            api_calls_count=data.get('api_calls_count', 0),
            db_queries_count=data.get('db_queries_count', 0),
            success_rate=data.get('success_rate', 1.0),
            session_id=data.get('session_id', '')
        )


@dataclass
class ProgressState:
    session_id: str
    current_step: str
    progress_percentage: float
    estimated_completion: Optional[datetime]
    steps_completed: int
    total_steps: int
    start_time: datetime
    errors_encountered: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'session_id': self.session_id,
            'current_step': self.current_step,
            'progress_percentage': self.progress_percentage,
            'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None,
            'steps_completed': self.steps_completed,
            'total_steps': self.total_steps,
            'start_time': self.start_time.isoformat(),
            'errors_encountered': self.errors_encountered
        }


@dataclass
class TimeRange:
    start: datetime
    end: datetime
    
    def contains(self, timestamp: datetime) -> bool:
        """Check if timestamp falls within this range."""
        return self.start <= timestamp <= self.end


@dataclass
class LogFilters:
    session_id: Optional[str] = None
    function_name: Optional[str] = None
    event_type: Optional[str] = None
    time_range: Optional[TimeRange] = None
    limit: Optional[int] = None


@dataclass
class PerformanceSummary:
    time_range: TimeRange
    total_executions: int
    average_execution_time: float
    total_memory_usage: int
    error_count: int
    success_rate: float
    top_functions: List[Dict[str, Any]] = field(default_factory=list)