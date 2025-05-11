import logging
import jwt
import bcrypt
import secrets
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import hashlib
import re
from dataclasses import dataclass
from .metrics import SecurityMetrics

logger = logging.getLogger(__name__)

@dataclass
class SecurityContext:
    """Security context information"""
    user_id: str
    roles: List[str]
    permissions: List[str]
    ip_address: str
    user_agent: str
    timestamp: datetime
    session_id: str
    token_id: str
    additional_info: Optional[Dict[str, Any]] = None

class SecurityManager:
    """Advanced security management system"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.token_blacklist: Dict[str, datetime] = {}
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.max_failed_attempts = 5
        self.lockout_duration = 300  # 5 minutes
        self.token_expiry = 3600  # 1 hour
        self.refresh_token_expiry = 604800  # 7 days
        self.password_policy = {
            'min_length': 12,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_digits': True,
            'require_special': True,
            'max_age_days': 90
        }
        
    def generate_token(
        self,
        user_id: str,
        roles: List[str],
        permissions: List[str],
        context: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Generate JWT token and refresh token"""
        try:
            # Generate token ID
            token_id = secrets.token_hex(16)
            
            # Create token payload
            payload = {
                'user_id': user_id,
                'roles': roles,
                'permissions': permissions,
                'token_id': token_id,
                'exp': int(time.time()) + self.token_expiry,
                'iat': int(time.time())
            }
            
            # Generate access token
            access_token = jwt.encode(
                payload,
                self.secret_key,
                algorithm='HS256'
            )
            
            # Generate refresh token
            refresh_payload = {
                'user_id': user_id,
                'token_id': token_id,
                'exp': int(time.time()) + self.refresh_token_expiry,
                'iat': int(time.time())
            }
            
            refresh_token = jwt.encode(
                refresh_payload,
                self.secret_key,
                algorithm='HS256'
            )
            
            # Update metrics
            SecurityMetrics.update_api_usage(1, 'token_generation')
            
            return access_token, refresh_token
            
        except Exception as e:
            logger.error("Error generating token", exc_info=True)
            raise SecurityError("Token generation failed")
    
    def verify_token(
        self,
        token: str,
        context: Dict[str, Any]
    ) -> SecurityContext:
        """Verify JWT token and return security context"""
        try:
            # Check if token is blacklisted
            if token in self.token_blacklist:
                raise SecurityError("Token has been revoked")
            
            # Decode token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=['HS256']
            )
            
            # Create security context
            security_context = SecurityContext(
                user_id=payload['user_id'],
                roles=payload['roles'],
                permissions=payload['permissions'],
                ip_address=context.get('ip_address', ''),
                user_agent=context.get('user_agent', ''),
                timestamp=datetime.utcnow(),
                session_id=context.get('session_id', ''),
                token_id=payload['token_id']
            )
            
            # Update metrics
            SecurityMetrics.update_api_usage(1, 'token_verification')
            
            return security_context
            
        except jwt.ExpiredSignatureError:
            raise SecurityError("Token has expired")
        except jwt.InvalidTokenError:
            raise SecurityError("Invalid token")
        except Exception as e:
            logger.error("Error verifying token", exc_info=True)
            raise SecurityError("Token verification failed")
    
    def refresh_token(
        self,
        refresh_token: str,
        context: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Generate new access token using refresh token"""
        try:
            # Verify refresh token
            payload = jwt.decode(
                refresh_token,
                self.secret_key,
                algorithms=['HS256']
            )
            
            # Get user information
            user_id = payload['user_id']
            token_id = payload['token_id']
            
            # Generate new tokens
            return self.generate_token(
                user_id,
                [],  # Roles will be fetched from database
                [],  # Permissions will be fetched from database
                context
            )
            
        except jwt.ExpiredSignatureError:
            raise SecurityError("Refresh token has expired")
        except jwt.InvalidTokenError:
            raise SecurityError("Invalid refresh token")
        except Exception as e:
            logger.error("Error refreshing token", exc_info=True)
            raise SecurityError("Token refresh failed")
    
    def revoke_token(self, token: str):
        """Revoke a token by adding it to blacklist"""
        try:
            # Decode token to get expiration
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=['HS256']
            )
            
            # Add to blacklist
            self.token_blacklist[token] = datetime.fromtimestamp(
                payload['exp']
            )
            
            # Update metrics
            SecurityMetrics.update_api_usage(1, 'token_revocation')
            
        except Exception as e:
            logger.error("Error revoking token", exc_info=True)
            raise SecurityError("Token revocation failed")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        try:
            # Generate salt
            salt = bcrypt.gensalt()
            
            # Hash password
            hashed = bcrypt.hashpw(
                password.encode('utf-8'),
                salt
            )
            
            return hashed.decode('utf-8')
            
        except Exception as e:
            logger.error("Error hashing password", exc_info=True)
            raise SecurityError("Password hashing failed")
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed.encode('utf-8')
            )
        except Exception as e:
            logger.error("Error verifying password", exc_info=True)
            raise SecurityError("Password verification failed")
    
    def validate_password(self, password: str) -> bool:
        """Validate password against policy"""
        try:
            # Check length
            if len(password) < self.password_policy['min_length']:
                return False
            
            # Check uppercase
            if self.password_policy['require_uppercase'] and not re.search(
                r'[A-Z]',
                password
            ):
                return False
            
            # Check lowercase
            if self.password_policy['require_lowercase'] and not re.search(
                r'[a-z]',
                password
            ):
                return False
            
            # Check digits
            if self.password_policy['require_digits'] and not re.search(
                r'\d',
                password
            ):
                return False
            
            # Check special characters
            if self.password_policy['require_special'] and not re.search(
                r'[!@#$%^&*(),.?":{}|<>]',
                password
            ):
                return False
            
            return True
            
        except Exception as e:
            logger.error("Error validating password", exc_info=True)
            raise SecurityError("Password validation failed")
    
    def check_failed_attempts(self, user_id: str) -> bool:
        """Check if user is locked out due to failed attempts"""
        try:
            if user_id not in self.failed_attempts:
                return False
            
            # Get failed attempts
            attempts = self.failed_attempts[user_id]
            
            # Remove old attempts
            current_time = datetime.utcnow()
            attempts = [
                attempt for attempt in attempts
                if current_time - attempt < timedelta(seconds=self.lockout_duration)
            ]
            
            # Update attempts
            self.failed_attempts[user_id] = attempts
            
            # Check if locked out
            return len(attempts) >= self.max_failed_attempts
            
        except Exception as e:
            logger.error("Error checking failed attempts", exc_info=True)
            raise SecurityError("Failed attempts check failed")
    
    def record_failed_attempt(self, user_id: str):
        """Record a failed login attempt"""
        try:
            if user_id not in self.failed_attempts:
                self.failed_attempts[user_id] = []
            
            self.failed_attempts[user_id].append(datetime.utcnow())
            
            # Update metrics
            SecurityMetrics.update_failed_logins(1, user_id)
            
        except Exception as e:
            logger.error("Error recording failed attempt", exc_info=True)
            raise SecurityError("Failed attempt recording failed")
    
    def clear_failed_attempts(self, user_id: str):
        """Clear failed attempts for user"""
        try:
            if user_id in self.failed_attempts:
                del self.failed_attempts[user_id]
        except Exception as e:
            logger.error("Error clearing failed attempts", exc_info=True)
            raise SecurityError("Failed attempts clearing failed")
    
    def check_permission(
        self,
        security_context: SecurityContext,
        required_permission: str
    ) -> bool:
        """Check if user has required permission"""
        try:
            return required_permission in security_context.permissions
        except Exception as e:
            logger.error("Error checking permission", exc_info=True)
            raise SecurityError("Permission check failed")
    
    def check_role(
        self,
        security_context: SecurityContext,
        required_role: str
    ) -> bool:
        """Check if user has required role"""
        try:
            return required_role in security_context.roles
        except Exception as e:
            logger.error("Error checking role", exc_info=True)
            raise SecurityError("Role check failed")
    
    def sanitize_input(self, input_str: str) -> str:
        """Sanitize user input"""
        try:
            # Remove potentially dangerous characters
            sanitized = re.sub(r'[<>]', '', input_str)
            
            # Update metrics
            SecurityMetrics.update_suspicious_activities(
                1 if sanitized != input_str else 0,
                'input_sanitization'
            )
            
            return sanitized
            
        except Exception as e:
            logger.error("Error sanitizing input", exc_info=True)
            raise SecurityError("Input sanitization failed")
    
    def validate_session(self, session_id: str) -> bool:
        """Validate session ID"""
        try:
            # Implement session validation logic
            return True
        except Exception as e:
            logger.error("Error validating session", exc_info=True)
            raise SecurityError("Session validation failed")
    
    def generate_session_id(self) -> str:
        """Generate secure session ID"""
        try:
            return secrets.token_hex(32)
        except Exception as e:
            logger.error("Error generating session ID", exc_info=True)
            raise SecurityError("Session ID generation failed")
    
    def hash_session_id(self, session_id: str) -> str:
        """Hash session ID for storage"""
        try:
            return hashlib.sha256(
                session_id.encode('utf-8')
            ).hexdigest()
        except Exception as e:
            logger.error("Error hashing session ID", exc_info=True)
            raise SecurityError("Session ID hashing failed")

class SecurityError(Exception):
    """Security-related error"""
    pass 