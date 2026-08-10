"""Shared reCAPTCHA test helpers — mock Google verify so tests stay offline."""

from unittest.mock import patch

from django_recaptcha.client import RecaptchaResponse

VALID_CAPTCHA_POST = {"g-recaptcha-response": "PASSED"}


def mock_recaptcha_valid():
    """Patch django_recaptcha.client.submit to always succeed."""
    return patch(
        "django_recaptcha.client.submit",
        return_value=RecaptchaResponse(is_valid=True),
    )


def mock_recaptcha_invalid():
    """Patch django_recaptcha.client.submit to always fail."""
    return patch(
        "django_recaptcha.client.submit",
        return_value=RecaptchaResponse(is_valid=False, error_codes=["invalid-input-response"]),
    )
