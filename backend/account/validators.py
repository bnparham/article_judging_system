import re
from django.core.exceptions import ValidationError


def is_persian_only(text):
    """
    Validates if the given text contains only Persian characters.

    Args:
        text (str): The input string to validate.

    Returns:
        bool: True if the text contains only Persian characters, False otherwise.
    """
    # Persian Unicode range: \u0600-\u06FF, and Persian-specific characters like \uFB8A-\uFB8C
    pattern = r'^[\u0600-\u06FF\uFB8A-\uFB8C\s]+$'
    if not re.fullmatch(pattern, text):
        raise ValidationError(message="تنها استفاده از حروف فارسی مجاز میباشد")


def validate_email_domain(value):
    allowed_domains = ["gmail.com", "ymail.com",
                       "outlook.com", "hotmail.com",
                       "icloud.com", "guilan.ac.ir"]  # Add your valid domains here
    domain = value.split('@')[-1]
    if domain not in allowed_domains:
        raise ValidationError(message=f"ایمیل باید از دامنه‌های معتبر باشد: {', '.join(allowed_domains)}")

def validate_iranian_mobile_number(value):
    if not re.match(r'^09\d{9}$', value):
        raise ValidationError("شماره موبایل باید یک شماره معتبر ایرانی باشد (مانند 09123456789).")
