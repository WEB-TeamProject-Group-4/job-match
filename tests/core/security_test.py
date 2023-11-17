import pytest
import src.app.core.security as sec
from datetime import datetime, UTC, timedelta
import jwt

test_data = {"username": "test_user"}
test_expiry_delta = 3
test_secret_key: str = sec.EMAIL_KEY


def test_create_access_token_default():
    result = sec.create_access_token(test_data)
    encoded = jwt.decode(result, sec.SECRET_KEY, algorithms=['HS256'])

    expected_exp = datetime.now(UTC) + timedelta(minutes=30)
    expected_exp_timestamp = expected_exp.timestamp()

    assert encoded["username"] == "test_user"
    assert encoded["exp"] == pytest.approx(expected_exp_timestamp)


def test_create_access_token():
    result = sec.create_access_token(test_data, test_expiry_delta, test_secret_key)
    encoded = jwt.decode(result, sec.EMAIL_KEY, algorithms=['HS256'])

    expected_exp = datetime.now(UTC) + timedelta(minutes=3)
    expected_exp_timestamp = expected_exp.timestamp()

    assert encoded["username"] == "test_user"
    assert encoded["exp"] == pytest.approx(expected_exp_timestamp)
