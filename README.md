# Smart Clinical Copilot - Configuration Management System

A modern, secure, and feature-rich configuration management system designed for healthcare applications. This system provides a comprehensive solution for managing application configurations with advanced features like encryption, validation, templates, and more.

## Features

### Core Features
- **Configuration Editor**: Intuitive interface for managing configuration settings
- **Security**: Built-in encryption and access control mechanisms
- **Templates**: Reusable configuration templates with variable support
- **Validation**: Rule-based configuration validation
- **Import/Export**: Support for importing and exporting configurations
- **History**: Track changes and maintain configuration history
- **Statistics**: Monitor configuration usage and performance

### Advanced Features
- **Encryption**: Secure storage of sensitive configuration values
- **Access Control**: Role-based access control for configurations
- **Validation Rules**: Customizable validation rules for configuration values
- **Templates**: Variable-based templates for quick configuration deployment
- **Backup/Restore**: Automatic backup and restore functionality
- **Audit Logging**: Comprehensive audit trail of configuration changes
- **Performance Monitoring**: Real-time performance metrics and statistics

### Self-Healing System
- Automatic error detection and recovery
- Pattern-based error handling
- Service health monitoring
- Resource usage tracking
- Metrics collection and analysis
- Prometheus integration
- Redis-based metrics storage

## Architecture

The system is built using a modern tech stack:

### Frontend
- React with TypeScript
- Material-UI for the component library
- Monaco Editor for code editing
- Recharts for data visualization

### Backend
- Python with FastAPI
- Redis for caching
- Prometheus for metrics
- SQLAlchemy for database operations

## Getting Started

### Prerequisites
- Node.js 16+
- Python 3.8+
- Redis
- PostgreSQL

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/smart-clinical-copilot.git
cd smart-clinical-copilot
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

3. Install backend dependencies:
```bash
cd ../backend
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start the development servers:

Frontend:
```bash
cd frontend
npm start
```

Backend:
```bash
cd backend
uvicorn main:app --reload
```

## Usage

### Configuration Management

1. **Creating a Configuration**
   - Click "New Configuration" in the main interface
   - Fill in the required fields
   - Save the configuration

2. **Using Templates**
   - Access the Templates section
   - Choose a template
   - Fill in the variables
   - Apply the template

3. **Security**
   - Access the Security section
   - Configure encryption settings
   - Manage access control rules

4. **Validation**
   - Set up validation rules
   - Run validation on configurations
   - View validation results

### Best Practices

1. **Security**
   - Always encrypt sensitive values
   - Use strong access control rules
   - Regularly rotate encryption keys
   - Monitor access logs

2. **Performance**
   - Use caching for frequently accessed configurations
   - Implement rate limiting
   - Monitor system metrics
   - Optimize database queries

3. **Maintenance**
   - Regular backups
   - Clean up old configurations
   - Update validation rules
   - Monitor system health

## API Documentation

The API documentation is available at `/docs` when running the backend server. It provides detailed information about all available endpoints, request/response formats, and authentication requirements.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team.

## Acknowledgments

- Material-UI for the component library
- Monaco Editor for the code editor
- FastAPI for the backend framework
- Redis for caching
- Prometheus for metrics

## System Architecture

### Backend Components
1. **Error Handler**
   - Pattern-based error recognition
   - Automatic recovery strategies
   - Detailed error logging
   - Metrics collection
   - User-friendly error responses

2. **Recovery Strategies**
   - Service restart
   - Database reconnection
   - Memory cleanup
   - Configuration reload
   - Permission checks
   - Security alerts

3. **Health Monitor**
   - System metrics tracking
   - Service health checks
   - Error rate monitoring
   - Resource usage monitoring
   - Prometheus metrics

4. **Configuration Management**
   - YAML-based configuration
   - Runtime configuration reloading
   - Service-specific settings
   - Resource thresholds
   - Alerting configuration

## Configuration

### Self-Healing Configuration
The system is configured through `config/self_healing_config.yaml`:

```yaml
monitoring:
  system_metrics_interval: 60
  service_health_interval: 30
  error_rates_interval: 60

recovery:
  max_retries: 3
  initial_retry_delay: 1.0
  max_retry_delay: 30.0

resources:
  cpu:
    warning_threshold: 70
    critical_threshold: 85
```

### Error Patterns
Error patterns are defined in `config/error_patterns.yaml`:

```yaml
DatabaseError:
  action: check_services
  severity: high
  description: "Database error"
  auto_fix: true
  retry_count: 3
  retry_delay: 2
  recovery_strategy: "reconnect_db"
```

## API Endpoints

### Health Monitoring
- `GET /health` - Get system health status
- `GET /metrics` - Get error metrics
- `POST /recover/{error_type}` - Trigger manual recovery
- `GET /config` - Get current configuration
- `POST /config/reload` - Reload configuration

## Monitoring

### Prometheus Metrics
- `self_healing_errors_total` - Total errors by type
- `self_healing_recoveries_total` - Recovery attempts
- `self_healing_recovery_duration_seconds` - Recovery time
- `self_healing_system_health` - System health metrics

### Redis Metrics
- Error counts by type
- Recovery success rates
- System health history
- Service status

## Error Recovery

The system implements various recovery strategies:

1. **Service Recovery**
   - Automatic service restart
   - Health check verification
   - Connection pool management

2. **Resource Recovery**
   - Memory cleanup
   - Disk space management
   - Connection pool optimization

3. **Data Recovery**
   - Database reconnection
   - Transaction rollback
   - Data validation

4. **Security Recovery**
   - Permission checks
   - IP blocking
   - Security alerts

## Development

### Project Structure
```
SmartClinicalCopilot/
├── backend/
│   ├── error_handler.py
│   ├── recovery_strategies.py
│   ├── monitoring/
│   │   └── health_monitor.py
│   └── self_healing.py
├── config/
│   ├── error_patterns.yaml
│   └── self_healing_config.yaml
└── frontend/
    └── src/
```

### Adding New Recovery Strategies
1. Add strategy to `RecoveryStrategies` class
2. Update error patterns in `error_patterns.yaml`
3. Configure strategy in `self_healing_config.yaml`

