import logging
import json
import os
import base64
import hashlib
import difflib
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import threading
import yaml
import toml
import jsonschema
from cryptography.fernet import Fernet
from prometheus_client import Counter, Histogram, Gauge
from .metrics import PerformanceMetrics
import redis
from redis.exceptions import RedisError
import aiohttp
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

# Prometheus metrics
CONFIG_OPERATIONS = Counter('config_operations_total', 'Total configuration operations', ['operation'])
CONFIG_LATENCY = Histogram('config_operation_latency_seconds', 'Configuration operation latency', ['operation'])
CONFIG_ERRORS = Counter('config_errors_total', 'Total configuration errors', ['error_type'])
CONFIG_CACHE_HITS = Counter('config_cache_hits_total', 'Configuration cache hits')
CONFIG_CACHE_MISSES = Counter('config_cache_misses_total', 'Configuration cache misses')
CONFIG_MEMORY_USAGE = Gauge('config_memory_usage_bytes', 'Configuration memory usage')

@dataclass
class ConfigValue:
    """Enhanced configuration value information"""
    value: Any
    source: str
    timestamp: datetime
    description: Optional[str]
    validation: Optional[Dict[str, Any]]
    encrypted: bool = False
    profile: Optional[str] = None
    environment: Optional[str] = None
    version: str = "1.0"
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    last_modified: datetime = None
    modified_by: str = None
    audit_log: List[Dict[str, Any]] = None

class ConfigManager:
    """Advanced configuration system with enhanced features"""
    
    def __init__(
        self,
        config_dir: str = 'config',
        default_format: str = 'json',
        reload_interval: int = 300,
        validate_on_load: bool = True,
        encryption_key: Optional[str] = None,
        default_profile: str = 'default',
        default_environment: str = 'development',
        redis_url: Optional[str] = None,
        enable_cache: bool = True,
        enable_audit: bool = True,
        enable_metrics: bool = True,
        max_history_size: int = 1000,
        backup_retention_days: int = 30
    ):
        self.config_dir = config_dir
        self.default_format = default_format
        self.reload_interval = reload_interval
        self.validate_on_load = validate_on_load
        self.default_profile = default_profile
        self.default_environment = default_environment
        self.enable_cache = enable_cache
        self.enable_audit = enable_audit
        self.enable_metrics = enable_metrics
        self.max_history_size = max_history_size
        self.backup_retention_days = backup_retention_days
        
        # Initialize Redis cache if enabled
        if enable_cache and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.cache_enabled = True
            except RedisError as e:
                logger.error(f"Failed to initialize Redis cache: {e}")
                self.cache_enabled = False
        else:
            self.cache_enabled = False
        
        # Create necessary directories
        self._create_directories()
        
        # Initialize data structures
        self._initialize_data_structures()
        
        # Initialize encryption
        self._initialize_encryption(encryption_key)
        
        # Start background tasks
        self._start_background_tasks()
        
        # Load initial configuration
        self._load_initial_config()
    
    def _create_directories(self):
        """Create all necessary directories"""
        directories = [
            self.config_dir,
            os.path.join(self.config_dir, 'profiles'),
            os.path.join(self.config_dir, 'templates'),
            os.path.join(self.config_dir, 'backups'),
            os.path.join(self.config_dir, 'schemas'),
            os.path.join(self.config_dir, 'audit_logs'),
            os.path.join(self.config_dir, 'migrations')
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def _initialize_data_structures(self):
        """Initialize all data structures with thread safety"""
        self.values = {}
        self.files = {}
        self.schemas = {}
        self.templates = {}
        self.history = {}
        self.dependencies = {}
        self.audit_log = []
        
        # Thread-safe locks
        self.values_lock = threading.Lock()
        self.files_lock = threading.Lock()
        self.schemas_lock = threading.Lock()
        self.templates_lock = threading.Lock()
        self.history_lock = threading.Lock()
        self.dependencies_lock = threading.Lock()
        self.audit_lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'load_count': 0,
            'save_count': 0,
            'validation_errors': 0,
            'reload_count': 0,
            'backup_count': 0,
            'restore_count': 0,
            'encryption_count': 0,
            'decryption_count': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'audit_entries': 0
        }
    
    def _initialize_encryption(self, encryption_key: Optional[str]):
        """Initialize encryption with key rotation support"""
        if encryption_key:
            self.encryption_key = base64.urlsafe_b64encode(
                hashlib.sha256(encryption_key.encode()).digest()
            )
            self.cipher = Fernet(self.encryption_key)
            self.key_rotation_date = datetime.utcnow()
        else:
            self.encryption_key = None
            self.cipher = None
            self.key_rotation_date = None
    
    def _start_background_tasks(self):
        """Start all background tasks"""
        self.reload_thread = threading.Thread(
            target=self._reload_loop,
            daemon=True
        )
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True
        )
        self.metrics_thread = threading.Thread(
            target=self._metrics_loop,
            daemon=True
        )
        
        self.reload_thread.start()
        self.cleanup_thread.start()
        self.metrics_thread.start()
    
    def _load_initial_config(self):
        """Load initial configuration with error handling"""
        try:
            self._load_environment_variables()
            self._load_schemas()
            self._load_templates()
            self._load_profiles()
            self._validate_initial_config()
        except Exception as e:
            logger.error("Error loading initial configuration", exc_info=True)
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _fetch_remote_config(self, url: str) -> Dict[str, Any]:
        """Fetch configuration from remote source with retry logic"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                raise Exception(f"Failed to fetch remote config: {response.status}")
    
    def _cleanup_loop(self):
        """Background task for cleanup operations"""
        while True:
            try:
                self._cleanup_old_backups()
                self._cleanup_old_audit_logs()
                self._cleanup_old_history()
                time.sleep(3600)  # Run every hour
            except Exception as e:
                logger.error("Error in cleanup loop", exc_info=True)
    
    def _metrics_loop(self):
        """Background task for metrics collection"""
        while True:
            try:
                if self.enable_metrics:
                    self._update_metrics()
                time.sleep(60)  # Run every minute
            except Exception as e:
                logger.error("Error in metrics loop", exc_info=True)
    
    def _update_metrics(self):
        """Update Prometheus metrics"""
        CONFIG_MEMORY_USAGE.set(self._get_memory_usage())
        for operation, count in self.stats.items():
            CONFIG_OPERATIONS.labels(operation=operation).inc(count)
    
    def _get_memory_usage(self) -> int:
        """Calculate memory usage of configuration data"""
        import sys
        return sys.getsizeof(self.values) + sys.getsizeof(self.files) + \
               sys.getsizeof(self.schemas) + sys.getsizeof(self.templates)
    
    def _cleanup_old_backups(self):
        """Clean up old backup files"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.backup_retention_days)
        backup_dir = os.path.join(self.config_dir, 'backups')
        
        for backup in os.listdir(backup_dir):
            backup_path = os.path.join(backup_dir, backup)
            if os.path.getmtime(backup_path) < cutoff_date.timestamp():
                os.remove(backup_path)
    
    def _cleanup_old_audit_logs(self):
        """Clean up old audit logs"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.backup_retention_days)
        audit_dir = os.path.join(self.config_dir, 'audit_logs')
        
        for log_file in os.listdir(audit_dir):
            log_path = os.path.join(audit_dir, log_file)
            if os.path.getmtime(log_path) < cutoff_date.timestamp():
                os.remove(log_path)
    
    def _cleanup_old_history(self):
        """Clean up old history entries"""
        with self.history_lock:
            for key in self.history:
                self.history[key] = self.history[key][-self.max_history_size:]
    
    def _validate_initial_config(self):
        """Validate initial configuration"""
        if self.validate_on_load:
            for key, value in self.values.items():
                if value.validation:
                    if not self._validate_value(value.value, value.validation):
                        logger.warning(f"Invalid initial configuration for key: {key}")
    
    def _load_profiles(self):
        """Load configuration profiles"""
        profiles_dir = os.path.join(self.config_dir, 'profiles')
        if not os.path.exists(profiles_dir):
            return
        
        for profile in os.listdir(profiles_dir):
            profile_path = os.path.join(profiles_dir, profile)
            if os.path.isdir(profile_path):
                self._load_profile(profile)
    
    def _load_profile(self, profile: str):
        """Load a specific profile"""
        profile_path = os.path.join(self.config_dir, 'profiles', profile)
        info_path = os.path.join(profile_path, 'info.json')
        
        if os.path.exists(info_path):
            with open(info_path, 'r') as f:
                profile_info = json.load(f)
            
            # Load profile-specific configuration
            config_path = os.path.join(profile_path, f'config.{self.default_format}')
            if os.path.exists(config_path):
                self.load_config(
                    name=profile,
                    file_path=config_path,
                    profile=profile,
                    description=profile_info.get('description')
                )
    
    def _load_environment_variables(self):
        """Load configuration from environment variables"""
        try:
            for key, value in os.environ.items():
                if key.startswith('CONFIG_'):
                    config_key = key[7:].lower()
                    self.set_value(
                        config_key,
                        value,
                        source='environment',
                        environment=self.default_environment
                    )
        except Exception as e:
            logger.error("Error loading environment variables", exc_info=True)
    
    def _load_schemas(self):
        """Load configuration schemas"""
        try:
            schema_dir = os.path.join(self.config_dir, 'schemas')
            if not os.path.exists(schema_dir):
                return
            
            for file_name in os.listdir(schema_dir):
                if file_name.endswith('.json'):
                    schema_name = file_name[:-5]
                    schema_path = os.path.join(schema_dir, file_name)
                    
                    with open(schema_path, 'r') as f:
                        schema = json.load(f)
                    
                    with self.schemas_lock:
                        self.schemas[schema_name] = schema
        except Exception as e:
            logger.error("Error loading schemas", exc_info=True)
    
    def _load_templates(self):
        """Load configuration templates"""
        try:
            for file_name in os.listdir(self.templates_dir):
                if file_name.endswith(('.json', '.yaml', '.toml')):
                    template_name = os.path.splitext(file_name)[0]
                    template_path = os.path.join(self.templates_dir, file_name)
                    
                    with open(template_path, 'r') as f:
                        if file_name.endswith('.json'):
                            template = json.load(f)
                        elif file_name.endswith('.yaml'):
                            template = yaml.safe_load(f)
                        else:
                            template = toml.load(f)
                    
                    with self.templates_lock:
                        self.templates[template_name] = template
        except Exception as e:
            logger.error("Error loading templates", exc_info=True)
    
    def load_config(
        self,
        name: str,
        file_path: Optional[str] = None,
        format: Optional[str] = None,
        description: Optional[str] = None,
        validation: Optional[Dict[str, Any]] = None,
        profile: Optional[str] = None,
        environment: Optional[str] = None,
        encrypt: bool = False
    ):
        """Load configuration from file"""
        try:
            # Set file path
            if not file_path:
                file_path = os.path.join(
                    self.config_dir,
                    f"{name}.{format or self.default_format}"
                )
            
            # Check file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Config file {file_path} not found")
            
            # Load file
            with open(file_path, 'r') as f:
                if format == 'yaml' or file_path.endswith('.yaml'):
                    config = yaml.safe_load(f)
                elif format == 'toml' or file_path.endswith('.toml'):
                    config = toml.load(f)
                else:
                    config = json.load(f)
            
            # Store file path
            with self.files_lock:
                self.files[name] = file_path
            
            # Store values
            with self.values_lock:
                for key, value in config.items():
                    # Validate value
                    if self.validate_on_load and validation:
                        if not self._validate_value(value, validation):
                            self.stats['validation_errors'] += 1
                            continue
                    
                    # Encrypt value if needed
                    if encrypt and self.cipher:
                        value = self._encrypt_value(value)
                        self.stats['encryption_count'] += 1
                    
                    self.values[key] = ConfigValue(
                        value=value,
                        source=file_path,
                        timestamp=datetime.utcnow(),
                        description=description,
                        validation=validation,
                        encrypted=encrypt,
                        profile=profile or self.default_profile,
                        environment=environment or self.default_environment
                    )
            
            # Update stats
            self.stats['load_count'] += 1
            
        except Exception as e:
            logger.error("Error loading config", exc_info=True)
            raise
    
    def save_config(
        self,
        name: str,
        file_path: Optional[str] = None,
        format: Optional[str] = None,
        profile: Optional[str] = None,
        environment: Optional[str] = None
    ):
        """Save configuration to file"""
        try:
            # Set file path
            if not file_path:
                file_path = os.path.join(
                    self.config_dir,
                    f"{name}.{format or self.default_format}"
                )
            
            # Get values
            with self.values_lock:
                config = {
                    key: value.value
                    for key, value in self.values.items()
                    if value.source == file_path and
                    (not profile or value.profile == profile) and
                    (not environment or value.environment == environment)
                }
            
            # Save file
            with open(file_path, 'w') as f:
                if format == 'yaml' or file_path.endswith('.yaml'):
                    yaml.dump(config, f)
                elif format == 'toml' or file_path.endswith('.toml'):
                    toml.dump(config, f)
                else:
                    json.dump(config, f, indent=2)
            
            # Update stats
            self.stats['save_count'] += 1
            
        except Exception as e:
            logger.error("Error saving config", exc_info=True)
            raise
    
    def get_value(
        self,
        key: str,
        default: Any = None,
        profile: Optional[str] = None,
        environment: Optional[str] = None
    ) -> Any:
        """Get configuration value"""
        try:
            with self.values_lock:
                if key in self.values:
                    value = self.values[key]
                    
                    # Check profile and environment
                    if profile and value.profile != profile:
                        return default
                    if environment and value.environment != environment:
                        return default
                    
                    # Decrypt value if needed
                    if value.encrypted and self.cipher:
                        decrypted = self._decrypt_value(value.value)
                        self.stats['decryption_count'] += 1
                        return decrypted
                    
                    return value.value
                return default
                
        except Exception as e:
            logger.error("Error getting value", exc_info=True)
            return default
    
    def set_value(
        self,
        key: str,
        value: Any,
        source: Optional[str] = None,
        description: Optional[str] = None,
        validation: Optional[Dict[str, Any]] = None,
        encrypt: bool = False,
        profile: Optional[str] = None,
        environment: Optional[str] = None
    ):
        """Set configuration value"""
        try:
            # Validate value
            if validation and not self._validate_value(value, validation):
                self.stats['validation_errors'] += 1
                raise ValueError(f"Invalid value for {key}")
            
            # Encrypt value if needed
            if encrypt and self.cipher:
                value = self._encrypt_value(value)
                self.stats['encryption_count'] += 1
            
            with self.values_lock:
                self.values[key] = ConfigValue(
                    value=value,
                    source=source or 'memory',
                    timestamp=datetime.utcnow(),
                    description=description,
                    validation=validation,
                    encrypted=encrypt,
                    profile=profile or self.default_profile,
                    environment=environment or self.default_environment
                )
            
        except Exception as e:
            logger.error("Error setting value", exc_info=True)
            raise
    
    def delete_value(self, key: str):
        """Delete configuration value"""
        try:
            with self.values_lock:
                if key in self.values:
                    del self.values[key]
            
        except Exception as e:
            logger.error("Error deleting value", exc_info=True)
            raise
    
    def get_all_values(self) -> Dict[str, Any]:
        """Get all configuration values"""
        try:
            with self.values_lock:
                return {
                    key: value.value
                    for key, value in self.values.items()
                }
                
        except Exception as e:
            logger.error("Error getting all values", exc_info=True)
            return {}
    
    def get_value_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get configuration value information"""
        try:
            with self.values_lock:
                if key in self.values:
                    value = self.values[key]
                    return {
                        'value': value.value,
                        'source': value.source,
                        'timestamp': value.timestamp.isoformat(),
                        'description': value.description,
                        'validation': value.validation
                    }
                return None
                
        except Exception as e:
            logger.error("Error getting value info", exc_info=True)
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get configuration statistics"""
        try:
            return {
                'load_count': self.stats['load_count'],
                'save_count': self.stats['save_count'],
                'validation_errors': self.stats['validation_errors'],
                'reload_count': self.stats['reload_count'],
                'backup_count': self.stats['backup_count'],
                'restore_count': self.stats['restore_count'],
                'encryption_count': self.stats['encryption_count'],
                'decryption_count': self.stats['decryption_count'],
                'value_count': len(self.values),
                'file_count': len(self.files),
                'schema_count': len(self.schemas),
                'template_count': len(self.templates),
                'profile_count': len(os.listdir(self.profiles_dir)),
                'backup_count': len(os.listdir(self.backups_dir)),
                'values': {
                    key: {
                        'source': value.source,
                        'timestamp': value.timestamp.isoformat(),
                        'description': value.description,
                        'validation': value.validation,
                        'encrypted': value.encrypted,
                        'profile': value.profile,
                        'environment': value.environment
                    }
                    for key, value in self.values.items()
                }
            }
        except Exception as e:
            logger.error("Error getting config stats", exc_info=True)
            return {}
    
    def _reload_loop(self):
        """Background reload loop"""
        while True:
            try:
                time.sleep(self.reload_interval)
                self._reload_configs()
            except Exception as e:
                logger.error("Error in reload loop", exc_info=True)
    
    def _reload_configs(self):
        """Reload all configurations"""
        try:
            with self.files_lock:
                for name, file_path in self.files.items():
                    try:
                        self.load_config(name, file_path)
                    except Exception:
                        continue
            
            # Update stats
            self.stats['reload_count'] += 1
            
        except Exception as e:
            logger.error("Error reloading configs", exc_info=True)
    
    def _validate_value(
        self,
        value: Any,
        validation: Dict[str, Any]
    ) -> bool:
        """Validate configuration value"""
        try:
            # Check type
            if 'type' in validation:
                if not isinstance(value, eval(validation['type'])):
                    return False
            
            # Check range
            if 'min' in validation:
                if value < validation['min']:
                    return False
            
            if 'max' in validation:
                if value > validation['max']:
                    return False
            
            # Check length
            if 'min_length' in validation:
                if len(value) < validation['min_length']:
                    return False
            
            if 'max_length' in validation:
                if len(value) > validation['max_length']:
                    return False
            
            # Check pattern
            if 'pattern' in validation:
                import re
                if not re.match(validation['pattern'], str(value)):
                    return False
            
            # Check enum
            if 'enum' in validation:
                if value not in validation['enum']:
                    return False
            
            # Check custom validation
            if 'validate' in validation:
                if not validation['validate'](value):
                    return False
            
            return True
            
        except Exception as e:
            logger.error("Error validating value", exc_info=True)
            return False
    
    def get_value_history(
        self,
        key: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Tuple[datetime, Any]]:
        """Get value history"""
        try:
            with self.values_lock:
                if key not in self.values:
                    return []
                
                value = self.values[key]
                
                # Apply time filters
                if start_time and value.timestamp < start_time:
                    return []
                
                if end_time and value.timestamp > end_time:
                    return []
                
                return [(value.timestamp, value.value)]
                
        except Exception as e:
            logger.error("Error getting value history", exc_info=True)
            return []
    
    def get_values_by_source(
        self,
        source: str
    ) -> Dict[str, Any]:
        """Get values by source"""
        try:
            with self.values_lock:
                return {
                    key: value.value
                    for key, value in self.values.items()
                    if value.source == source
                }
                
        except Exception as e:
            logger.error("Error getting values by source", exc_info=True)
            return {}
    
    def get_values_by_validation(
        self,
        validation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get values by validation rules"""
        try:
            with self.values_lock:
                return {
                    key: value.value
                    for key, value in self.values.items()
                    if value.validation == validation
                }
                
        except Exception as e:
            logger.error("Error getting values by validation", exc_info=True)
            return {}
    
    def export_config(
        self,
        format: str = 'json',
        include_info: bool = False
    ) -> str:
        """Export configuration"""
        try:
            with self.values_lock:
                if include_info:
                    config = {
                        key: {
                            'value': value.value,
                            'source': value.source,
                            'timestamp': value.timestamp.isoformat(),
                            'description': value.description,
                            'validation': value.validation
                        }
                        for key, value in self.values.items()
                    }
                else:
                    config = {
                        key: value.value
                        for key, value in self.values.items()
                    }
            
            if format == 'yaml':
                return yaml.dump(config)
            elif format == 'toml':
                return toml.dumps(config)
            else:
                return json.dumps(config, indent=2)
                
        except Exception as e:
            logger.error("Error exporting config", exc_info=True)
            return ''
    
    def import_config(
        self,
        config: str,
        format: str = 'json',
        validate: bool = True
    ):
        """Import configuration"""
        try:
            # Parse config
            if format == 'yaml':
                values = yaml.safe_load(config)
            elif format == 'toml':
                values = toml.loads(config)
            else:
                values = json.loads(config)
            
            # Import values
            with self.values_lock:
                for key, value in values.items():
                    # Get existing value
                    existing = self.values.get(key)
                    
                    # Validate value
                    if validate and existing and existing.validation:
                        if not self._validate_value(value, existing.validation):
                            self.stats['validation_errors'] += 1
                            continue
                    
                    # Set value
                    self.values[key] = ConfigValue(
                        value=value,
                        source='import',
                        timestamp=datetime.utcnow(),
                        description=existing.description if existing else None,
                        validation=existing.validation if existing else None
                    )
            
        except Exception as e:
            logger.error("Error importing config", exc_info=True)
            raise
    
    def get_value_dependencies(
        self,
        key: str
    ) -> List[str]:
        """Get value dependencies"""
        try:
            with self.values_lock:
                if key not in self.values:
                    return []
                
                value = self.values[key]
                
                # Check for references
                dependencies = []
                
                if isinstance(value.value, str):
                    # Look for ${var} references
                    import re
                    refs = re.findall(r'\${([^}]+)}', value.value)
                    dependencies.extend(refs)
                
                return dependencies
                
        except Exception as e:
            logger.error("Error getting value dependencies", exc_info=True)
            return []
    
    def get_value_dependents(
        self,
        key: str
    ) -> List[str]:
        """Get value dependents"""
        try:
            with self.values_lock:
                dependents = []
                
                for k, v in self.values.items():
                    if isinstance(v.value, str):
                        # Look for ${key} references
                        if f"${{{key}}}" in v.value:
                            dependents.append(k)
                
                return dependents
                
        except Exception as e:
            logger.error("Error getting value dependents", exc_info=True)
            return []
    
    def get_value_tree(self) -> Dict[str, Any]:
        """Get value dependency tree"""
        try:
            with self.values_lock:
                tree = {}
                
                for key in self.values:
                    tree[key] = {
                        'dependencies': self.get_value_dependencies(key),
                        'dependents': self.get_value_dependents(key)
                    }
                
                return tree
                
        except Exception as e:
            logger.error("Error getting value tree", exc_info=True)
            return {}
    
    def create_profile(
        self,
        name: str,
        description: Optional[str] = None,
        parent: Optional[str] = None
    ):
        """Create a new configuration profile"""
        try:
            profile_dir = os.path.join(self.profiles_dir, name)
            if not os.path.exists(profile_dir):
                os.makedirs(profile_dir)
            
            # Create profile info
            profile_info = {
                'name': name,
                'description': description,
                'parent': parent,
                'created': datetime.utcnow().isoformat()
            }
            
            # Save profile info
            with open(os.path.join(profile_dir, 'info.json'), 'w') as f:
                json.dump(profile_info, f, indent=2)
            
        except Exception as e:
            logger.error("Error creating profile", exc_info=True)
            raise
    
    def switch_profile(self, name: str):
        """Switch to a different configuration profile"""
        try:
            profile_dir = os.path.join(self.profiles_dir, name)
            if not os.path.exists(profile_dir):
                raise ValueError(f"Profile {name} does not exist")
            
            self.default_profile = name
            
        except Exception as e:
            logger.error("Error switching profile", exc_info=True)
            raise
    
    def switch_environment(self, name: str):
        """Switch to a different environment"""
        try:
            self.default_environment = name
            
        except Exception as e:
            logger.error("Error switching environment", exc_info=True)
            raise
    
    def create_backup(self, name: Optional[str] = None):
        """Create a configuration backup"""
        try:
            # Generate backup name
            if not name:
                name = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            
            backup_dir = os.path.join(self.backups_dir, name)
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Export current configuration
            config = self.export_config(include_info=True)
            
            # Save backup
            with open(os.path.join(backup_dir, 'config.json'), 'w') as f:
                f.write(config)
            
            # Update stats
            self.stats['backup_count'] += 1
            
        except Exception as e:
            logger.error("Error creating backup", exc_info=True)
            raise
    
    def restore_backup(self, name: str):
        """Restore configuration from backup"""
        try:
            backup_dir = os.path.join(self.backups_dir, name)
            if not os.path.exists(backup_dir):
                raise ValueError(f"Backup {name} does not exist")
            
            # Load backup
            with open(os.path.join(backup_dir, 'config.json'), 'r') as f:
                config = f.read()
            
            # Import configuration
            self.import_config(config)
            
            # Update stats
            self.stats['restore_count'] += 1
            
        except Exception as e:
            logger.error("Error restoring backup", exc_info=True)
            raise
    
    def get_backups(self) -> List[Dict[str, Any]]:
        """Get list of available backups"""
        try:
            backups = []
            
            for name in os.listdir(self.backups_dir):
                backup_dir = os.path.join(self.backups_dir, name)
                if os.path.isdir(backup_dir):
                    backup_file = os.path.join(backup_dir, 'config.json')
                    if os.path.exists(backup_file):
                        backups.append({
                            'name': name,
                            'created': datetime.fromtimestamp(
                                os.path.getctime(backup_file)
                            ).isoformat(),
                            'size': os.path.getsize(backup_file)
                        })
            
            return sorted(
                backups,
                key=lambda x: x['created'],
                reverse=True
            )
            
        except Exception as e:
            logger.error("Error getting backups", exc_info=True)
            return []
    
    def create_template(
        self,
        name: str,
        template: Dict[str, Any],
        description: Optional[str] = None
    ):
        """Create a configuration template"""
        try:
            template_path = os.path.join(
                self.templates_dir,
                f"{name}.{self.default_format}"
            )
            
            # Save template
            with open(template_path, 'w') as f:
                if self.default_format == 'yaml':
                    yaml.dump(template, f)
                elif self.default_format == 'toml':
                    toml.dump(template, f)
                else:
                    json.dump(template, f, indent=2)
            
            # Store template info
            with self.templates_lock:
                self.templates[name] = {
                    'template': template,
                    'description': description
                }
            
        except Exception as e:
            logger.error("Error creating template", exc_info=True)
            raise
    
    def apply_template(
        self,
        name: str,
        values: Dict[str, Any],
        profile: Optional[str] = None,
        environment: Optional[str] = None
    ):
        """Apply a configuration template"""
        try:
            with self.templates_lock:
                if name not in self.templates:
                    raise ValueError(f"Template {name} does not exist")
                
                template = self.templates[name]['template']
            
            # Apply template
            for key, value in template.items():
                if key in values:
                    self.set_value(
                        key,
                        values[key],
                        source='template',
                        profile=profile,
                        environment=environment
                    )
                else:
                    self.set_value(
                        key,
                        value,
                        source='template',
                        profile=profile,
                        environment=environment
                    )
            
        except Exception as e:
            logger.error("Error applying template", exc_info=True)
            raise
    
    def get_templates(self) -> List[Dict[str, Any]]:
        """Get list of available templates"""
        try:
            templates = []
            
            with self.templates_lock:
                for name, info in self.templates.items():
                    templates.append({
                        'name': name,
                        'description': info['description'],
                        'keys': list(info['template'].keys())
                    })
            
            return templates
            
        except Exception as e:
            logger.error("Error getting templates", exc_info=True)
            return []
    
    def generate_docs(self, output_dir: str):
        """Generate configuration documentation"""
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Generate main documentation
            with open(os.path.join(output_dir, 'README.md'), 'w') as f:
                f.write("# Configuration Documentation\n\n")
                
                # Write profiles
                f.write("## Profiles\n\n")
                for name in os.listdir(self.profiles_dir):
                    profile_dir = os.path.join(self.profiles_dir, name)
                    if os.path.isdir(profile_dir):
                        info_path = os.path.join(profile_dir, 'info.json')
                        if os.path.exists(info_path):
                            with open(info_path, 'r') as info_file:
                                info = json.load(info_file)
                                f.write(f"### {name}\n")
                                f.write(f"{info['description']}\n\n")
                
                # Write templates
                f.write("## Templates\n\n")
                for template in self.get_templates():
                    f.write(f"### {template['name']}\n")
                    f.write(f"{template['description']}\n\n")
                    f.write("Configuration keys:\n")
                    for key in template['keys']:
                        f.write(f"- {key}\n")
                    f.write("\n")
                
                # Write schemas
                f.write("## Schemas\n\n")
                with self.schemas_lock:
                    for name, schema in self.schemas.items():
                        f.write(f"### {name}\n")
                        f.write("```json\n")
                        f.write(json.dumps(schema, indent=2))
                        f.write("\n```\n\n")
            
        except Exception as e:
            logger.error("Error generating documentation", exc_info=True)
            raise
    
    def _encrypt_value(self, value: Any) -> str:
        """Encrypt a configuration value"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return self.cipher.encrypt(str(value).encode()).decode()
        except Exception as e:
            logger.error("Error encrypting value", exc_info=True)
            raise
    
    def _decrypt_value(self, value: str) -> Any:
        """Decrypt a configuration value"""
        try:
            decrypted = self.cipher.decrypt(value.encode()).decode()
            try:
                return json.loads(decrypted)
            except json.JSONDecodeError:
                return decrypted
        except Exception as e:
            logger.error("Error decrypting value", exc_info=True)
            raise
    
    def get_diff(
        self,
        other_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get differences between configurations"""
        try:
            current_config = self.get_all_values()
            
            diff = {
                'added': {},
                'removed': {},
                'modified': {}
            }
            
            # Find added and modified values
            for key, value in other_config.items():
                if key not in current_config:
                    diff['added'][key] = value
                elif value != current_config[key]:
                    diff['modified'][key] = {
                        'old': current_config[key],
                        'new': value
                    }
            
            # Find removed values
            for key, value in current_config.items():
                if key not in other_config:
                    diff['removed'][key] = value
            
            return diff
            
        except Exception as e:
            logger.error("Error getting config diff", exc_info=True)
            return {}
    
    def validate_schema(
        self,
        schema_name: str,
        values: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate values against a schema"""
        try:
            with self.schemas_lock:
                if schema_name not in self.schemas:
                    raise ValueError(f"Schema {schema_name} does not exist")
                
                schema = self.schemas[schema_name]
            
            # Validate values
            validator = jsonschema.Draft7Validator(schema)
            errors = list(validator.iter_errors(values))
            
            return len(errors) == 0, [str(e) for e in errors]
            
        except Exception as e:
            logger.error("Error validating schema", exc_info=True)
            return False, [str(e)] 