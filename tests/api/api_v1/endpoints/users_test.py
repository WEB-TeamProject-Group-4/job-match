from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest
from app.db.models import DbUsers
from app.schemas.user import UserCreate
from src.app.main import app


client = TestClient(app)


def  create_user():
    return DbUsers(
            username='TestUser',
            password='TestPassword',
            email='test.email@email.com',
            type='admin'
        )

@pytest.mark.asyncio
def test_create_user_admin_success(mocker):
    mocker.patch('app.api.api_v1.endpoints.users.create_user', return_value=create_user())
    new_user = {
        'username':'TestUser',
        'password':'TestPassword',
        'email':'test.email@email.com'
    }
    response = client.post('/users', json=new_user)
    data = response.json()

    assert response.status_code == 200
    assert data['type'] == 'admin'
    assert data['username'] == 'TestUser'


@pytest.mark.asyncio
def test_create_user_admin_missingBody(mocker):
    mocker.patch('app.api.api_v1.endpoints.users.create_user', return_value=create_user())
    response = client.post('/users')
    data = response.json()

    assert response.status_code == 422
    assert data['detail'][0]['loc'] == ['body']


@pytest.mark.asyncio
def test_create_user_admin_missingEmail(mocker):
    mocker.patch('app.api.api_v1.endpoints.users.create_user', return_value=create_user())
    new_user = {
        'username':'TestUser',
        'password':'TestPassword'
    }
    response = client.post('/users', json=new_user)
    data = response.json()

    assert response.status_code == 422
    assert data['detail'][0]['loc'] == ['body', 'email']


@pytest.mark.asyncio
def test_create_user_admin_missingUsername(mocker):
    mocker.patch('app.api.api_v1.endpoints.users.create_user', return_value=create_user())
    new_user = {
        'password':'TestPassword',
        'email':'test.email@email.com'
    }
    response = client.post('/users', json=new_user)
    data = response.json()

    assert response.status_code == 422
    assert data['detail'][0]['loc'] == ['body', 'username']


@pytest.mark.asyncio
def test_create_user_admin_missingPassword(mocker):
    mocker.patch('app.api.api_v1.endpoints.users.create_user', return_value=create_user())
    new_user = {
        'username':'TestUser',
        'email':'test.email@email.com'
    }
    response = client.post('/users', json=new_user)
    data = response.json()

    assert response.status_code == 422
    assert data['detail'][0]['loc'] == ['body', 'password']


@pytest.mark.asyncio
def test_create_user_admin_invalidEmail(mocker):
    mocker.patch('app.api.api_v1.endpoints.users.create_user', return_value=create_user())
    new_user = {
        'username':'TestUser',
        'password':'TestPassword',
        'email':'test.emailemail.com'
    }
    response = client.post('/users', json=new_user)
    data = response.json()

    assert response.status_code == 422
    assert data['detail'][0]['loc'] == ['body', 'email']



@pytest.mark.asyncio
async def test_get_users_notAuthenticated():
    response = client.get('/users')
    data = response.json()

    assert response.status_code == 401
    assert data['detail'] == 'Not authenticated'


@pytest.mark.asyncio
async def test_get_users_success(db, mocker):
    mocker.patch.object(db, 'query', return_value=[])
    mocker.patch('app.core.auth.get_current_user', return_value=create_user())
    response = client.get('/users', headers={"Authorization": "Bearer valid_token_here"})
    data = response.json()

    assert response.status_code == 401
    assert data['detail'] == 'Not authenticated'