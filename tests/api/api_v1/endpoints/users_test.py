import jwt
import pytest
from app.db.models import DbUsers
from fastapi.testclient import TestClient
from app.core.security import SECRET_KEY


def create_user():
    return DbUsers(
        username='TestUser',
        password='TestPassword',
        email='test.email@email.com',
        type='admin'
    )


def get_valid_token():
    return jwt.encode({'username': 'TestUser'}, SECRET_KEY, algorithm='HS256')


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


@pytest.mark.parametrize(
    'test_input, expected_loc',
    [
        ({"password": "TestPassword", "email": "test.email@email.com"}, ['body', 'username']),
        ({"username": "TestUser", "email": "test.email@email.com"}, ['body', 'password']),
        ({"username": "TestUser", "password": "TestPassword"}, ['body', 'email']),
        ([], ['body'])
    ]
)
def test_create_user_admin_missing_fields(client: TestClient, test_db, mocker, test_input, expected_loc):
    mocker.patch('app.api.api_v1.endpoints.users.create_user', return_value=create_user())

    response = client.post('/users', json=test_input)
    data = response.json()

    assert response.status_code == 422
    assert data['detail'][0]['loc'] == expected_loc


@pytest.mark.asyncio
async def test_get_users_not_authenticated(client: TestClient):
    response = client.get('/users')
    data = response.json()

    assert response.status_code == 401
    assert data['detail'] == 'Not authenticated'


def test_get_users_success(client: TestClient, test_db, db, mocker):
    user_data_list = [
        {'id': 'test-id-one', "username": "User1", "email": "test1@example.com", "password": "password123",
         'type': 'admin', 'is_verified': 0},  # this should not be counted, is_verified == 0
        {'id': 'test-id-two', "username": "User2", "email": "test2@example.com", "password": "password123",
         'type': 'company', 'is_verified': 1},
        {'id': 'test-id-three', "username": "User3", "email": "test3@example.com", "password": "password123",
         'type': 'professional', 'is_verified': 1}

    ]

    for user_data in user_data_list:
        user = DbUsers(**user_data)
        db.add(user)

    db.commit()
    mocker.patch('app.core.auth.get_user_by_username', return_value=create_user())

    response = client.get('/users', headers={"Authorization": f"Bearer {get_valid_token()}"})
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
