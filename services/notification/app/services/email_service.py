from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

template_dir = Path(__file__).parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(template_dir))


async def send_email(to_email: str, subject: str, template_name: str, context: dict):
    """Send email using mock (print to console) with HTML template."""
    try:
        template = jinja_env.get_template(template_name)
        html_content = template.render(**context)

        # Mock email - print to console
        print("\n" + "="*80)
        print("📧 MOCK EMAIL")
        print("="*80)
        print(f"From: {settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print("-"*80)
        print("Content:")
        print(html_content)
        print("="*80 + "\n")

        logger.info(f"Mock email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send mock email to {to_email}: {e}")
        return False


async def send_welcome_email(email: str, user_id: int):
    """Send welcome email after registration."""
    context = {"user_id": user_id}
    return await send_email(
        to_email=email,
        subject="Welcome to GameKeys Store!",
        template_name="welcome.html",
        context=context
    )


async def send_order_confirmation(email: str, order_id: int, total_amount: float):
    """Send order confirmation email."""
    context = {"order_id": order_id, "total_amount": total_amount}
    return await send_email(
        to_email=email,
        subject=f"Order #{order_id} Confirmation",
        template_name="order_created.html",
        context=context
    )


async def send_payment_confirmation(email: str, order_id: int, keys: list):
    """Send payment confirmation with game keys."""
    context = {"order_id": order_id, "keys": keys}
    return await send_email(
        to_email=email,
        subject=f"Your Game Keys - Order #{order_id}",
        template_name="order_paid.html",
        context=context
    )


async def send_order_failed(email: str, order_id: int, reason: str):
    """Send order failure notification."""
    context = {"order_id": order_id, "reason": reason}
    return await send_email(
        to_email=email,
        subject=f"Order #{order_id} Failed",
        template_name="order_failed.html",
        context=context
    )