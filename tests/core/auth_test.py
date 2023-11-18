import jwt
import pytest
from fastapi import HTTPException

from app.core.auth import get_user_by_username, get_current_user
from app.db.models import DbUsers


dummy_user = DbUsers(
    id='test_id',
    username='test_username',
    password='test_password',
    type='test_type'
)
dummy_token = "dummy_token"


def test_get_username_success(db, mocker):
    mock_query = mocker.MagicMock()
    mock_query.filter.return_value.first.return_value = dummy_user
    mocker.patch.object(db, 'query', return_value=mock_query)

    result = get_user_by_username(db, 'test_username')

    assert result.username == 'test_username'
    assert result == dummy_user


def test_get_user_by_username_not_found(db, mocker):
    mock_query = mocker.MagicMock()
    mock_query.filter.return_value.first.return_value = None
    mocker.patch.object(db, 'query', return_value=mock_query)

    with pytest.raises(HTTPException) as ecx_info:
        get_user_by_username(db, "nonexistent_user")

    assert ecx_info.value.status_code == 404
    assert ecx_info.value.detail == 'User with username nonexistent_user not found!'


def test_get_current_user_returns_correct_user(db, mocker):
    mocker.patch('jwt.decode', return_value={'username': 'test_username'})

    mocker.patch('app.core.auth.get_user_by_username',return_value=dummy_user)

    user = get_current_user(dummy_token, db)

    assert user.username == 'test_username'
    assert user == dummy_user


def test_get_current_user_invalid_token(db, mocker):
    mocker.patch('jwt.decode', side_effect=jwt.DecodeError)

    with pytest.raises(HTTPException) as ecx_info:
        get_current_user(dummy_token, db)

    assert ecx_info.value.status_code == 401
    assert ecx_info.value.detail == 'Could not validate credentials'
    assert ecx_info.value.headers == {'WWW-Authenticate': 'Bearer'}


def test_get_current_user_no_username(db, mocker):
    mocker.patch('jwt.decode', return_value={})

    with pytest.raises(HTTPException) as ecx_info:
        get_current_user(dummy_token, db)

    assert ecx_info.value.status_code == 401
    assert ecx_info.value.detail == 'Could not validate credentials'
    assert ecx_info.value.headers == {'WWW-Authenticate': 'Bearer'}


def test_get_current_user_return_no_user(db, mocker):
    mocker.patch('jwt.decode', return_value={'username': 'nonexistent_user'})

    mocker.patch('app.core.auth.get_user_by_username',return_value=None)

    with pytest.raises(HTTPException) as ecx_info:
        get_current_user(dummy_token, db)

    assert ecx_info.value.status_code == 401
    assert ecx_info.value.detail == 'Could not validate credentials'
    assert ecx_info.value.headers == {'WWW-Authenticate': 'Bearer'}
