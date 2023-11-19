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


@pytest.mark.asyncio
async def test_login(client: TestClient, db, mocker, test_db):
    mocker.patch('app.api.api_v1.endpoints.login.Hash.verify', return_value=True)
    mocker.patch('app.api.api_v1.endpoints.login.create_access_token', return_value='valid_token')

    response = client.post('/login', data=user)
    assert response.status_code == 404

    db.add(db_user)
    db.commit()

    response = client.post('/login', data=user)
    assert response.status_code == 200

    mocker.patch('app.api.api_v1.endpoints.login.Hash.verify', return_value=False)
    response = client.post('/login', data=user)
    assert response.status_code == 404
