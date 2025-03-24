"""
Configuration Module

This module handles loading and validating environment variables for the application.
It uses python-dotenv for environment variable management and provides typed configuration
values with validation.
"""

import os
import secrets
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for managing environment variables with validation."""
    
    # Email Configuration
    SMTP_SERVER: str = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', '587'))
    SMTP_SENDER_EMAIL: str = os.getenv('SMTP_SENDER_EMAIL', '')
    SMTP_SENDER_PASSWORD: str = os.getenv('SMTP_SENDER_PASSWORD', '')
    
    # API Security
    SECRET_KEY: str = os.getenv('SECRET_KEY', secrets.token_hex(32))
    API_KEY: str = os.getenv('API_KEY', secrets.token_urlsafe(32))
    ALLOWED_ORIGINS: List[str] = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    MAX_CONTENT_LENGTH: int = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
    JWT_ACCESS_TOKEN_EXPIRES: int = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))  # 1 hour
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    
    # Security Headers
    SECURE_HEADERS = {
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'X-Content-Type-Options': 'nosniff',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'",
    }
    
    @classmethod
    def validate(cls) -> List[str]:
        """
        Validate the configuration settings.
        
        Returns:
            List[str]: List of validation errors, empty if all valid
        """
        errors = []
        
        # Validate email settings if email is configured
        if cls.SMTP_SENDER_EMAIL:
            if not cls.SMTP_SENDER_PASSWORD:
                errors.append("SMTP_SENDER_PASSWORD is required when SMTP_SENDER_EMAIL is set")
            if not cls.SMTP_SERVER:
                errors.append("SMTP_SERVER is required when SMTP_SENDER_EMAIL is set")
        
        # Validate security settings
        if len(cls.SECRET_KEY) < 32:
            errors.append("SECRET_KEY should be at least 32 characters long")
        
        # Validate JWT settings
        if len(cls.JWT_SECRET_KEY) < 32:
            errors.append("JWT_SECRET_KEY should be at least 32 characters long")
        
        # Validate rate limiting
        if cls.RATE_LIMIT_PER_MINUTE < 1:
            errors.append("RATE_LIMIT_PER_MINUTE must be greater than 0")
        
        return errors
