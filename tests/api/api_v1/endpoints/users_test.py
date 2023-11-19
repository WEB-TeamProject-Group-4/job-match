import pytest
from app.db.models import DbUsers
from fastapi.testclient import TestClient


def create_user():
    return DbUsers(
        username='TestUser',
        password='TestPassword',
        email='test.email@email.com',
        type='admin'
    )


def test_create_user_admin_success(client: TestClient, mocker):
    mocker.patch('app.api.api_v1.endpoints.users.create_user', return_value=create_user())
    new_user = {
        'username': 'TestUser',
        'password': 'TestPassword',
        'email': 'test.email@email.com'
    }
    response = client.post('/users', json=new_user)
    data = response.json()

    assert response.status_code == 200
    assert data['type'] == 'admin'
    assert data['username'] == 'TestUser'


def test_create_user_admin_missingBody(client: TestClient, mocker):
    mocker.patch('app.api.api_v1.endpoints.users.create_user', return_value=create_user())
    response = client.post('/users')
    data = response.json()

    assert response.status_code == 422
    assert data['detail'][0]['loc'] == ['body']


def test_create_user_admin_missingEmail(client: TestClient, mocker):
    mocker.patch('app.api.api_v1.endpoints.users.create_user', return_value=create_user())
    new_user = {
        'username': 'TestUser',
        'password': 'TestPassword'
    }
    response = client.post('/users', json=new_user)
    data = response.json()

    assert response.status_code == 422
    assert data['detail'][0]['loc'] == ['body', 'email']


def test_create_user_admin_missingUsername(client: TestClient, mocker):
    mocker.patch('app.api.api_v1.endpoints.users.create_user', return_value=create_user())
    new_user = {
        'password': 'TestPassword',
        'email': 'test.email@email.com'
    }
    response = client.post('/users', json=new_user)
    data = response.json()

    assert response.status_code == 422
    assert data['detail'][0]['loc'] == ['body', 'username']


def test_create_user_admin_missingPassword(client: TestClient, mocker):
    mocker.patch('app.api.api_v1.endpoints.users.create_user', return_value=create_user())
    new_user = {
        'username': 'TestUser',
        'email': 'test.email@email.com'
    }
    response = client.post('/users', json=new_user)
    data = response.json()

    assert response.status_code == 422
    assert data['detail'][0]['loc'] == ['body', 'password']


def test_create_user_admin_invalidEmail(client: TestClient, mocker):
    mocker.patch('app.api.api_v1.endpoints.users.create_user', return_value=create_user())
    new_user = {
        'username': 'TestUser',
        'password': 'TestPassword',
        'email': 'test.emailemail.com'
    }
    response = client.post('/users', json=new_user)
    data = response.json()

    assert response.status_code == 422
    assert data['detail'][0]['loc'] == ['body', 'email']


@pytest.mark.asyncio
async def test_get_users_notAuthenticated(client: TestClient):
    response = client.get('/users')
    data = response.json()

    assert response.status_code == 401
    assert data['detail'] == 'Not authenticated'


@pytest.mark.asyncio
async def test_get_users_success(client: TestClient, mocker):
    mocker.patch('app.core.auth.get_current_user', return_value=create_user())
    response = client.get('/users', headers={"Authorization": "Bearer valid_token_here"})
    data = response.json()

    assert response.status_code == 401
    assert data['detail'] == 'Could not validate credentials'
