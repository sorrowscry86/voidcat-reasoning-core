#!/usr/bin/env python3
"""
VoidCat Comprehensive Logging System - Pillar IV Infrastructure Component

This module implements a robust, multi-level logging system for the VoidCat enhanced MCP server
providing comprehensive monitoring, diagnostics, performance tracking, and operational insights.

Features:
- Structured logging with JSON output for machine processing
- Multiple log levels with component-specific filtering
- Performance metrics tracking and aggregation
- Error tracking with contextual information
- Real-time log streaming and monitoring
- Log rotation and archival management
- Integration with all VoidCat components
- Security-focused log sanitization

Author: VoidCat Reasoning Core Team - Pillar IV Infrastructure
License: MIT
Version: 1.0.0
"""

import inspect
import json
import logging
import logging.handlers
import os
import sys
import threading
import time
import traceback
import uuid
from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union


# Logging levels and categories
class LogLevel(Enum):
    """Enhanced logging levels for VoidCat system."""

    TRACE = 5  # Detailed execution tracing
    DEBUG = 10  # Debug information
    INFO = 20  # General information
    WARNING = 30  # Warning conditions
    ERROR = 40  # Error conditions
    CRITICAL = 50  # Critical errors
    AUDIT = 60  # Security and audit events


class LogCategory(Enum):
    """Log categories for component-specific filtering."""

    SYSTEM = "system"
    MCP_SERVER = "mcp_server"
    RATE_LIMITER = "rate_limiter"
    TASK_MANAGER = "task_manager"
    MEMORY_SYSTEM = "memory_system"
    CODE_ANALYZER = "code_analyzer"
    FILE_OPERATIONS = "file_operations"
    REASONING_ENGINE = "reasoning_engine"
    SECURITY = "security"
    PERFORMANCE = "performance"
    AUDIT = "audit"


@dataclass
class LogEntry:
    """Structured log entry with comprehensive metadata."""

    timestamp: str
    level: str
    category: str
    component: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    log_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary for JSON serialization."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert log entry to JSON string."""
        return json.dumps(self.to_dict(), default=str)


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking for operations."""

    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    additional_metrics: Dict[str, Any] = field(default_factory=dict)

    def complete(self) -> None:
        """Mark the operation as completed and calculate duration."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time


class VoidCatLogger:
    """
    Comprehensive logging system for VoidCat with structured output,
    performance tracking, and multi-component support.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the VoidCat logging system.

        Args:
            config: Logging configuration dictionary
        """
        self.config = config or {}
        self.log_dir = Path(self.config.get("log_directory", "logs"))
        self.log_dir.mkdir(exist_ok=True)

        # Initialize logging components
        self._setup_loggers()
        self._setup_handlers()
        self._setup_formatters()

        # Performance tracking
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}
        self.metrics_history: deque = deque(maxlen=10000)

        # Real-time monitoring
        self.log_stream: deque = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.component_activity = defaultdict(int)

        # Threading for async operations
        self._log_queue: deque = deque()
        self._queue_lock = threading.Lock()
        self._background_thread = threading.Thread(
            target=self._background_processor, daemon=True
        )
        self._background_thread.start()

        # Security and sanitization
        self.sensitive_patterns = [
            r"api[_-]?key",
            r"password",
            r"token",
            r"secret",
            r"auth",
            r"credential",
        ]

        self.info(
            "VoidCat comprehensive logging system initialized",
            category=LogCategory.SYSTEM,
            details={"log_directory": str(self.log_dir)},
        )

    def _setup_loggers(self) -> None:
        """Set up Python loggers for different components."""
        self.loggers = {}

        # Main VoidCat logger
        self.main_logger = logging.getLogger("VoidCat")
        self.main_logger.setLevel(logging.DEBUG)

        # Component-specific loggers
        for category in LogCategory:
            logger = logging.getLogger(f"VoidCat.{category.value}")
            logger.setLevel(logging.DEBUG)
            self.loggers[category] = logger

    def _setup_handlers(self) -> None:
        """Set up log handlers for different output destinations."""
        self.handlers = {}

        # Console handler for immediate feedback
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        self.handlers["console"] = console_handler

        # File handler for general logs
        general_log_file = self.log_dir / "voidcat.log"
        file_handler = logging.handlers.RotatingFileHandler(
            general_log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
        )
        file_handler.setLevel(logging.DEBUG)
        self.handlers["file"] = file_handler

        # Error-specific handler
        error_log_file = self.log_dir / "voidcat_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file, maxBytes=5 * 1024 * 1024, backupCount=3  # 5MB
        )
        error_handler.setLevel(logging.ERROR)
        self.handlers["error"] = error_handler

        # JSON structured log handler
        json_log_file = self.log_dir / "voidcat_structured.json"
        json_handler = logging.handlers.RotatingFileHandler(
            json_log_file, maxBytes=20 * 1024 * 1024, backupCount=10  # 20MB
        )
        json_handler.setLevel(logging.DEBUG)
        self.handlers["json"] = json_handler

        # Performance metrics handler
        perf_log_file = self.log_dir / "voidcat_performance.log"
        perf_handler = logging.handlers.RotatingFileHandler(
            perf_log_file, maxBytes=5 * 1024 * 1024, backupCount=5  # 5MB
        )
        self.handlers["performance"] = perf_handler

        # Audit log handler (for security events)
        audit_log_file = self.log_dir / "voidcat_audit.log"
        audit_handler = logging.handlers.RotatingFileHandler(
            audit_log_file, maxBytes=10 * 1024 * 1024, backupCount=10  # 10MB
        )
        audit_handler.setLevel(logging.INFO)
        self.handlers["audit"] = audit_handler

    def _setup_formatters(self) -> None:
        """Set up log formatters for different output formats."""
        # Standard text formatter
        text_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # JSON formatter for structured logging
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }

                # Add exception info if present
                if record.exc_info:
                    log_entry["exception"] = self.formatException(record.exc_info)

                return json.dumps(log_entry)

        json_formatter = JSONFormatter()

        # Apply formatters to handlers
        self.handlers["console"].setFormatter(text_formatter)
        self.handlers["file"].setFormatter(text_formatter)
        self.handlers["error"].setFormatter(text_formatter)
        self.handlers["json"].setFormatter(json_formatter)
        self.handlers["performance"].setFormatter(text_formatter)
        self.handlers["audit"].setFormatter(text_formatter)

        # Add handlers to loggers
        for handler in self.handlers.values():
            self.main_logger.addHandler(handler)

    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize sensitive information from log data."""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                key_lower = str(key).lower()
                if any(pattern in key_lower for pattern in self.sensitive_patterns):
                    sanitized[key] = "***REDACTED***"
                else:
                    sanitized[key] = self._sanitize_data(value)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        elif isinstance(data, str) and len(data) > 20:
            # Check if string looks like a token or key
            if any(pattern in data.lower() for pattern in self.sensitive_patterns):
                return "***REDACTED***"

        return data

    def _background_processor(self) -> None:
        """Background thread for processing log queue and maintenance tasks."""
        while True:
            try:
                # Process log queue
                if self._log_queue:
                    with self._queue_lock:
                        if self._log_queue:
                            log_entry = self._log_queue.popleft()
                            self._process_log_entry(log_entry)

                # Perform maintenance tasks
                self._maintenance_tasks()

                time.sleep(0.1)  # Small delay to prevent excessive CPU usage

            except Exception as e:
                # Fallback logging for logger errors
                print(
                    f"[VoidCat Logger Error] Background processor failed: {e}",
                    file=sys.stderr,
                )

    def _process_log_entry(self, log_entry: LogEntry) -> None:
        """Process a log entry through all handlers."""
        try:
            # Add to real-time stream
            self.log_stream.append(log_entry)

            # Update statistics
            self.component_activity[log_entry.component] += 1
            if log_entry.level in ["ERROR", "CRITICAL"]:
                self.error_counts[log_entry.component] += 1

            # Write structured log
            json_record = logging.LogRecord(
                name=f"VoidCat.{log_entry.category}",
                level=getattr(logging, log_entry.level, logging.INFO),
                pathname="",
                lineno=0,
                msg=log_entry.to_json(),
                args=(),
                exc_info=None,
            )

            self.handlers["json"].emit(json_record)

        except Exception as e:
            print(
                f"[VoidCat Logger Error] Failed to process log entry: {e}",
                file=sys.stderr,
            )

    def _maintenance_tasks(self) -> None:
        """Perform periodic maintenance tasks."""
        # Clean old performance metrics
        current_time = time.time()
        expired_metrics = [
            key
            for key, metrics in self.performance_metrics.items()
            if metrics.end_time and (current_time - metrics.end_time) > 3600  # 1 hour
        ]

        for key in expired_metrics:
            del self.performance_metrics[key]

    def log(
        self,
        level: Union[LogLevel, str],
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        component: str = "unknown",
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        performance_metrics: Optional[Dict[str, float]] = None,
        stack_trace: Optional[str] = None,
    ) -> None:
        """
        Log a message with comprehensive metadata.

        Args:
            level: Log level (LogLevel enum or string)
            message: Log message
            category: Log category for filtering
            component: Component generating the log
            details: Additional details dictionary
            correlation_id: Correlation ID for tracking related events
            request_id: Request ID for MCP request tracking
            user_id: User ID if applicable
            session_id: Session ID for user sessions
            performance_metrics: Performance metrics dictionary
            stack_trace: Stack trace for errors
        """
        try:
            # Convert level to string
            level_str = (
                level.name if isinstance(level, LogLevel) else str(level).upper()
            )

            # Sanitize details
            sanitized_details = self._sanitize_data(details or {})

            # Create log entry
            log_entry = LogEntry(
                timestamp=datetime.now(UTC).isoformat(),
                level=level_str,
                category=(
                    category.value
                    if isinstance(category, LogCategory)
                    else str(category)
                ),
                component=component,
                message=message,
                details=sanitized_details,
                correlation_id=correlation_id,
                request_id=request_id,
                user_id=user_id,
                session_id=session_id,
                performance_metrics=performance_metrics or {},
                stack_trace=stack_trace,
            )

            # Add to processing queue
            with self._queue_lock:
                self._log_queue.append(log_entry)

            # Also log through standard Python logging for immediate output
            logger = self.loggers.get(category, self.main_logger)
            log_level = getattr(logging, level_str, logging.INFO)
            logger.log(log_level, f"[{component}] {message}")

        except Exception as e:
            # Fallback logging
            print(f"[VoidCat Logger Error] Failed to log message: {e}", file=sys.stderr)

    # Convenience methods for different log levels
    def trace(self, message: str, **kwargs) -> None:
        """Log a trace message."""
        self.log(LogLevel.TRACE, message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message."""
        self.log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log an info message."""
        self.log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message."""
        self.log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log an error message."""
        # Automatically add stack trace for errors
        if "stack_trace" not in kwargs:
            kwargs["stack_trace"] = traceback.format_exc()
        self.log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log a critical message."""
        # Automatically add stack trace for critical errors
        if "stack_trace" not in kwargs:
            kwargs["stack_trace"] = traceback.format_exc()
        self.log(LogLevel.CRITICAL, message, **kwargs)

    def audit(self, message: str, **kwargs) -> None:
        """Log an audit event."""
        kwargs["category"] = LogCategory.AUDIT
        self.log(LogLevel.AUDIT, message, **kwargs)

    @contextmanager
    def performance_context(
        self,
        operation_name: str,
        component: str = "unknown",
        category: LogCategory = LogCategory.PERFORMANCE,
        **additional_metrics,
    ):
        """
        Context manager for tracking operation performance.

        Args:
            operation_name: Name of the operation being tracked
            component: Component performing the operation
            category: Log category
            **additional_metrics: Additional metrics to track
        """
        metrics_id = f"{component}_{operation_name}_{int(time.time() * 1000)}"

        # Start performance tracking
        perf_metrics = PerformanceMetrics(
            operation_name=operation_name,
            start_time=time.time(),
            additional_metrics=additional_metrics,
        )

        self.performance_metrics[metrics_id] = perf_metrics

        try:
            yield perf_metrics
        finally:
            # Complete performance tracking
            perf_metrics.complete()

            # Log performance metrics
            self.info(
                f"Operation completed: {operation_name}",
                category=category,
                component=component,
                performance_metrics={
                    "duration": perf_metrics.duration,
                    "memory_usage_mb": perf_metrics.memory_usage_mb,
                    "cpu_usage_percent": perf_metrics.cpu_usage_percent,
                    **perf_metrics.additional_metrics,
                },
            )

            # Add to metrics history
            self.metrics_history.append(perf_metrics)

    def get_real_time_logs(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent log entries for real-time monitoring."""
        return [log_entry.to_dict() for log_entry in list(self.log_stream)[-count:]]

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors by component."""
        return dict(self.error_counts)

    def get_component_activity(self) -> Dict[str, Any]:
        """Get activity summary by component."""
        return dict(self.component_activity)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary."""
        if not self.metrics_history:
            return {"message": "No performance metrics available"}

        recent_metrics = list(self.metrics_history)[-100:]  # Last 100 operations

        durations = [m.duration for m in recent_metrics if m.duration]

        summary = {
            "total_operations": len(recent_metrics),
            "average_duration": sum(durations) / len(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "operations_by_name": defaultdict(int),
        }

        for metrics in recent_metrics:
            summary["operations_by_name"][metrics.operation_name] += 1

        return summary

    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive logging system status."""
        return {
            "logging_system": {
                "status": "operational",
                "log_directory": str(self.log_dir),
                "handlers_configured": len(self.handlers),
                "background_thread_active": self._background_thread.is_alive(),
                "queue_size": len(self._log_queue),
            },
            "activity_summary": self.get_component_activity(),
            "error_summary": self.get_error_summary(),
            "performance_summary": self.get_performance_summary(),
            "recent_log_count": len(self.log_stream),
        }


# Global logger instance for easy access
_global_logger: Optional[VoidCatLogger] = None


def get_logger() -> VoidCatLogger:
    """Get the global VoidCat logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = VoidCatLogger()
    return _global_logger


def initialize_logging(config: Optional[Dict[str, Any]] = None) -> VoidCatLogger:
    """Initialize the global VoidCat logging system."""
    global _global_logger
    _global_logger = VoidCatLogger(config)
    return _global_logger


# Convenience functions for easy logging
def log_info(message: str, component: str = "unknown", **kwargs):
    """Log an info message using the global logger."""
    get_logger().info(message, component=component, **kwargs)


def log_error(message: str, component: str = "unknown", **kwargs):
    """Log an error message using the global logger."""
    get_logger().error(message, component=component, **kwargs)


def log_performance(
    operation_name: str, component: str = "unknown", **additional_metrics
):
    """Create a performance tracking context using the global logger."""
    return get_logger().performance_context(
        operation_name, component, **additional_metrics
    )


# Example usage and testing
if __name__ == "__main__":

    def test_logging_system():
        """Test the VoidCat logging system."""
        print("Testing VoidCat Comprehensive Logging System")
        print("=" * 50)

        # Initialize logger
        logger = VoidCatLogger({"log_directory": "test_logs"})

        # Test different log levels
        logger.info(
            "System initialization",
            component="test_system",
            details={"version": "1.0.0", "mode": "test"},
        )

        logger.warning(
            "Test warning message",
            component="test_component",
            details={"warning_type": "configuration"},
        )

        logger.error(
            "Test error message",
            component="test_component",
            details={"error_code": 500, "description": "Test error"},
        )

        # Test performance tracking
        with logger.performance_context(
            "test_operation", component="test_performance"
        ) as perf:
            time.sleep(0.1)  # Simulate work
            perf.additional_metrics["items_processed"] = 100

        # Test audit logging
        logger.audit(
            "Test security event",
            component="test_security",
            details={"action": "login_attempt", "user": "test_user"},
        )

        # Wait for background processing
        time.sleep(1)

        # Get comprehensive status
        status = logger.get_comprehensive_status()
        print("\nLogging System Status:")
        print(json.dumps(status, indent=2))

        # Get recent logs
        recent_logs = logger.get_real_time_logs(5)
        print(f"\nRecent logs ({len(recent_logs)} entries):")
        for log_entry in recent_logs:
            print(
                f"  {log_entry['timestamp']} - {log_entry['level']} - {log_entry['message']}"
            )

    test_logging_system()
