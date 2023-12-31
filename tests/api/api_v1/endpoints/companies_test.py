import jwt
import pytest

from fastapi.testclient import TestClient

from app.db.models import DbCompanies, DbUsers, DbInfo, DbProfessionals, DbAds, DbJobsMatches
from app.core.security import SECRET_KEY
from app.schemas.company import CompanyCreateDisplay
from tests.crud.crud_company_test import fill_match_db


def create_user():
    return DbUsers(
        username='dummyUserId',
        password='dummyPassword',
        email='dummy@email.com',
        type='admin'
    )


def get_valid_token():
    return jwt.encode({'username': 'dummyUserId'}, SECRET_KEY, algorithm='HS256')


def create_company() -> CompanyCreateDisplay:
    return CompanyCreateDisplay(
        username='TestCOmpany',
        name='Company Name'
    )


async def fill_test_db(db):
    user = DbUsers(id='dummyUserId', username='dummyUsername', password='dummyPassword', email='dummy@email.com',
                   type='company', is_verified=True)
    db.add(user)
    company = DbCompanies(id='dummyCompanyId', name='dummyName', user_id=user.id)
    db.add(company)
    db.commit()

    return user, company


async def create_info() -> DbInfo:
    info = DbInfo(
        id='dummyInfoId',
        description='dummyDescription',
        location='dummyLocation'
    )
    return info


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

    assert response.status_code == 201
    assert data['username'] == 'TestCompany'
    assert data['name'] == 'Test Company'


@pytest.mark.parametrize(
    "test_input, expected_loc",
    [
        ({"password": "Test123", "email": "test.company@example.com", "name": "Test Company"}, ['body', 'username']),
        (
                {"username": "TestCompany", "email": "test.company@example.com", "name": "Test Company"},
                ['body', 'password']),
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


def test_get_companies_success(client: TestClient, test_db, db, mocker):
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

    company_data_list = [
        {'id': 'company-id-one', 'name': 'Company One', 'user_id': 'test-id-one'},
        {'id': 'company-id-two', 'name': 'Company Two', 'user_id': 'test-id-two'},
        {'id': 'company-id-three', 'name': 'Company Threes', 'user_id': 'test-id-three'}

    ]

    for company_data in company_data_list:
        company = DbCompanies(**company_data)
        db.add(company)

    db.commit()

    response = client.get('/companies')
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_company_by_id(client: TestClient, test_db, db, mocker):
    user, company = await fill_test_db(db)
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.get(f'/companies/{company.id}', headers={"Authorization": f"Bearer {get_valid_token()}"})

    assert response.status_code == 200
    assert response.json().get('name') == company.name

    # Test with company that does not exist

    response = client.get(f'/companies/dummyNonexistentCompany',
                          headers={"Authorization": f"Bearer {get_valid_token()}"})

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_company(client: TestClient, test_db, db, mocker):
    user, company = await fill_test_db(db)
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.patch(f'/companies/',
                            headers={"Authorization": f"Bearer {get_valid_token()}"})

    assert response.status_code == 200
    assert response.json().get('name') == company.name

    # Test with unverified user
    user.is_verified = False
    db.commit()

    response = client.patch(f'/companies/',
                            headers={"Authorization": f"Bearer {get_valid_token()}"})

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_company(client: TestClient, db, test_db, mocker):
    user, company = await fill_test_db(db)
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.delete(f'/companies/dummyCompanyId', headers={"Authorization": f"Bearer {get_valid_token()}"})

    assert response.status_code == 204
    assert company.is_deleted == True


@pytest.mark.asyncio
async def test_create_company_info(client: TestClient, db, test_db, mocker):
    user, company = await fill_test_db(db)
    schema = {
        'description': 'dummyDescription',
        'location': 'dummyLocation'
    }
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.post('/companies/info', headers={"Authorization": f"Bearer {get_valid_token()}"},
                           json=schema)

    assert response.status_code == 201
    assert response.json().get('description') == 'dummyDescription'

    # Testing with unverified user
    user.is_verified = False
    db.commit()

    response = client.post('/companies/info', headers={"Authorization": f"Bearer {get_valid_token()}"},
                           json=schema)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_company_info(client: TestClient, db, test_db, mocker):
    user, company = await fill_test_db(db)
    info = await create_info()
    company.info_id = info.id
    db.add(info)
    db.commit()
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.get('/companies/info/', headers={"Authorization": f"Bearer {get_valid_token()}"})

    assert response.status_code == 200
    assert response.json().get('description') == info.description

    # Testing with unverified user
    user.is_verified = False
    db.commit()

    response = client.get('/companies/info/', headers={"Authorization": f"Bearer {get_valid_token()}"})

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_info(client: TestClient, db, test_db, mocker):
    user, company = await fill_test_db(db)
    info = await create_info()
    company.info_id = info.id
    db.add(info)
    db.commit()
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.patch('/companies/info', headers={"Authorization": f"Bearer {get_valid_token()}"},
                            params={'description': 'newDescription'})

    assert response.status_code == 200
    assert response.json().get('description') == 'newDescription'
    assert response.json().get('location') == info.location

    # Testing with unverified user
    user.is_verified = False
    db.commit()

    response = client.patch('/companies/info', headers={"Authorization": f"Bearer {get_valid_token()}"},
                            params={'description': 'newDescription'})

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_info(client: TestClient, db, test_db, mocker):
    user, company = await fill_test_db(db)
    info = await create_info()
    company.info_id = info.id
    db.add(info)
    db.commit()
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.delete(f'/companies/info/dummyInfoId', headers={"Authorization": f"Bearer {get_valid_token()}"})

    assert response.status_code == 204
    assert info.is_deleted == True


@pytest.mark.asyncio
async def test_upload(client: TestClient, db, test_db, mocker):
    user, company = await fill_test_db(db)
    info = await create_info()
    company.info_id = info.id
    db.add(info)
    db.commit()
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)
    mocker.patch('app.api.api_v1.endpoints.companies.NudeDetector.detect')
    mock_image_data = b'test image data'

    response = client.post('/companies/info/upload', headers={"Authorization": f"Bearer {get_valid_token()}"},
                           files={'image': ('test_image.jpg', mock_image_data, 'image/jpeg')})

    assert response.status_code == 200
    assert response.json().get('message') == "Image uploaded successfully"

    # Testing with explicit content
    mocker.patch('app.api.api_v1.endpoints.companies.NudeDetector.detect', return_value=[{'class': 'BUTTOCKS_EXPOSED'}])

    response = client.post('/companies/info/upload', headers={"Authorization": f"Bearer {get_valid_token()}"},
                           files={'image': ('test_image.jpg', mock_image_data, 'image/jpeg')})

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_image(client: TestClient, db, test_db, mocker):
    user, company = await fill_test_db(db)
    info = await create_info()
    company.info_id = info.id
    mock_image_data = b'test image data'
    info.picture = mock_image_data
    db.add(info)
    db.commit()
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.get('/companies/info/image', headers={"Authorization": f"Bearer {get_valid_token()}"})

    assert response.status_code == 200
    assert response.content == mock_image_data


@pytest.mark.asyncio
async def test_search_for_matches(client: TestClient, db, test_db, mocker):
    await fill_match_db(db)
    company = db.query(DbCompanies).first()
    mocker.patch('app.crud.crud_company.calculate_similarity', return_value=True)
    mocker.patch('app.core.auth.get_user_by_username', return_value=company.user)

    response = client.post('/companies/match', headers={"Authorization": f"Bearer {get_valid_token()}"},
                           params={'ad_id': 'dummyAdId'})

    assert response.status_code == 200
    assert response.json().get('message') == 'You have new matches!'


@pytest.mark.asyncio
async def test_get_matches(client: TestClient, db, test_db, mocker):
    await fill_match_db(db)
    company = db.query(DbCompanies).first()
    mocker.patch('app.core.auth.get_user_by_username', return_value=company.user)

    response = client.get('/companies/match/', headers={"Authorization": f"Bearer {get_valid_token()}"})

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_approve_match(client: TestClient, db, test_db, mocker):
    await fill_match_db(db)
    company = db.query(DbCompanies).first()
    prof = db.query(DbProfessionals).first()
    company_ad = db.query(DbAds).filter(DbAds.is_resume == False).first()
    prof_ad = db.query(DbAds).filter(DbAds.is_resume == True).first()
    match = DbJobsMatches(
        ad_id=company_ad.id,
        resume_id=prof_ad.id,
        company_id=company.id,
        professional_id=prof.id
    )
    db.add(match)
    db.commit()
    mocker.patch('app.core.auth.get_user_by_username', return_value=company.user)

    response = client.patch('/companies/match', headers={"Authorization": f"Bearer {get_valid_token()}"},
                            params={'resume_id': prof_ad.id})

    assert response.status_code == 200
    assert match.company_approved == True

