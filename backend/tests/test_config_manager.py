import unittest
import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from ..config.config_manager import ConfigManager, ConfigValue
import pytest

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        # Create temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(
            config_dir=self.test_dir,
            default_format='json',
            reload_interval=1,
            validate_on_load=True
        )
        
        # Sample validation rules
        self.validation_rules = {
            'string': {
                'type': 'str',
                'min_length': 3,
                'max_length': 10,
                'pattern': r'^[a-z]+$'
            },
            'number': {
                'type': 'int',
                'min': 0,
                'max': 100
            },
            'enum': {
                'type': 'str',
                'enum': ['red', 'green', 'blue']
            }
        }
    
    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_load_save_config(self):
        # Create test config
        config = {
            'name': 'test',
            'value': 42,
            'color': 'red'
        }
        
        # Save config
        config_path = os.path.join(self.test_dir, 'test.json')
        with open(config_path, 'w') as f:
            json.dump(config, f)
        
        # Load config
        self.config_manager.load_config('test', config_path)
        
        # Verify values
        self.assertEqual(self.config_manager.get_value('name'), 'test')
        self.assertEqual(self.config_manager.get_value('value'), 42)
        self.assertEqual(self.config_manager.get_value('color'), 'red')
        
        # Save config
        self.config_manager.save_config('test')
        
        # Verify file
        with open(config_path, 'r') as f:
            saved_config = json.load(f)
        self.assertEqual(saved_config, config)
    
    def test_validation(self):
        # Test valid values
        self.config_manager.set_value(
            'valid_string',
            'hello',
            validation=self.validation_rules['string']
        )
        self.assertEqual(
            self.config_manager.get_value('valid_string'),
            'hello'
        )
        
        # Test invalid values
        with self.assertRaises(ValueError):
            self.config_manager.set_value(
                'invalid_string',
                'hi',  # Too short
                validation=self.validation_rules['string']
            )
        
        with self.assertRaises(ValueError):
            self.config_manager.set_value(
                'invalid_number',
                150,  # Too large
                validation=self.validation_rules['number']
            )
        
        with self.assertRaises(ValueError):
            self.config_manager.set_value(
                'invalid_enum',
                'yellow',  # Not in enum
                validation=self.validation_rules['enum']
            )
    
    def test_value_history(self):
        # Set initial value
        self.config_manager.set_value('test', 'initial')
        
        # Update value
        self.config_manager.set_value('test', 'updated')
        
        # Get history
        history = self.config_manager.get_value_history('test')
        self.assertEqual(len(history), 1)  # Only latest value stored
        
        # Get history with time filter
        past = datetime.utcnow() - timedelta(hours=1)
        future = datetime.utcnow() + timedelta(hours=1)
        
        history = self.config_manager.get_value_history(
            'test',
            start_time=past,
            end_time=future
        )
        self.assertEqual(len(history), 1)
    
    def test_dependencies(self):
        # Set values with dependencies
        self.config_manager.set_value('base_url', 'http://example.com')
        self.config_manager.set_value(
            'api_url',
            '${base_url}/api'
        )
        
        # Check dependencies
        deps = self.config_manager.get_value_dependencies('api_url')
        self.assertEqual(deps, ['base_url'])
        
        # Check dependents
        deps = self.config_manager.get_value_dependents('base_url')
        self.assertEqual(deps, ['api_url'])
        
        # Get dependency tree
        tree = self.config_manager.get_value_tree()
        self.assertEqual(
            tree['api_url']['dependencies'],
            ['base_url']
        )
        self.assertEqual(
            tree['base_url']['dependents'],
            ['api_url']
        )
    
    def test_export_import(self):
        # Set test values
        self.config_manager.set_value('test1', 'value1')
        self.config_manager.set_value('test2', 'value2')
        
        # Export config
        exported = self.config_manager.export_config(
            format='json',
            include_info=True
        )
        
        # Clear config
        self.config_manager.delete_value('test1')
        self.config_manager.delete_value('test2')
        
        # Import config
        self.config_manager.import_config(exported)
        
        # Verify values
        self.assertEqual(self.config_manager.get_value('test1'), 'value1')
        self.assertEqual(self.config_manager.get_value('test2'), 'value2')
    
    def test_stats(self):
        # Perform operations
        self.config_manager.set_value('test', 'value')
        self.config_manager.get_value('test')
        self.config_manager.delete_value('test')
        
        # Get stats
        stats = self.config_manager.get_stats()
        
        # Verify stats
        self.assertIn('value_count', stats)
        self.assertIn('file_count', stats)
        self.assertIn('load_count', stats)
        self.assertIn('save_count', stats)
    
    def test_values_by_source(self):
        # Set values from different sources
        self.config_manager.set_value('memory1', 'value1', source='memory')
        self.config_manager.set_value('memory2', 'value2', source='memory')
        self.config_manager.set_value('file1', 'value3', source='file')
        
        # Get values by source
        memory_values = self.config_manager.get_values_by_source('memory')
        self.assertEqual(len(memory_values), 2)
        self.assertEqual(memory_values['memory1'], 'value1')
        self.assertEqual(memory_values['memory2'], 'value2')
        
        file_values = self.config_manager.get_values_by_source('file')
        self.assertEqual(len(file_values), 1)
        self.assertEqual(file_values['file1'], 'value3')
    
    def test_values_by_validation(self):
        # Set values with different validation rules
        self.config_manager.set_value(
            'string1',
            'hello',
            validation=self.validation_rules['string']
        )
        self.config_manager.set_value(
            'string2',
            'world',
            validation=self.validation_rules['string']
        )
        self.config_manager.set_value(
            'number1',
            42,
            validation=self.validation_rules['number']
        )
        
        # Get values by validation
        string_values = self.config_manager.get_values_by_validation(
            self.validation_rules['string']
        )
        self.assertEqual(len(string_values), 2)
        self.assertEqual(string_values['string1'], 'hello')
        self.assertEqual(string_values['string2'], 'world')
        
        number_values = self.config_manager.get_values_by_validation(
            self.validation_rules['number']
        )
        self.assertEqual(len(number_values), 1)
        self.assertEqual(number_values['number1'], 42)

@pytest.fixture
def config_manager():
    """Create a test configuration manager"""
    manager = ConfigManager(
        config_dir='test_config',
        default_format='json',
        reload_interval=1,
        validate_on_load=True,
        encryption_key='test_key',
        default_profile='test',
        default_environment='test'
    )
    yield manager
    
    # Cleanup
    if os.path.exists('test_config'):
        for root, dirs, files in os.walk('test_config', topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir('test_config')

def test_environment_variables(config_manager):
    """Test environment variable support"""
    # Set environment variable
    os.environ['CONFIG_TEST_VAR'] = 'test_value'
    
    # Reload environment variables
    config_manager._load_environment_variables()
    
    # Check value
    assert config_manager.get_value('test_var') == 'test_value'
    assert config_manager.get_value('test_var', environment='test') == 'test_value'
    assert config_manager.get_value('test_var', environment='prod') is None

def test_profiles(config_manager):
    """Test configuration profiles"""
    # Create profiles
    config_manager.create_profile('dev', 'Development profile')
    config_manager.create_profile('prod', 'Production profile', parent='dev')
    
    # Set values in profiles
    config_manager.set_value('test_key', 'dev_value', profile='dev')
    config_manager.set_value('test_key', 'prod_value', profile='prod')
    
    # Check values
    assert config_manager.get_value('test_key', profile='dev') == 'dev_value'
    assert config_manager.get_value('test_key', profile='prod') == 'prod_value'
    
    # Switch profile
    config_manager.switch_profile('prod')
    assert config_manager.get_value('test_key') == 'prod_value'

def test_validation(config_manager):
    """Test configuration validation"""
    # Create schema
    schema = {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'age': {'type': 'integer', 'minimum': 0}
        },
        'required': ['name', 'age']
    }
    
    # Save schema
    schema_dir = os.path.join('test_config', 'schemas')
    os.makedirs(schema_dir, exist_ok=True)
    with open(os.path.join(schema_dir, 'user.json'), 'w') as f:
        json.dump(schema, f)
    
    # Load schema
    config_manager._load_schemas()
    
    # Test validation
    valid_values = {'name': 'John', 'age': 30}
    invalid_values = {'name': 'John', 'age': -1}
    
    is_valid, errors = config_manager.validate_schema('user', valid_values)
    assert is_valid
    assert len(errors) == 0
    
    is_valid, errors = config_manager.validate_schema('user', invalid_values)
    assert not is_valid
    assert len(errors) > 0

def test_encryption(config_manager):
    """Test configuration encryption"""
    # Set encrypted value
    config_manager.set_value('secret', 'sensitive_data', encrypt=True)
    
    # Check value is encrypted
    value = config_manager.get_value('secret')
    assert value == 'sensitive_data'
    
    # Check raw value is encrypted
    with config_manager.values_lock:
        raw_value = config_manager.values['secret'].value
        assert raw_value != 'sensitive_data'
        assert isinstance(raw_value, str)

def test_backup_restore(config_manager):
    """Test configuration backup and restore"""
    # Set some values
    config_manager.set_value('key1', 'value1')
    config_manager.set_value('key2', 'value2')
    
    # Create backup
    config_manager.create_backup('test_backup')
    
    # Modify values
    config_manager.set_value('key1', 'new_value1')
    config_manager.set_value('key3', 'value3')
    
    # Restore backup
    config_manager.restore_backup('test_backup')
    
    # Check values
    assert config_manager.get_value('key1') == 'value1'
    assert config_manager.get_value('key2') == 'value2'
    assert config_manager.get_value('key3') is None
    
    # Check backups
    backups = config_manager.get_backups()
    assert len(backups) == 1
    assert backups[0]['name'] == 'test_backup'

def test_templates(config_manager):
    """Test configuration templates"""
    # Create template
    template = {
        'name': 'default_name',
        'age': 25,
        'settings': {
            'theme': 'light',
            'notifications': True
        }
    }
    
    config_manager.create_template('user', template, 'User configuration template')
    
    # Apply template
    values = {
        'name': 'John',
        'settings': {
            'theme': 'dark'
        }
    }
    
    config_manager.apply_template('user', values)
    
    # Check values
    assert config_manager.get_value('name') == 'John'
    assert config_manager.get_value('age') == 25
    assert config_manager.get_value('settings.theme') == 'dark'
    assert config_manager.get_value('settings.notifications') is True
    
    # Check templates
    templates = config_manager.get_templates()
    assert len(templates) == 1
    assert templates[0]['name'] == 'user'

def test_documentation(config_manager):
    """Test configuration documentation generation"""
    # Create profiles
    config_manager.create_profile('dev', 'Development profile')
    config_manager.create_profile('prod', 'Production profile')
    
    # Create template
    template = {
        'name': 'default_name',
        'age': 25
    }
    config_manager.create_template('user', template, 'User configuration template')
    
    # Create schema
    schema = {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'age': {'type': 'integer'}
        }
    }
    schema_dir = os.path.join('test_config', 'schemas')
    os.makedirs(schema_dir, exist_ok=True)
    with open(os.path.join(schema_dir, 'user.json'), 'w') as f:
        json.dump(schema, f)
    
    # Load schema
    config_manager._load_schemas()
    
    # Generate documentation
    config_manager.generate_docs('test_docs')
    
    # Check documentation
    assert os.path.exists('test_docs/README.md')
    with open('test_docs/README.md', 'r') as f:
        content = f.read()
        assert 'Configuration Documentation' in content
        assert 'Profiles' in content
        assert 'Templates' in content
        assert 'Schemas' in content

def test_diff(config_manager):
    """Test configuration diffing"""
    # Set initial values
    config_manager.set_value('key1', 'value1')
    config_manager.set_value('key2', 'value2')
    
    # Create new configuration
    new_config = {
        'key1': 'new_value1',
        'key3': 'value3'
    }
    
    # Get diff
    diff = config_manager.get_diff(new_config)
    
    # Check diff
    assert 'key1' in diff['modified']
    assert diff['modified']['key1']['old'] == 'value1'
    assert diff['modified']['key1']['new'] == 'new_value1'
    assert 'key3' in diff['added']
    assert 'key2' in diff['removed']

def test_statistics(config_manager):
    """Test configuration statistics"""
    # Perform some operations
    config_manager.set_value('key1', 'value1')
    config_manager.set_value('key2', 'value2', encrypt=True)
    config_manager.create_backup('test_backup')
    config_manager.create_profile('test_profile')
    
    # Get statistics
    stats = config_manager.get_stats()
    
    # Check statistics
    assert stats['value_count'] == 2
    assert stats['encryption_count'] == 1
    assert stats['backup_count'] == 1
    assert stats['profile_count'] == 1
    assert 'key1' in stats['values']
    assert 'key2' in stats['values']
    assert stats['values']['key2']['encrypted'] is True

if __name__ == '__main__':
    unittest.main() 