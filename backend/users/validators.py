from django.core.exceptions import ValidationError
import re


def validate_username(value):
    if not re.match(r'^[\w.@+-]+\Z', value):
        raise ValidationError(
            'Недопустимое значение символов'
        )
