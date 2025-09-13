import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import List, Optional

def send_email(to: str, subject: str, html: str) -> bool:
    """
    Simple email sending function for local development
    In production, this would use a real SMTP server
    """
    # For local development, just print to console
    print("=" * 60)
    print(f"[EMAIL] To: {to}")
    print(f"[EMAIL] Subject: {subject}")
    print(f"[EMAIL] Body:")
    print(html)
    print("=" * 60)
    
    # If SMTP is configured, try to send real email
    smtp_host = os.getenv("SMTP_HOST")
    if smtp_host:
        try:
            return send_email_smtp(to, subject, html)
        except Exception as e:
            print(f"SMTP Error: {e}")
            print("Falling back to console output")
    
    return True

def send_email_smtp(to: str, subject: str, html: str) -> bool:
    """
    Send email via SMTP (for production)
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM")
    
    if not all([smtp_host, smtp_user, smtp_password, smtp_from]):
        print("SMTP configuration incomplete, using console output")
        return send_email(to, subject, html)
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_from
        msg['To'] = to
        
        # Add HTML content
        html_part = MIMEText(html, 'html')
        msg.attach(html_part)
        
        # Send email
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        
        print(f"Email sent successfully to {to}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Async version for compatibility with FastAPI
async def send_email_async(to: List[str], subject: str, body: str, html_body: Optional[str] = None) -> bool:
    """
    Async email sending function for FastAPI compatibility
    """
    # Convert list to string for compatibility
    to_str = to[0] if isinstance(to, list) else to
    html = html_body or body
    
    return send_email(to_str, subject, html)