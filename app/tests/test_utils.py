from datetime import date

import pytest

from app.utils.helpers import calculate_age
from app.utils.validators import validate_gender, parse_date


def test_calculate_age():
    assert calculate_age(date(2000, 1, 1)) == 26  # до конца 2026 года


def test_validate_gender():
    assert validate_gender("M") == "M"
    with pytest.raises(ValueError):
        validate_gender("X")


def test_parse_date():
    assert parse_date("1990-01-01") == date(1990, 1, 1)
    with pytest.raises(ValueError):
        parse_date("01-01-1990")
