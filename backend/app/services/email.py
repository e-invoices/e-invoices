import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.core.config import get_settings
from app.core.security import create_access_token

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailService:
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.email_from = settings.email_from

    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send an email using SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = to_email

            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_user and self.smtp_password:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.email_from, to_email, msg.as_string())

            logger.info("Email sent successfully to %s", to_email)
            return True
        except Exception as e:
            logger.error("Failed to send email to %s: %s", to_email, str(e))
            return False

    def generate_verification_token(self, user_id: int) -> str:
        """Generate a verification token for email verification"""
        from datetime import timedelta
        return create_access_token(user_id, expires_delta=timedelta(hours=24))

    def send_verification_email(
        self,
        to_email: str,
        user_name: Optional[str],
        verification_token: str,
        base_url: str = "http://localhost:5173"
    ) -> bool:
        """Send email verification email"""
        verification_link = f"{base_url}/verify-email?token={verification_token}"

        name = user_name or "User"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #3b82f6; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f8fafc; padding: 30px; border-radius: 0 0 8px 8px; }}
                .footer {{ text-align: center; color: #64748b; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>e-Faktura</h1>
                </div>
                <div class="content">
                    <h2>Добредојдовте, {name}!</h2>
                    <p>Ви благодариме што се регистриравте на e-Faktura. За да го завршите процесот на регистрација, ве молиме потврдете ја вашата е-пошта.</p>
                    
                    <p style="text-align: center;">
                        <a href="{verification_link}" style="display: inline-block; background-color: #3b82f6; color: #ffffff !important; padding: 12px 30px; text-decoration: none; border-radius: 25px; margin: 20px 0; font-weight: bold;">Потврди е-пошта</a>
                    </p>
                    
                    <p>Или копирајте го овој линк во вашиот прелистувач:</p>
                    <p style="word-break: break-all; color: #3b82f6;">{verification_link}</p>
                    
                    <p>Овој линк важи 24 часа.</p>
                    
                    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                    
                    <p style="color: #64748b; font-size: 14px;">
                        Ако не сте се регистрирале на e-Faktura, можете да ја игнорирате оваа порака.
                    </p>
                </div>
                <div class="footer">
                    <p>© 2025 e-Faktura. Сите права се задржани.</p>
                </div>
            </div>
        </body>
        </html>
        """

        subject = "Потврдете ја вашата е-пошта - e-Faktura"
        return self._send_email(to_email, subject, html_content)

    def send_welcome_email(
        self,
        to_email: str,
        user_name: Optional[str]
    ) -> bool:
        """Send welcome email after successful verification"""
        name = user_name or "User"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #3b82f6; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f8fafc; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block;color: #ffffff; background-color: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #64748b; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>e-Faktura</h1>
                </div>
                <div class="content">
                    <h2>Добредојдовте на e-Faktura, {name}!</h2>
                    <p>Вашата сметка е успешно активирана. Сега можете да започнете со користење на платформата за електронски фактури.</p>
                    
                    <p style="text-align: center;">
                        <a href="http://localhost:5173/app" class="button">Започни</a>
                    </p>
                    
                    <p>Со e-Faktura можете:</p>
                    <ul>
                        <li>Да креирате електронски фактури усогласени со УЈП</li>
                        <li>Автоматски да генерирате XML и XAdES потписи</li>
                        <li>Да управувате со вашите клиенти и фактури</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>© 2025 e-Faktura. Сите права се задржани.</p>
                </div>
            </div>
        </body>
        </html>
        """

        subject = "Добредојдовте на e-Faktura!"
        return self._send_email(to_email, subject, html_content)


# Singleton instance
email_service = EmailService()

