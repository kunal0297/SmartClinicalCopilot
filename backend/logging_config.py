import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import json
from .config import settings

class CustomJSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
            
        # Add extra fields if present
        if hasattr(record, "extra"):
            log_data.update(record.extra)
            
        return json.dumps(log_data)

def setup_logging() -> None:
    """Configure logging with file rotation and structured output"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create handlers
    handlers = []
    
    # Console handler with color
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)
    
    # File handler for all logs
    all_logs_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    all_logs_handler.setLevel(logging.DEBUG)
    all_logs_handler.setFormatter(CustomJSONFormatter())
    handlers.append(all_logs_handler)
    
    # File handler for errors
    error_logs_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "error.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_logs_handler.setLevel(logging.ERROR)
    error_logs_handler.setFormatter(CustomJSONFormatter())
    handlers.append(error_logs_handler)
    
    # Add handlers to root logger
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Set logging levels for specific modules
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info("Logging system initialized", extra={
        "environment": settings.ENVIRONMENT,
        "log_level": settings.LOG_LEVEL,
        "log_dir": str(log_dir.absolute())
    })

class LogContext:
    """Context manager for adding context to log messages"""
    
    def __init__(self, **context):
        self.context = context
        self.old_context = {}
        
    def __enter__(self):
        # Store old context
        logger = logging.getLogger()
        for handler in logger.handlers:
            if isinstance(handler.formatter, CustomJSONFormatter):
                self.old_context[handler] = getattr(handler.formatter, 'extra', {})
                handler.formatter.extra = {**self.old_context[handler], **self.context}
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore old context
        logger = logging.getLogger()
        for handler in logger.handlers:
            if isinstance(handler.formatter, CustomJSONFormatter):
                handler.formatter.extra = self.old_context.get(handler, {}) 