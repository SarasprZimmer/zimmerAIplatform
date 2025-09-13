import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@zimmerai.com')
        self.app_url = os.getenv('APP_URL', 'http://localhost:3001')
        
    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str) -> bool:
        """
        Send password reset email to user
        """
        try:
            # Create message
            subject = "بازنشانی رمز عبور - زیمر"
            
            reset_url = f"{self.app_url}/reset-password?token={reset_token}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html dir="rtl" lang="fa">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>بازنشانی رمز عبور</title>
                <style>
                    body {{ font-family: 'Tahoma', Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #3B82F6; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .button {{ display: inline-block; background-color: #3B82F6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>زیمر</h1>
                        <p>بازنشانی رمز عبور</p>
                    </div>
                    <div class="content">
                        <p>سلام {user_name}،</p>
                        <p>درخواست بازنشانی رمز عبور برای حساب کاربری شما دریافت شده است.</p>
                        <p>برای بازنشانی رمز عبور خود، روی دکمه زیر کلیک کنید:</p>
                        <div style="text-align: center;">
                            <a href="{reset_url}" class="button">بازنشانی رمز عبور</a>
                        </div>
                        <p>اگر شما این درخواست را نکرده‌اید، این ایمیل را نادیده بگیرید.</p>
                        <p>این لینک تا 30 دقیقه معتبر است.</p>
                        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                        <p><strong>لینک مستقیم:</strong></p>
                        <p><a href="{reset_url}">{reset_url}</a></p>
                    </div>
                    <div class="footer">
                        <p>این ایمیل از طرف سیستم زیمر ارسال شده است.</p>
                        <p>لطفاً به این ایمیل پاسخ ندهید.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            بازنشانی رمز عبور - زیمر
            
            سلام {user_name}،
            
            درخواست بازنشانی رمز عبور برای حساب کاربری شما دریافت شده است.
            
            برای بازنشانی رمز عبور خود، به این لینک مراجعه کنید:
            {reset_url}
            
            اگر شما این درخواست را نکرده‌اید، این ایمیل را نادیده بگیرید.
            این لینک تا 30 دقیقه معتبر است.
            
            با تشکر،
            تیم زیمر
            """
            
            return self._send_email(to_email, subject, html_content, text_content)
            
        except Exception as e:
            print(f"Error sending password reset email: {e}")
            return False
    
    def _send_email(self, to_email: str, subject: str, html_content: str, text_content: str) -> bool:
        """
        Send email using SMTP or fallback to console output
        """
        # If SMTP credentials are not configured, use console output
        if not self.smtp_username or not self.smtp_password:
            print("=" * 50)
            print("EMAIL NOTIFICATION (SMTP not configured)")
            print("=" * 50)
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print("=" * 50)
            print("HTML Content:")
            print(html_content)
            print("=" * 50)
            print("Text Content:")
            print(text_content)
            print("=" * 50)
            return True
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Attach parts
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"Password reset email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email via SMTP: {e}")
            # Fallback to console output
            return self._send_email(to_email, subject, html_content, text_content)

# Global email service instance
email_service = EmailService() 