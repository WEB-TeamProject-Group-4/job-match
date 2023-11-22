import jwt
import pytest
from app.db.models import DbAds, DbInfo, DbProfessionals, DbUsers
from fastapi.testclient import TestClient
from app.core.security import SECRET_KEY
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


def create_professional() -> ProfessionalCreateDisplay:
    return ProfessionalCreateDisplay(username='TestUser', first_name='Professional', last_name='Lastname')


def test_create_professional_success(client: TestClient, test_db, mocker):
    mocker.patch('app.api.api_v1.endpoints.users.create_user', return_value=create_professional())
    mocker.patch('app.crud.crud_user.send_email')

    new_professional = {
        "username": "TestUser",
        "password": "Test123",
        "email": "test/prof@example.com",
        "first_name": "Professional",
        "last_name": "Lastname"
    }
    response = client.post('/professionals', json=new_professional)
    data = response.json()

    assert response.status_code == 200
    assert data['username'] == 'TestUser'
    assert data['first_name'] == 'Professional'
    assert data['last_name'] == 'Lastname'


@pytest.mark.parametrize(
    "test_input, expected_loc",
    [
        ({"password": "Test123", "email": "test/prof@example.com", "first_name": "Professional",
          "last_name": "Lastname"}, ['body', 'username']),
        ({"username": "TestUser", "email": "test/prof@example.com", "first_name": "Professional",
          "last_name": "Lastname"}, ['body', 'password']),
        ({"username": "TestUser", "password": "Test123", "first_name": "Professional", "last_name": "Lastname"},
         ['body', 'email']),
        ({"username": "TestUser", "password": "Test123", "email": "test/prof@example.com", "last_name": "Lastname"},
         ['body', 'first_name']),
        (
                {"username": "TestUser", "password": "Test123", "email": "test/prof@example.com",
                 "first_name": "Professional"},
                ['body', 'last_name']),
        ([], ['body']),
    ]
)
def test_create_professional_missing_fields(client: TestClient, test_db, mocker, test_input, expected_loc):
    mocker.patch('app.api.api_v1.endpoints.users.create_user', return_value=create_professional())

    response = client.post('/professionals', json=test_input)
    data = response.json()

    assert response.status_code == 422
    assert data['detail'][0]['loc'] == expected_loc


@pytest.mark.asyncio
async def test_get_professional_not_authenticated(client: TestClient):
    response = client.get('/professionals')
    data = response.json()

    assert response.status_code == 401
    assert data['detail'] == 'Not authenticated'


def test_get_professionals_success(client: TestClient, test_db, db, mocker):
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

    professional_data_list = [
        {'id': 'professional-id-one', 'first_name': 'Prof1', 'last_name': 'Last1', 'user_id': 'test-id-one'},
        {'id': 'professional-id-two', 'first_name': 'Prof2', 'last_name': 'Last2', 'user_id': 'test-id-two'},
        {'id': 'professional-id-three', 'first_name': 'Prof3', 'last_name': 'Last3', 'user_id': 'test-id-three'}

    ]

    for professional_data in professional_data_list:
        professional = DbProfessionals(**professional_data)
        db.add(professional)

    db.commit()
    # mocker.patch('app.crud.crud_professional.is_user_verified', return_value=create_user())
    mocker.patch('app.core.auth.get_user_by_username')

    response = client.get('/professionals', headers={"Authorization": f"Bearer {get_valid_token()}"})
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_all_resumes(client: TestClient, test_db, db, mocker):
    mocker.patch('app.core.auth.get_user_by_username')
    user_data = {'id': 'test-id-one',
                "username": "User3",
                "email": "test3@example.com",
                "password": "password123",
                'type': 'professional', 'is_verified': 1}
    
    user = DbUsers(**user_data)
    db.add(user)

    professional_data = {'id': 'professional-id-one', 'first_name': 'Prof1', 'last_name': 'Last1', 'user_id': 'test-id-one', 'info_id': "test-info-id"}
    professional = DbProfessionals(**professional_data)
    db.add(professional)

    info_data = {'id': 'test-info-id', 'description': 'test-description', 'location': 'Test Location'}
    info = DbInfo(**info_data)
    db.add(info)

    ad_data_list = [
        {'id': 'test-id-1', 'description': 'resume description-1', 'location': 'Test Location', 'status': 'test-status', 'min_salary': 1000, 'max_salary': 2000, 'info_id': 'test-info-id'},
        {'id': 'test-id-2', 'description': 'resume description-2', 'location': 'Test Location', 'status': 'test-status', 'min_salary': 1000, 'max_salary': 2000, 'info_id': 'test-info-id'},
        {'id': 'test-id-3', 'description': 'resume description-3', 'location': 'Test Location', 'status': 'test-status', 'min_salary': 1000, 'max_salary': 2000, 'info_id': 'test-info-id'}
               ]
    
    for add_data in ad_data_list:
        ad = DbAds(**add_data)
        db.add(ad)

    db.commit()

    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.get('/professionals/resumes', headers={"Authorization": f"Bearer {get_valid_token()}"})
    data = response.json()

    assert response.status_code == 200
    assert data == [
        {'id': 'test-id-1', 'description': 'resume description-1', 'location': 'Test Location', 'status': 'test-status', 'min_salary': 1000, 'max_salary': 2000},
        {'id': 'test-id-2', 'description': 'resume description-2', 'location': 'Test Location', 'status': 'test-status', 'min_salary': 1000, 'max_salary': 2000},
        {'id': 'test-id-3', 'description': 'resume description-3', 'location': 'Test Location', 'status': 'test-status', 'min_salary': 1000, 'max_salary': 2000}
               ]


@pytest.mark.asyncio
async def test_get_professional_info(client: TestClient, test_db, db, mocker):
    mocker.patch('app.core.auth.get_user_by_username')
    user_data = {'id': 'test-id-one', "username": "User3", "email": "test3@example.com", "password": "password123",
                'type': 'professional', 'is_verified': 1}
    
    user = DbUsers(**user_data)
    db.add(user)

    professional_data = {'id': 'professional-id-one', 'first_name': 'Prof1', 'last_name': 'Last1', 'status':'active', 'user_id': 'test-id-one', 'info_id': "test-info-id"}
    professional = DbProfessionals(**professional_data)
    db.add(professional)

    info_data = {'id': 'test-info-id', 'description': 'test-description', 'location': 'Test Location'}
    info = DbInfo(**info_data)
    db.add(info)

    db.commit()

    mocker.patch('app.core.auth.get_user_by_username', return_value=user)
    mocker.patch('app.crud.crud_professional.get_resumes')

    response = client.get('/professionals/info', headers={"Authorization": f"Bearer {get_valid_token()}"})
    data = response.json()

    assert response.status_code == 200
    assert data == {
        "first_name": "Prof1",
        "last_name": "Last1",
        "summary": "test-description",
        "location": "Test Location",
        "status": "active",
        "picture": None,
        "active_resumes": 0
    }


@pytest.mark.asyncio
async def test_edit_professional_info_success(client: TestClient, test_db, db, mocker):
    mocker.patch('app.core.auth.get_user_by_username')

    user_data = {'id': 'test-id-one', "username": "User3", "email": "test3@example.com", "password": "password123",
                'type': 'professional', 'is_verified': 1}
    
    user = DbUsers(**user_data)
    db.add(user)

    professional_data = {'id': 'professional-id-one', 'first_name': 'Prof1', 'last_name': 'Last1', 'status':'active', 'user_id': 'test-id-one', 'info_id': "test-info-id"}
    professional = DbProfessionals(**professional_data)
    db.add(professional)

    info_data = {'id': 'test-info-id', 'description': 'test-description', 'location': 'Test Location 1'}
    info = DbInfo(**info_data)
    db.add(info)
    
    db.commit()

    mocker.patch('app.core.auth.get_user_by_username', return_value=user)
    mocker.patch('app.crud.crud_professional.get_professional')


    response = client.post('/professionals/info', headers={"Authorization": f"Bearer {get_valid_token()}"}, params={'location': 'Test Location 2'})
    data = response.json()

    assert response.status_code == 201
    changed: DbInfo = (db.query(DbInfo).filter(DbInfo.id == 'test-info-id').first())

    assert 'Test Location 2' == changed.location
