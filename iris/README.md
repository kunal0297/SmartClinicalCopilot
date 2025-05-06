# SmartClinicalCopilot IRIS Configuration 🏥

Configuration and setup for InterSystems IRIS for Health integration with SmartClinicalCopilot.

## 🔧 Prerequisites

- InterSystems IRIS for Health 2023.1 or later
- Windows 10/11 or Linux
- 8GB RAM minimum
- 20GB free disk space

## 🚀 Quick Start

1. **Install IRIS for Health**
   - Download from [InterSystems WRC](https://wrc.intersystems.com)
   - Run the installer
   - Choose "HealthShare" installation type

2. **Configure IRIS**
   ```bash
   # Start IRIS
   iris start

   # Access Management Portal
   http://localhost:52773/csp/sys/UtilHome.csp
   ```

3. **Set Up FHIR Server**
   - Navigate to System Administration > Security > Users
   - Create user: `SuperUser` with password: `AeQV@17463`
   - Enable FHIR server in System Administration > Configuration > FHIR

4. **Verify Installation**
   ```bash
   # Test FHIR endpoint
   curl -u SuperUser:AeQV@17463 http://localhost:52773/csp/healthshare/fhir/r4/metadata
   ```

## 📊 FHIR Configuration

### 1. Server Settings
```json
{
  "fhir": {
    "baseUrl": "http://localhost:52773/csp/healthshare/fhir/r4",
    "version": "R4",
    "timeout": 30,
    "retryAttempts": 3
  }
}
```

### 2. Security Settings
```json
{
  "security": {
    "authentication": "Basic",
    "username": "SuperUser",
    "password": "AeQV@17463",
    "ssl": false
  }
}
```

### 3. Resource Settings
```json
{
  "resources": {
    "Patient": {
      "enabled": true,
      "versioning": "versioned"
    },
    "Observation": {
      "enabled": true,
      "versioning": "versioned"
    },
    "MedicationRequest": {
      "enabled": true,
      "versioning": "versioned"
    },
    "Condition": {
      "enabled": true,
      "versioning": "versioned"
    }
  }
}
```

## 🔐 Security Configuration

1. **User Management**
   - Create application-specific users
   - Set appropriate permissions
   - Enable audit logging

2. **SSL/TLS**
   - Generate certificates
   - Configure SSL/TLS
   - Enable HTTPS

3. **API Security**
   - Enable CORS
   - Set rate limits
   - Configure IP restrictions

## 📈 Performance Tuning

1. **Cache Settings**
   ```json
   {
     "cache": {
       "enabled": true,
       "size": "1GB",
       "ttl": 300
     }
   }
   ```

2. **Connection Pool**
   ```json
   {
     "connections": {
       "max": 100,
       "min": 10,
       "timeout": 30
     }
   }
   ```

3. **Query Optimization**
   - Enable query caching
   - Set appropriate indices
   - Configure query timeout

## 🧪 Testing

1. **Health Check**
   ```bash
   curl -u SuperUser:AeQV@17463 http://localhost:52773/csp/healthshare/fhir/r4/metadata
   ```

2. **Patient Test**
   ```bash
   curl -u SuperUser:AeQV@17463 http://localhost:52773/csp/healthshare/fhir/r4/Patient/example
   ```

3. **Observation Test**
   ```bash
   curl -u SuperUser:AeQV@17463 http://localhost:52773/csp/healthshare/fhir/r4/Observation?patient=example
   ```

## 🔍 Monitoring

1. **System Metrics**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network traffic

2. **Application Metrics**
   - Request rate
   - Response time
   - Error rate
   - Cache hit rate

3. **Logging**
   - Access logs
   - Error logs
   - Audit logs
   - Performance logs

## 🐛 Troubleshooting

1. **Connection Issues**
   - Check IRIS service status
   - Verify network connectivity
   - Check firewall settings

2. **Performance Issues**
   - Monitor system resources
   - Check query performance
   - Review cache settings

3. **Security Issues**
   - Verify user permissions
   - Check SSL/TLS configuration
   - Review audit logs

## 📝 License

This project is licensed under the MIT License.
