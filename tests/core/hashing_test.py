import pytest
from fastapi import HTTPException
from jwt import PyJWTError
from app.core.hashing import Hash, very_token
from app.db.models import DbUsers


def test_hash():
    password = "dummy_password"

    hashed_password = Hash.bcrypt(password)

    assert Hash.verify(hashed_password, password) is True
    assert Hash.verify(hashed_password, 'fake_pass') is False


@pytest.mark.asyncio
async def test_very_token_success(db, mocker, test_db):
    mocker.patch('app.core.hashing.jwt.decode', return_value={"id": 'test_id', "username": "test_username"})

    mock_user = DbUsers(
        id='test_id',
        username='test_username',
        password='test_password',
        email='dummyEmail',
        type='test_type'
    )

    db.add(mock_user)
    db.commit()

    result = await very_token('dummy_token', db)

    assert result.id == 'test_id'


@pytest.mark.asyncio
async def test_very_token_raises_error(db, mocker):
    mocker.patch('app.core.hashing.jwt.decode', side_effect=PyJWTError(""),)

    with pytest.raises(HTTPException) as exception:
        result = await very_token('dummy_token', db)

    exception_info = exception.value
    assert exception_info.status_code == 401
    assert exception_info.detail == 'Invalid token'
    assert exception_info.headers == {'WWW-Authenticate': 'Bearer'}
