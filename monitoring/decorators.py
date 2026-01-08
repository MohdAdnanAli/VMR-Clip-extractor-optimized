"""Function decorators for monitoring execution and performance."""
import functools
import time
import traceback
import psutil
import os
from datetime import datetime
from typing import Any, Dict, Optional
import uuid
import logging

from .core import ensure_initialized
from .event_bus import event_bus
from .database import db_manager
from .models import LogEntry, PerformanceMetrics


def monitor_execution(func):
    """Decorator to monitor function execution, parameters, and outcomes."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ensure_initialized()
        
        # Generate session ID for this execution
        session_id = str(uuid.uuid4())[:8]
        func_name = f"{func.__module__}.{func.__name__}"
        start_time = datetime.now()
        
        # Log function start
        start_entry = LogEntry(
            timestamp=start_time,
            session_id=session_id,
            function_name=func_name,
            event_type='start',
            parameters={
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys()),
                'args_summary': str(args)[:200] + '...' if len(str(args)) > 200 else str(args)
            }
        )
        
        try:
            db_manager.insert_log_entry(start_entry)
            event_bus.publish('function.started', {
                'function_name': func_name,
                'session_id': session_id,
                'timestamp': start_time.isoformat()
            })
        except Exception as e:
            logging.error(f"Error logging function start: {e}")
        
        try:
            # Execute the function
            result = func(*args, **kwargs)
            
            # Log successful completion
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            complete_entry = LogEntry(
                timestamp=end_time,
                session_id=session_id,
                function_name=func_name,
                event_type='complete',
                duration=duration,
                result_summary=str(result)[:200] + '...' if len(str(result)) > 200 else str(result)
            )
            
            try:
                db_manager.insert_log_entry(complete_entry)
                event_bus.publish('function.completed', {
                    'function_name': func_name,
                    'session_id': session_id,
                    'duration': duration,
                    'timestamp': end_time.isoformat()
                })
            except Exception as e:
                logging.error(f"Error logging function completion: {e}")
            
            return result
            
        except Exception as error:
            # Log error
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            error_entry = LogEntry(
                timestamp=end_time,
                session_id=session_id,
                function_name=func_name,
                event_type='error',
                duration=duration,
                error_details=str(error),
                parameters={
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys()),
                    'traceback': traceback.format_exc()
                }
            )
            
            try:
                db_manager.insert_log_entry(error_entry)
                event_bus.publish('function.failed', {
                    'function_name': func_name,
                    'session_id': session_id,
                    'error': str(error),
                    'duration': duration,
                    'timestamp': end_time.isoformat()
                })
            except Exception as e:
                logging.error(f"Error logging function error: {e}")
            
            raise  # Re-raise the original error
    
    return wrapper


def track_performance(func):
    """Decorator to track performance metrics like execution time and memory usage."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ensure_initialized()
        
        func_name = f"{func.__module__}.{func.__name__}"
        start_time = datetime.now()
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        try:
            # Execute function
            result = func(*args, **kwargs)
            
            # Calculate metrics
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            final_memory = process.memory_info().rss
            memory_peak = max(initial_memory, final_memory)
            
            # Create performance metrics
            metrics = PerformanceMetrics(
                timestamp=end_time,
                function_name=func_name,
                execution_time=execution_time,
                memory_peak=memory_peak,
                cpu_usage=process.cpu_percent(),
                success_rate=1.0
            )
            
            try:
                db_manager.insert_performance_metrics(metrics)
                event_bus.publish('performance.recorded', {
                    'function_name': func_name,
                    'execution_time': execution_time,
                    'memory_peak': memory_peak,
                    'timestamp': end_time.isoformat()
                })
            except Exception as e:
                logging.error(f"Error recording performance metrics: {e}")
            
            return result
            
        except Exception as error:
            # Record failed execution
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            final_memory = process.memory_info().rss
            memory_peak = max(initial_memory, final_memory)
            
            metrics = PerformanceMetrics(
                timestamp=end_time,
                function_name=func_name,
                execution_time=execution_time,
                memory_peak=memory_peak,
                cpu_usage=process.cpu_percent(),
                success_rate=0.0
            )
            
            try:
                db_manager.insert_performance_metrics(metrics)
            except Exception as e:
                logging.error(f"Error recording failed performance metrics: {e}")
            
            raise  # Re-raise the original error
    
    return wrapper


def progress_step(weight: float = 1.0):
    """Decorator to mark functions as progress steps with relative weights."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ensure_initialized()
            
            func_name = f"{func.__module__}.{func.__name__}"
            
            # Publish progress step start
            event_bus.publish('progress.step_started', {
                'function_name': func_name,
                'weight': weight,
                'timestamp': datetime.now().isoformat()
            })
            
            try:
                result = func(*args, **kwargs)
                
                # Publish progress step completion
                event_bus.publish('progress.step_completed', {
                    'function_name': func_name,
                    'weight': weight,
                    'timestamp': datetime.now().isoformat()
                })
                
                return result
                
            except Exception as error:
                # Publish progress step failure
                event_bus.publish('progress.step_failed', {
                    'function_name': func_name,
                    'weight': weight,
                    'error': str(error),
                    'timestamp': datetime.now().isoformat()
                })
                raise
        
        return wrapper
    return decorator


# Convenience decorator that combines monitoring and performance tracking
def monitor_all(weight: float = 1.0):
    """Decorator that combines execution monitoring, performance tracking, and progress tracking."""
    def decorator(func):
        # Apply all decorators
        decorated_func = monitor_execution(func)
        decorated_func = track_performance(decorated_func)
        decorated_func = progress_step(weight)(decorated_func)
        return decorated_func
    return decorator