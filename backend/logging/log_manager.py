import logging
import time
import json
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import threading
import queue
import traceback
from .metrics import PerformanceMetrics

logger = logging.getLogger(__name__)

@dataclass
class LogEntry:
    """Log entry information"""
    timestamp: datetime
    level: str
    message: str
    module: str
    function: str
    line: int
    traceback: Optional[str]
    extra: Dict[str, Any]

class LogManager:
    """Advanced logging system"""
    
    def __init__(
        self,
        log_dir: str = 'logs',
        max_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        flush_interval: int = 5,
        log_format: str = 'json',
        log_level: str = 'INFO'
    ):
        self.log_dir = log_dir
        self.max_size = max_size
        self.backup_count = backup_count
        self.flush_interval = flush_interval
        self.log_format = log_format
        self.log_level = getattr(logging, log_level.upper())
        
        # Create log directory
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Log files
        self.log_files = {
            'error': os.path.join(log_dir, 'error.log'),
            'warning': os.path.join(log_dir, 'warning.log'),
            'info': os.path.join(log_dir, 'info.log'),
            'debug': os.path.join(log_dir, 'debug.log')
        }
        
        # Log queue
        self.log_queue = queue.Queue()
        
        # Log buffer
        self.log_buffer: List[LogEntry] = []
        
        # Locks
        self.buffer_lock = threading.Lock()
        self.file_lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'error_count': 0,
            'warning_count': 0,
            'info_count': 0,
            'debug_count': 0,
            'dropped_count': 0,
            'buffer_size': 0,
            'file_size': 0
        }
        
        # Start worker thread
        self.worker_thread = threading.Thread(
            target=self._worker_loop,
            daemon=True
        )
        self.worker_thread.start()
        
        # Configure root logger
        self._configure_root_logger()
    
    def log(
        self,
        level: str,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Log a message"""
        try:
            # Get caller info
            frame = traceback.extract_stack()[-2]
            module = frame[0]
            function = frame[2]
            line = frame[1]
            
            # Create log entry
            entry = LogEntry(
                timestamp=datetime.utcnow(),
                level=level.upper(),
                message=message,
                module=module,
                function=function,
                line=line,
                traceback=traceback.format_exc() if level.upper() == 'ERROR' else None,
                extra=extra or {}
            )
            
            # Add to queue
            self.log_queue.put(entry)
            
            # Update stats
            self.stats[f'{level.lower()}_count'] += 1
            
        except Exception as e:
            logger.error("Error logging message", exc_info=True)
            self.stats['dropped_count'] += 1
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message"""
        self.log('ERROR', message, extra)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self.log('WARNING', message, extra)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self.log('INFO', message, extra)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self.log('DEBUG', message, extra)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        try:
            return {
                'error_count': self.stats['error_count'],
                'warning_count': self.stats['warning_count'],
                'info_count': self.stats['info_count'],
                'debug_count': self.stats['debug_count'],
                'dropped_count': self.stats['dropped_count'],
                'buffer_size': len(self.log_buffer),
                'file_size': self._get_total_file_size(),
                'queue_size': self.log_queue.qsize()
            }
        except Exception as e:
            logger.error("Error getting log stats", exc_info=True)
            return {}
    
    def clear_logs(self):
        """Clear all log files"""
        try:
            with self.file_lock:
                for file_path in self.log_files.values():
                    if os.path.exists(file_path):
                        with open(file_path, 'w') as f:
                            f.write('')
            
            # Reset stats
            self.stats = {
                'error_count': 0,
                'warning_count': 0,
                'info_count': 0,
                'debug_count': 0,
                'dropped_count': 0,
                'buffer_size': 0,
                'file_size': 0
            }
            
        except Exception as e:
            logger.error("Error clearing logs", exc_info=True)
    
    def _configure_root_logger(self):
        """Configure root logger"""
        try:
            # Create handlers
            handlers = []
            
            for level, file_path in self.log_files.items():
                handler = logging.FileHandler(file_path)
                handler.setLevel(getattr(logging, level.upper()))
                
                if self.log_format == 'json':
                    formatter = logging.Formatter(
                        '%(message)s'
                    )
                else:
                    formatter = logging.Formatter(
                        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    )
                
                handler.setFormatter(formatter)
                handlers.append(handler)
            
            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(self.log_level)
            
            for handler in handlers:
                root_logger.addHandler(handler)
            
        except Exception as e:
            logger.error("Error configuring root logger", exc_info=True)
    
    def _worker_loop(self):
        """Background worker loop"""
        while True:
            try:
                # Get entry from queue
                entry = self.log_queue.get(timeout=self.flush_interval)
                
                # Add to buffer
                with self.buffer_lock:
                    self.log_buffer.append(entry)
                    self.stats['buffer_size'] = len(self.log_buffer)
                
                # Flush if buffer is full
                if len(self.log_buffer) >= 100:
                    self._flush_buffer()
                
            except queue.Empty:
                # Flush buffer
                self._flush_buffer()
            except Exception as e:
                logger.error("Error in worker loop", exc_info=True)
    
    def _flush_buffer(self):
        """Flush log buffer to files"""
        try:
            with self.buffer_lock:
                if not self.log_buffer:
                    return
                
                # Group entries by level
                entries_by_level = {
                    'error': [],
                    'warning': [],
                    'info': [],
                    'debug': []
                }
                
                for entry in self.log_buffer:
                    level = entry.level.lower()
                    if level in entries_by_level:
                        entries_by_level[level].append(entry)
                
                # Write to files
                with self.file_lock:
                    for level, entries in entries_by_level.items():
                        if not entries:
                            continue
                        
                        file_path = self.log_files[level]
                        
                        # Check file size
                        if os.path.exists(file_path):
                            size = os.path.getsize(file_path)
                            if size >= self.max_size:
                                self._rotate_file(file_path)
                        
                        # Write entries
                        with open(file_path, 'a') as f:
                            for entry in entries:
                                if self.log_format == 'json':
                                    log_data = {
                                        'timestamp': entry.timestamp.isoformat(),
                                        'level': entry.level,
                                        'message': entry.message,
                                        'module': entry.module,
                                        'function': entry.function,
                                        'line': entry.line,
                                        'traceback': entry.traceback,
                                        'extra': entry.extra
                                    }
                                    f.write(json.dumps(log_data) + '\n')
                                else:
                                    f.write(
                                        f"{entry.timestamp.isoformat()} - "
                                        f"{entry.level} - "
                                        f"{entry.message} - "
                                        f"{entry.module}:{entry.function}:{entry.line}"
                                    )
                                    if entry.traceback:
                                        f.write(f"\n{entry.traceback}")
                                    if entry.extra:
                                        f.write(f"\nExtra: {json.dumps(entry.extra)}")
                                    f.write('\n')
                
                # Clear buffer
                self.log_buffer.clear()
                self.stats['buffer_size'] = 0
                
                # Update file size
                self.stats['file_size'] = self._get_total_file_size()
                
        except Exception as e:
            logger.error("Error flushing buffer", exc_info=True)
    
    def _rotate_file(self, file_path: str):
        """Rotate log file"""
        try:
            # Remove oldest backup
            oldest_backup = f"{file_path}.{self.backup_count}"
            if os.path.exists(oldest_backup):
                os.remove(oldest_backup)
            
            # Rotate existing backups
            for i in range(self.backup_count - 1, 0, -1):
                old_path = f"{file_path}.{i}"
                new_path = f"{file_path}.{i + 1}"
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
            
            # Rename current file
            os.rename(file_path, f"{file_path}.1")
            
        except Exception as e:
            logger.error("Error rotating file", exc_info=True)
    
    def _get_total_file_size(self) -> int:
        """Get total size of all log files"""
        try:
            total_size = 0
            
            for file_path in self.log_files.values():
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
                    
                    # Add backup sizes
                    for i in range(1, self.backup_count + 1):
                        backup_path = f"{file_path}.{i}"
                        if os.path.exists(backup_path):
                            total_size += os.path.getsize(backup_path)
            
            return total_size
            
        except Exception as e:
            logger.error("Error getting total file size", exc_info=True)
            return 0
    
    def get_log_entries(
        self,
        level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get log entries with filters"""
        try:
            entries = []
            
            # Read log files
            with self.file_lock:
                for file_level, file_path in self.log_files.items():
                    if level and file_level != level.lower():
                        continue
                    
                    if not os.path.exists(file_path):
                        continue
                    
                    with open(file_path, 'r') as f:
                        for line in f:
                            try:
                                if self.log_format == 'json':
                                    entry = json.loads(line)
                                else:
                                    # Parse text format
                                    parts = line.split(' - ', 3)
                                    if len(parts) < 4:
                                        continue
                                    
                                    timestamp_str, level_str, message = parts
                                    entry = {
                                        'timestamp': timestamp_str,
                                        'level': level_str,
                                        'message': message.strip()
                                    }
                                
                                # Apply filters
                                if start_time and datetime.fromisoformat(entry['timestamp']) < start_time:
                                    continue
                                
                                if end_time and datetime.fromisoformat(entry['timestamp']) > end_time:
                                    continue
                                
                                entries.append(entry)
                                
                            except Exception:
                                continue
            
            # Sort by timestamp
            entries.sort(
                key=lambda x: datetime.fromisoformat(x['timestamp']),
                reverse=True
            )
            
            # Apply limit
            return entries[:limit]
            
        except Exception as e:
            logger.error("Error getting log entries", exc_info=True)
            return []
    
    def search_logs(
        self,
        query: str,
        level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search log entries"""
        try:
            entries = []
            
            # Read log files
            with self.file_lock:
                for file_level, file_path in self.log_files.items():
                    if level and file_level != level.lower():
                        continue
                    
                    if not os.path.exists(file_path):
                        continue
                    
                    with open(file_path, 'r') as f:
                        for line in f:
                            try:
                                if self.log_format == 'json':
                                    entry = json.loads(line)
                                else:
                                    # Parse text format
                                    parts = line.split(' - ', 3)
                                    if len(parts) < 4:
                                        continue
                                    
                                    timestamp_str, level_str, message = parts
                                    entry = {
                                        'timestamp': timestamp_str,
                                        'level': level_str,
                                        'message': message.strip()
                                    }
                                
                                # Apply filters
                                if start_time and datetime.fromisoformat(entry['timestamp']) < start_time:
                                    continue
                                
                                if end_time and datetime.fromisoformat(entry['timestamp']) > end_time:
                                    continue
                                
                                # Search in message
                                if query.lower() in entry['message'].lower():
                                    entries.append(entry)
                                
                            except Exception:
                                continue
            
            # Sort by timestamp
            entries.sort(
                key=lambda x: datetime.fromisoformat(x['timestamp']),
                reverse=True
            )
            
            # Apply limit
            return entries[:limit]
            
        except Exception as e:
            logger.error("Error searching logs", exc_info=True)
            return []
    
    def get_log_levels(self) -> Dict[str, int]:
        """Get count of entries by level"""
        try:
            levels = {
                'error': 0,
                'warning': 0,
                'info': 0,
                'debug': 0
            }
            
            # Read log files
            with self.file_lock:
                for file_level, file_path in self.log_files.items():
                    if not os.path.exists(file_path):
                        continue
                    
                    with open(file_path, 'r') as f:
                        for line in f:
                            try:
                                if self.log_format == 'json':
                                    entry = json.loads(line)
                                    level = entry['level'].lower()
                                else:
                                    # Parse text format
                                    parts = line.split(' - ', 3)
                                    if len(parts) < 4:
                                        continue
                                    
                                    level = parts[1].lower()
                                
                                if level in levels:
                                    levels[level] += 1
                                
                            except Exception:
                                continue
            
            return levels
            
        except Exception as e:
            logger.error("Error getting log levels", exc_info=True)
            return {}
    
    def get_log_trends(
        self,
        interval: str = 'hour',
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, List[Tuple[datetime, int]]]:
        """Get log entry trends over time"""
        try:
            trends = {
                'error': [],
                'warning': [],
                'info': [],
                'debug': []
            }
            
            # Set time range
            if not end_time:
                end_time = datetime.utcnow()
            if not start_time:
                if interval == 'hour':
                    start_time = end_time - timedelta(hours=24)
                elif interval == 'day':
                    start_time = end_time - timedelta(days=30)
                elif interval == 'week':
                    start_time = end_time - timedelta(weeks=12)
                else:
                    start_time = end_time - timedelta(days=7)
            
            # Generate time points
            time_points = []
            current = start_time
            
            if interval == 'hour':
                while current <= end_time:
                    time_points.append(current)
                    current += timedelta(hours=1)
            elif interval == 'day':
                while current <= end_time:
                    time_points.append(current)
                    current += timedelta(days=1)
            elif interval == 'week':
                while current <= end_time:
                    time_points.append(current)
                    current += timedelta(weeks=1)
            else:
                while current <= end_time:
                    time_points.append(current)
                    current += timedelta(days=1)
            
            # Initialize counts
            for level in trends:
                trends[level] = [(t, 0) for t in time_points]
            
            # Read log files
            with self.file_lock:
                for file_level, file_path in self.log_files.items():
                    if not os.path.exists(file_path):
                        continue
                    
                    with open(file_path, 'r') as f:
                        for line in f:
                            try:
                                if self.log_format == 'json':
                                    entry = json.loads(line)
                                    timestamp = datetime.fromisoformat(entry['timestamp'])
                                    level = entry['level'].lower()
                                else:
                                    # Parse text format
                                    parts = line.split(' - ', 3)
                                    if len(parts) < 4:
                                        continue
                                    
                                    timestamp = datetime.fromisoformat(parts[0])
                                    level = parts[1].lower()
                                
                                # Skip if outside time range
                                if timestamp < start_time or timestamp > end_time:
                                    continue
                                
                                # Find time point
                                for i, (t, _) in enumerate(trends[level]):
                                    if interval == 'hour':
                                        if t.hour == timestamp.hour and t.date() == timestamp.date():
                                            trends[level][i] = (t, trends[level][i][1] + 1)
                                            break
                                    elif interval == 'day':
                                        if t.date() == timestamp.date():
                                            trends[level][i] = (t, trends[level][i][1] + 1)
                                            break
                                    elif interval == 'week':
                                        if t.isocalendar() == timestamp.isocalendar():
                                            trends[level][i] = (t, trends[level][i][1] + 1)
                                            break
                                    else:
                                        if t.date() == timestamp.date():
                                            trends[level][i] = (t, trends[level][i][1] + 1)
                                            break
                                
                            except Exception:
                                continue
            
            return trends
            
        except Exception as e:
            logger.error("Error getting log trends", exc_info=True)
            return {} 