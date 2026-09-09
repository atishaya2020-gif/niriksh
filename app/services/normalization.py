import math
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

NULL_VALUES = {"nan", "none", "nat", "null", "na", "<na>"}
SCIENTIFIC_NUMBER = re.compile(r"^[+]?(?:\d+(?:\.\d*)?|\.\d+)[eE][+-]?\d+$")
PLAIN_NUMBER = re.compile(r"^[+]?\d+(?:\.\d+)?$")
PHONE_FORMATTING = re.compile(r"[+\s().-]")


def clean_text(value):
    if value is None:
        return None
    value = str(value).strip()
    return value if value and value.lower() not in NULL_VALUES else None


def canonicalize_identifier(value):
    value = clean_text(value)
    if not value:
        return None

    value = re.sub(r"\s+", "", value)
    if value.isdigit():
        return value

    if SCIENTIFIC_NUMBER.fullmatch(value) or PLAIN_NUMBER.fullmatch(value):
        try:
            decimal_value = Decimal(value)
        except InvalidOperation:
            return None
        if not decimal_value.is_finite():
            return None
        return format(decimal_value, "f")

    return value.upper()


def canonicalize_integer_identifier(value):
    canonical = canonicalize_identifier(value)
    return canonical if canonical and canonical.isdigit() else None


def normalize_phone(value):
    raw_value = clean_text(value)
    if not raw_value:
        return None

    compact_value = re.sub(r"\s+", "", raw_value)
    if SCIENTIFIC_NUMBER.fullmatch(compact_value):
        digits = canonicalize_integer_identifier(compact_value)
    else:
        digits = PHONE_FORMATTING.sub("", raw_value)
        if not digits.isdigit():
            return None

    if not digits:
        return None
    if len(digits) == 10:
        return digits
    if len(digits) == 11 and digits.startswith("0"):
        return digits[1:]
    if len(digits) == 12 and digits.startswith("91"):
        return digits[2:]
    if len(digits) == 14 and digits.startswith("0091"):
        return digits[4:]
    return None


def normalize_name(value):
    value = clean_text(value)
    return re.sub(r"\s+", " ", value).strip().title() if value else None


def normalize_identifier(value):
    return canonicalize_identifier(value)


def parse_datetime(value):
    value = clean_text(value)
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        for fmt in ("%m/%d/%Y %H:%M", "%m/%d/%Y %H:%M:%S"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                pass
    return None


def finite_number(value):
    try:
        f = float(value)
        return f if math.isfinite(f) else None
    except (TypeError, ValueError):
        return None
