"""
Email Utility Module

This module handles secure email transmission using TLS and proper authentication.
It includes error handling and logging while maintaining security of sensitive data.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Optional

from .config import Config

logger = logging.getLogger(__name__)

class EmailError(Exception):
    """Custom exception for email-related errors."""
    pass

def send_email_with_attachment(
    to_email: str,
    subject: str,
    body: str,
    attachment_name: str,
    attachment_content: str,
    retry_count: int = 3
) -> bool:
    """
    Send an email with an attachment using secure TLS connection.
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        body (str): Email body text
        attachment_name (str): Name of the attachment file
        attachment_content (str): Content of the attachment
        retry_count (int, optional): Number of retry attempts. Defaults to 3.
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    
    Raises:
        EmailError: If there's an error in sending the email
    """
    if not all([Config.SMTP_SERVER, Config.SMTP_PORT, 
                Config.SMTP_SENDER_EMAIL, Config.SMTP_SENDER_PASSWORD]):
        raise EmailError("Email configuration is incomplete")

    # Create message
    msg = MIMEMultipart()
    msg['From'] = Config.SMTP_SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject

    # Add body
    msg.attach(MIMEText(body, 'plain'))

    # Add attachment
    attachment = MIMEApplication(attachment_content)
    attachment.add_header('Content-Disposition', 'attachment', 
                         filename=attachment_name)
    msg.attach(attachment)

    # Attempt to send email with retries
    for attempt in range(retry_count):
        try:
            # Create secure SSL/TLS connection
            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.starttls()
                server.login(Config.SMTP_SENDER_EMAIL, Config.SMTP_SENDER_PASSWORD)
                server.send_message(msg)
                logger.info(f"Email sent successfully to {to_email}")
                return True
                
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed")
            raise EmailError("Failed to authenticate with email server")
            
        except Exception as e:
            if attempt == retry_count - 1:
                logger.error(f"Failed to send email after {retry_count} attempts: {str(e)}")
                raise EmailError(f"Failed to send email: {str(e)}")
            logger.warning(f"Email attempt {attempt + 1} failed, retrying...")
    
    return False