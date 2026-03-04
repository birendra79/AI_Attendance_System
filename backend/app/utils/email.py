import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ..config import settings


def send_confirmation_email(to_email: str, username: str, token: str):
    """Send an admin signup confirmation email."""
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        print(f"[EMAIL SKIPPED] No SMTP creds set. Confirmation link: "
              f"{settings.FRONTEND_URL}/frontend-admin/confirm.html?token={token}")
        return

    confirm_url = f"{settings.FRONTEND_URL}/frontend-admin/confirm.html?token={token}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Confirm your AI Attendance Admin account"
    msg["From"] = settings.EMAIL_FROM or settings.SMTP_USERNAME
    msg["To"] = to_email

    html_body = f"""
    <html>
    <body style="font-family:Inter,sans-serif;background:#f8f9fa;padding:40px">
      <div style="max-width:500px;margin:auto;background:#fff;border-radius:12px;padding:32px;box-shadow:0 4px 6px rgba(0,0,0,.1)">
        <h2 style="color:#0d6efd">AI Attendance System</h2>
        <p>Hello <strong>{username}</strong>,</p>
        <p>Thank you for signing up as an admin. Please confirm your email address by clicking the button below:</p>
        <a href="{confirm_url}"
           style="display:inline-block;background:#0d6efd;color:#fff;text-decoration:none;padding:12px 24px;border-radius:8px;font-weight:600;margin:16px 0">
          Confirm Email
        </a>
        <p style="color:#6c757d;font-size:.85rem">If you did not sign up, simply ignore this email.</p>
      </div>
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(msg["From"], to_email, msg.as_string())


def send_username_email(to_email: str, username: str):
    """Send admin their username via email."""
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        print(f"[EMAIL SKIPPED] No SMTP creds set. Username for {to_email}: {username}")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your AI Attendance Admin Username"
    msg["From"] = settings.EMAIL_FROM or settings.SMTP_USERNAME
    msg["To"] = to_email

    html_body = f"""
    <html>
    <body style="font-family:Inter,sans-serif;background:#f8f9fa;padding:40px">
      <div style="max-width:500px;margin:auto;background:#fff;border-radius:12px;padding:32px;box-shadow:0 4px 6px rgba(0,0,0,.1)">
        <h2 style="color:#0d6efd">AI Attendance System</h2>
        <p>You requested your username. Here it is:</p>
        <p style="font-size:1.4rem;font-weight:700;color:#0d6efd;letter-spacing:1px">{username}</p>
        <p style="color:#6c757d;font-size:.85rem">If you did not request this, you can ignore this email.</p>
      </div>
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(msg["From"], to_email, msg.as_string())


def send_password_reset_email(to_email: str, username: str, token: str):
    """Send admin a password reset link."""
    reset_url = f"{settings.FRONTEND_URL}/frontend-admin/reset-password.html?token={token}"

    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        print(f"[EMAIL SKIPPED] No SMTP creds set. Password reset link for {username}: {reset_url}")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Reset your AI Attendance Admin password"
    msg["From"] = settings.EMAIL_FROM or settings.SMTP_USERNAME
    msg["To"] = to_email

    html_body = f"""
    <html>
    <body style="font-family:Inter,sans-serif;background:#f8f9fa;padding:40px">
      <div style="max-width:500px;margin:auto;background:#fff;border-radius:12px;padding:32px;box-shadow:0 4px 6px rgba(0,0,0,.1)">
        <h2 style="color:#0d6efd">AI Attendance System</h2>
        <p>Hello <strong>{username}</strong>,</p>
        <p>We received a request to reset your password. Click the button below (valid for 30 minutes):</p>
        <a href="{reset_url}"
           style="display:inline-block;background:#0d6efd;color:#fff;text-decoration:none;padding:12px 24px;border-radius:8px;font-weight:600;margin:16px 0">
          Reset Password
        </a>
        <p style="color:#6c757d;font-size:.85rem">If you did not request this, you can safely ignore this email.</p>
      </div>
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(msg["From"], to_email, msg.as_string())
