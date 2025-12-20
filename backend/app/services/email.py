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
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.email_from
            msg["To"] = to_email

            html_part = MIMEText(html_content, "html")
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

    def generate_password_reset_token(self, user_id: int) -> str:
        """Generate a token for password reset (valid for 1 hour)"""
        from datetime import timedelta

        # Create a special token with password_reset type
        return create_access_token(
            user_id, expires_delta=timedelta(hours=1), token_type="password_reset"
        )

    def send_password_reset_email(
        self,
        to_email: str,
        user_name: Optional[str],
        reset_token: str,
        base_url: str = "http://localhost:5173",
    ) -> bool:
        """Send password reset email"""
        reset_link = f"{base_url}/reset-password?token={reset_token}"

        name = user_name or "Корисник"

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
                    <h2>Ресетирање на лозинка</h2>
                    <p>Здраво {name},</p>
                    <p>Добивме барање за ресетирање на вашата лозинка. Кликнете на копчето подолу за да поставите нова лозинка:</p>

                    <p style="text-align: center;">
                        <a href="{reset_link}" style="display: inline-block; background-color: #3b82f6; color: #ffffff !important; padding: 12px 30px; text-decoration: none; border-radius: 25px; margin: 20px 0; font-weight: bold;">Ресетирај лозинка</a>
                    </p>

                    <p>Или копирајте го овој линк во вашиот прелистувач:</p>
                    <p style="word-break: break-all; color: #3b82f6;">{reset_link}</p>

                    <p><strong>Овој линк важи само 1 час.</strong></p>

                    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">

                    <p style="color: #64748b; font-size: 14px;">
                        Ако не сте го побарале ова ресетирање, можете безбедно да ја игнорирате оваа порака. Вашата лозинка нема да биде променета.
                    </p>
                </div>
                <div class="footer">
                    <p>© 2025 e-Faktura. Сите права се задржани.</p>
                </div>
            </div>
        </body>
        </html>
        """

        subject = "Ресетирање на лозинка - e-Faktura"
        return self._send_email(to_email, subject, html_content)

    def send_password_changed_email(
        self,
        to_email: str,
        user_name: Optional[str],
    ) -> bool:
        """Send confirmation email after password was changed"""
        name = user_name or "Корисник"

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
                    <h2>Лозинката е променета</h2>
                    <p>Здраво {name},</p>
                    <p>Вашата лозинка беше успешно променета.</p>

                    <p>Ако не сте ја направиле оваа промена, ве молиме веднаш контактирајте не.</p>

                    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">

                    <p style="color: #64748b; font-size: 14px;">
                        За безбедносни причини, ви препорачуваме да користите уникатна лозинка за секоја сметка.
                    </p>
                </div>
                <div class="footer">
                    <p>© 2025 e-Faktura. Сите права се задржани.</p>
                </div>
            </div>
        </body>
        </html>
        """

        subject = "Лозинката е променета - e-Faktura"
        return self._send_email(to_email, subject, html_content)

    def send_verification_email(
        self,
        to_email: str,
        user_name: Optional[str],
        verification_token: str,
        base_url: str = "http://localhost:5173",
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

    def send_welcome_email(self, to_email: str, user_name: Optional[str]) -> bool:
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

    def send_organization_invitation_email(
        self,
        to_email: str,
        organization_name: str,
        inviter_name: Optional[str],
        role: str,
        invitation_code: str,
        base_url: str = "http://localhost:5173",
        user_exists: bool = False,
    ) -> bool:
        """Send organization invitation email.

        Args:
            to_email: Email address to send the invitation to.
            organization_name: Name of the organization the user is invited to.
            inviter_name: Name of the person who sent the invitation.
            role: Role the invited user will have in the organization.
            invitation_code: Unique code for the invitation.
            base_url: Base URL of the frontend application.
            user_exists: If True, sends to login page. If False, sends to register page.

        Returns:
            True if email was sent successfully, False otherwise.
        """
        # Link goes to the join page which handles all auth states
        join_url = f"/organization/join?code={invitation_code}"
        if user_exists:
            # User has account - send to login first, then join
            invitation_link = f"{base_url}/login?redirect={join_url}"
            alt_link = f"{base_url}/register?redirect={join_url}"
            alt_text = f'Немате сметка? <a href="{alt_link}" style="color: #3b82f6;">Регистрирајте се тука</a>'
        else:
            # User doesn't have account - send to register first, then join
            invitation_link = f"{base_url}/register?redirect={join_url}"
            alt_link = f"{base_url}/login?redirect={join_url}"
            alt_text = f'Веќе имате сметка? <a href="{alt_link}" style="color: #3b82f6;">Најавете се тука</a>'

        inviter = inviter_name or "Член на тимот"

        # Role translation
        role_translations = {
            "owner": "Сопственик",
            "admin": "Администратор",
            "accountant": "Сметководител",
            "member": "Член",
            "viewer": "Набљудувач",
        }
        role_mk = role_translations.get(role.lower(), role)

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
                .role-badge {{ display: inline-block; background-color: #e0e7ff; color: #4f46e5; padding: 4px 12px; border-radius: 15px; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>e-Faktura</h1>
                </div>
                <div class="content">
                    <h2>Поканети сте да се приклучите на организација</h2>
                    <p>Здраво,</p>
                    <p><strong>{inviter}</strong> ве покани да се приклучите на организацијата <strong>{organization_name}</strong> на e-Faktura.</p>

                    <p>Вашата улога: <span class="role-badge">{role_mk}</span></p>

                    <p style="text-align: center;">
                        <a href="{invitation_link}" style="display: inline-block; background-color: #3b82f6; color: #ffffff !important; padding: 12px 30px; text-decoration: none; border-radius: 25px; margin: 20px 0; font-weight: bold;">Прифати покана</a>
                    </p>

                    <p>Или копирајте го овој линк во вашиот прелистувач:</p>
                    <p style="word-break: break-all; color: #3b82f6;">{invitation_link}</p>

                    <p><strong>Оваа покана важи само 30 минути.</strong></p>

                    <p style="color: #64748b; font-size: 14px;">
                        {alt_text}
                    </p>

                    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">

                    <p style="color: #64748b; font-size: 14px;">
                        Ако не очекувавте оваа покана, можете безбедно да ја игнорирате оваа порака.
                    </p>
                </div>
                <div class="footer">
                    <p>© 2025 e-Faktura. Сите права се задржани.</p>
                </div>
            </div>
        </body>
        </html>
        """

        subject = f"Покана за приклучување на {organization_name} - e-Faktura"
        return self._send_email(to_email, subject, html_content)


# Singleton instance
email_service = EmailService()
