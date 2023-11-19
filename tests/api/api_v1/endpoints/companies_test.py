import jwt
import pytest
from app.db.models import DbCompanies, DbProfessionals, DbUsers
from fastapi.testclient import TestClient
from app.core.security import SECRET_KEY
from app.schemas.company import CompanyCreateDisplay
from app.schemas.professional import ProfessionalCreateDisplay


def create_user():
    return DbUsers(
        username='TestUser',
        password='TestPassword',
        email='test.email@email.com',
        type='admin'
    )


def get_valid_token():
    return jwt.encode({'username': 'TestUser'}, SECRET_KEY, algorithm='HS256')


def create_company() -> CompanyCreateDisplay:
    return CompanyCreateDisplay(
        username='TestCOmpany',
        name='Company Name'
    )


def test_create_company_success(client: TestClient, test_db, db, mocker):
    mocker.patch('app.api.api_v1.endpoints.users.create_user', return_value=create_company())
    mocker.patch('app.crud.crud_user.send_email')


    new_company = {
        "username": "TestCompany",
        "password": "Test123",
        "email": "test.company@example.com",
        "name": "Test Company"
    }
    response = client.post('/companies', json=new_company)
    data = response.json()

    assert response.status_code == 200
    assert data['username'] == 'TestCompany'
    assert data['name'] == 'Test Company'


@pytest.mark.parametrize(
    "test_input, expected_loc",
    [   
        ({"password": "Test123", "email": "test.company@example.com", "name": "Test Company"}, ['body', 'username']),
        ({"username": "TestCompany", "email": "test.company@example.com", "name": "Test Company"}, ['body', 'password']),
        ({"username": "TestCompany", "password": "Test123", "name": "Test Company"}, ['body', 'email']),
        ({"username": "TestCompany", "password": "Test123", "email": "test.company@example.com"}, ['body', 'name']),
        ([], ['body']),
    ]
)
def test_create_company_missing_fields(client: TestClient, test_db, mocker, test_input, expected_loc):
    mocker.patch('app.api.api_v1.endpoints.users.create_user', return_value=create_company())

    response = client.post('/companies', json=test_input)
    data = response.json()

    assert response.status_code == 422
    assert data['detail'][0]['loc'] == expected_loc


@pytest.mark.asyncio
async def test_get_companies_not_authenticated(client: TestClient):
    response = client.get('/companies')
    data = response.json()

    assert response.status_code == 401
    assert data['detail'] == 'Not authenticated'


def test_get_companies_success(client: TestClient, test_db, db, mocker):
    user_data_list = [
        {'id': 'test-id-one', "username": "User1", "email": "test1@example.com", "password": "password123", 'type': 'admin', 'is_verified': 0}, # this should not be counted, is_verified == 0
        {'id': 'test-id-two', "username": "User2", "email": "test2@example.com", "password": "password123", 'type': 'company', 'is_verified': 1},
        {'id': 'test-id-three', "username": "User3", "email": "test3@example.com", "password": "password123", 'type': 'professional', 'is_verified': 1}

    ]

    for user_data in user_data_list:
        user = DbUsers(**user_data)
        db.add(user)

    company_data_list = [
        {'id': 'company-id-one', 'name': 'Company One', 'user_id': 'test-id-one'},
        {'id': 'company-id-two', 'name': 'Company Two', 'user_id': 'test-id-two'},
        {'id': 'company-id-three', 'name': 'Company Threes', 'user_id': 'test-id-three'}

    ]

    for company_data in company_data_list:
        company = DbCompanies(**company_data)
        db.add(company)

    db.commit()
    mocker.patch('app.core.auth.get_user_by_username', return_value=create_user())

    response = client.get('/companies', headers={"Authorization": f"Bearer {get_valid_token()}"})
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2