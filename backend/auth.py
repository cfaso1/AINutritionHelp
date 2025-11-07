"""
Authentication and authorization middleware for production use
"""
import jwt
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages JWT-based authentication"""

    def __init__(self, secret_key: str, token_expiry_hours: int = 24):
        self.secret_key = secret_key
        self.token_expiry_hours = token_expiry_hours
        self.algorithm = 'HS256'

    def generate_token(self, user_id: int, username: str, email: str) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow()
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def get_token_from_request(self) -> Optional[str]:
        """Extract token from Authorization header"""
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        # Expected format: "Bearer <token>"
        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None

        return parts[1]

    def require_auth(self, f: Callable) -> Callable:
        """Decorator to require authentication for endpoints"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = self.get_token_from_request()

            if not token:
                return jsonify({
                    'error': 'Missing authentication token',
                    'message': 'Please provide a valid token in the Authorization header'
                }), 401

            payload = self.verify_token(token)

            if not payload:
                return jsonify({
                    'error': 'Invalid or expired token',
                    'message': 'Please log in again'
                }), 401

            # Attach user info to request context
            request.user_id = payload['user_id']
            request.username = payload['username']
            request.email = payload['email']

            return f(*args, **kwargs)

        return decorated_function

    def optional_auth(self, f: Callable) -> Callable:
        """Decorator for endpoints that work with or without authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = self.get_token_from_request()

            if token:
                payload = self.verify_token(token)
                if payload:
                    request.user_id = payload['user_id']
                    request.username = payload['username']
                    request.email = payload['email']
                else:
                    request.user_id = None
            else:
                request.user_id = None

            return f(*args, **kwargs)

        return decorated_function


def get_current_user_id() -> Optional[int]:
    """Get current authenticated user ID from request context"""
    return getattr(request, 'user_id', None)
