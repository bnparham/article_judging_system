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
