"""
Security Module

This module provides security features for the API including:
- JWT token generation and validation
- Request authentication
- API key validation
- Rate limiting
- Input sanitization
"""

from functools import wraps
from datetime import datetime, timedelta
import secrets
import logging
from typing import Optional, Dict, Any, Callable

import jwt
from flask import request, jsonify, current_app, Response
from werkzeug.security import generate_password_hash, check_password_hash

from .config import Config

logger = logging.getLogger(__name__)

def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)

def create_jwt_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token with the given data and expiration.
    
    Args:
        data (Dict[str, Any]): Data to encode in the token
        expires_delta (Optional[timedelta]): Token expiration time
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, Config.SECRET_KEY, algorithm="HS256")

def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify a JWT token and return its payload.
    
    Args:
        token (str): JWT token to verify
        
    Returns:
        Dict[str, Any]: Token payload if valid
        
    Raises:
        jwt.InvalidTokenError: If token is invalid
    """
    return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])

def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize input data to prevent injection attacks.
    
    Args:
        data (Dict[str, Any]): Input data to sanitize
        
    Returns:
        Dict[str, Any]: Sanitized data
    """
    if not isinstance(data, dict):
        return data

    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Remove any potential script tags
            value = value.replace('<script>', '').replace('</script>', '')
            # Escape HTML characters
            value = value.replace('<', '&lt;').replace('>', '&gt;')
        elif isinstance(value, dict):
            value = sanitize_input(value)
        elif isinstance(value, list):
            value = [sanitize_input(item) if isinstance(item, dict) else item 
                    for item in value]
        sanitized[key] = value
    return sanitized

def require_api_key(f: Callable) -> Callable:
    """
    Decorator to require API key authentication.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key is missing'}), 401
        
        # TODO: Implement API key validation against database
        # For now, using a simple check
        if api_key != Config.API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
            
        return f(*args, **kwargs)
    return decorated

def validate_content_length(f: Callable) -> Callable:
    """
    Decorator to validate request content length.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        content_length = request.content_length
        if content_length and content_length > Config.MAX_CONTENT_LENGTH:
            return jsonify({
                'error': 'Request too large',
                'max_size': Config.MAX_CONTENT_LENGTH
            }), 413
        return f(*args, **kwargs)
    return decorated

def add_security_headers(response: Response) -> Response:
    """
    Add security headers to response.
    
    Args:
        response (Response): Flask response object
        
    Returns:
        Response: Response with security headers
    """
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
