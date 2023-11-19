import pytest
from fastapi.testclient import TestClient
from app.db.models import DbUsers

user = {'username': 'dummyUsername',
        'password': 'dummyPassword'}

db_user = DbUsers(
    username='dummyUsername',
    password='dummyPassword',
    email='dummy@email.com',
    type='admin'
)


def test_login(client: TestClient, test_db, db, mocker):
    mocker.patch('app.api.api_v1.endpoints.login.Hash.verify', return_value=True)
    mocker.patch('app.api.api_v1.endpoints.login.create_access_token', return_value='valid_token')

    response = client.post('/login', data=user)
    assert response.status_code == 401
    assert response.json().get('detail') == 'Invalid username'

    db.add(db_user)
    db.commit()

    response = client.post('/login', data=user)
    assert response.status_code == 200
    assert response.json() == {
        'access_token': 'valid_token',
        'token_type': 'bearer',
        'user_id': db_user.id,
        'username': db_user.username
    }

    mocker.patch('app.api.api_v1.endpoints.login.Hash.verify', return_value=False)
    response = client.post('/login', data=user)
    assert response.status_code == 401
    assert response.json().get('detail') == 'Incorrect password'
