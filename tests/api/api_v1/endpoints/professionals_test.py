import jwt
import pytest
import io
import os

from fastapi.testclient import TestClient

from app.db.models import DbAds, DbCompanies, DbInfo, DbJobsMatches, DbProfessionals, DbSkills, DbUsers
from app.core.security import SECRET_KEY
from app.schemas.professional import ProfessionalCreateDisplay


def create_user():
    return DbUsers(username='TestUser', password='TestPassword', email='test.email@email.com', type='professional',
        is_verified=1
    )


def get_valid_token():
    return jwt.encode({'username': 'TestUser'}, SECRET_KEY, algorithm='HS256')


def create_professional() -> ProfessionalCreateDisplay:
    return ProfessionalCreateDisplay(username='TestUser', first_name='Professional', last_name='Lastname')


@pytest.fixture
def fill_test_db(test_db, db):
    user = DbUsers(id='test-id-one', username='User3', password='password123', email='test3@example.com', type='professional', is_verified = 1)
    db.add(user) 
    professional = DbProfessionals(id='professional-id-one', first_name='Prof1', last_name='Last1', status='Active', user_id='test-id-one', info_id='test-info-id')
    db.add(professional)
    db.commit()

    return user, professional


@pytest.fixture
def fill_info_test_db(test_db, db):
    info = DbInfo(id='test-info-id', description='test-description', location='Test Location', picture=None, main_ad=None)
    db.add(info)
    db.commit()

    return info


@pytest.fixture
def fill_resume_test_db(test_db, db):
    resume_1 = DbAds(id='test-resume-id-1', description='test-resume-description-1', 
                     location='Test First Location', status='Active', min_salary=1000, max_salary=2000, 
                     is_resume = 1, is_deleted = False, info_id='test-info-id')
    db.add(resume_1)
    db.commit()

    return resume_1



@pytest.fixture
def fill_jobs_matches_test_db(test_db, db):
    job_match = DbJobsMatches(
        ad_id='test-resume-id-1',
        resume_id='test-cv-id-1',
        professional_id='professional-id-one',
        company_id='test-company-id-1',
        professional_approved=False,
        is_deleted=False
    )
    db.add(job_match)
    db.commit()

    return job_match


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
         'type': 'professional', 'is_verified': 0},  # this should not be counted, is_verified == 0
        {'id': 'test-id-two', "username": "User2", "email": "test2@example.com", "password": "password123",
         'type': 'professional', 'is_verified': 1}, 
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
    mocker.patch('app.core.auth.get_user_by_username', return_value = create_user())

    response = client.get('/professionals', headers={"Authorization": f"Bearer {get_valid_token()}"})
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_all_resumes(client: TestClient, test_db, db, mocker, fill_test_db, fill_info_test_db):
    mocker.patch('app.core.auth.get_user_by_username')
    user, _ = fill_test_db
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
async def test_get_professional_info(client: TestClient, test_db, db, mocker, fill_test_db, fill_info_test_db):
    mocker.patch('app.core.auth.get_user_by_username')
    user, _ = fill_test_db
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
        "status": "Active",
        "active_resumes": 0
    }


@pytest.mark.asyncio
async def test_edit_professional_info_success(client: TestClient, test_db, db, mocker, fill_test_db, fill_info_test_db):
    user, professional = fill_test_db
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)


    response = client.post('/professionals/info', headers={"Authorization": f"Bearer {get_valid_token()}"}, params={'location': 'Changed Location'})


    assert response.status_code == 201
    changed_location: DbInfo = (db.query(DbInfo).filter(DbInfo.id == 'test-info-id').first())

    assert changed_location.location == 'Changed location'


@pytest.mark.asyncio
async def test_edit_summary_success(client: TestClient, test_db, db, mocker, fill_test_db, fill_info_test_db):
    user, professional = fill_test_db
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)


    response = client.patch('/professionals/summary', headers={"Authorization": f"Bearer {get_valid_token()}"}, params={'summary': 'Changed summary'})


    assert response.status_code == 200
    changed_summary: DbInfo = (db.query(DbInfo).filter(DbInfo.id == 'test-info-id').first())

    assert changed_summary.description == 'Changed summary'


@pytest.mark.asyncio
async def test_change_professional_status_success(client: TestClient, test_db, db, mocker, fill_test_db):
    user, professional = fill_test_db
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)


    response = client.patch('/professionals/status', headers={"Authorization": f"Bearer {get_valid_token()}"}, params={'status': 'busy'})


    assert response.status_code == 200
    changed_status = professional.status

    assert 'busy' == changed_status


@pytest.mark.asyncio
async def test_set_main_resume_success(client: TestClient, test_db, db, mocker, fill_test_db, fill_info_test_db, fill_resume_test_db):
    user, professional = fill_test_db
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)


    response = client.patch('/professionals/resume/test-resume-id-1', headers={"Authorization": f"Bearer {get_valid_token()}"})


    assert response.status_code == 200
    changed_summary: DbInfo = (db.query(DbInfo).filter(DbInfo.id == 'test-info-id').first())

    assert 'test-resume-id-1' == changed_summary.main_ad


# @pytest.mark.asyncio
# async def test_delete_professional_resume_success(client: TestClient, test_db, db, mocker, fill_test_db, fill_info_test_db, fill_resume_test_db):
#     user, professional = fill_test_db
#     mocker.patch('app.core.auth.get_user_by_username', return_value=user)
#     mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)
#     resume_id = 'test-resume-id-1'

#     response = client.delete(f'/professionals/resume/{resume_id}', headers={"Authorization": f"Bearer {get_valid_token()}"})
    
#     assert response.status_code == 204
#     deleted_resume: DbAds = (db.query(DbAds).filter(DbAds.id == 'test-resume-id-1').first())
    
#     assert deleted_resume == None


@pytest.mark.asyncio
async def test_delete_professional_profile(client: TestClient, test_db, db, mocker, fill_test_db, fill_info_test_db, fill_resume_test_db):
    user, professional = fill_test_db
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)
    
    response = client.delete(f'/professionals/professional-id-one', headers={"Authorization": f"Bearer {get_valid_token()}"})
    
    assert response.status_code == 204
    deleted_professional: DbProfessionals = (db.query(DbProfessionals).filter(DbProfessionals.id == 'professional-id-one').first())
    deleted_info: DbInfo = (db.query(DbInfo).filter(DbInfo.id == 'test-info-id').first())
    deleted_resume: DbAds = (db.query(DbAds).filter(DbAds.id == 'test-resume-id-1').first())

    assert deleted_professional.is_deleted == True
    assert deleted_info.is_deleted == True
    assert deleted_resume.is_deleted == True


@pytest.mark.asyncio
async def test_get_image(client: TestClient, test_db, db, mocker, fill_test_db, fill_info_test_db):
    user, professional = fill_test_db
    info = fill_info_test_db
    info.picture = 'binary-code'
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)
    
    client.get(f'/professionals/image', headers={"Authorization": f"Bearer {get_valid_token()}"})
    updated_info: DbInfo = (db.query(DbInfo).filter(DbInfo.id == 'test-info-id').first())

    assert updated_info.picture == 'binary-code'


@pytest.mark.asyncio
async def test_upload_success(client: TestClient, test_db, db, mocker, fill_test_db, fill_info_test_db):
    user, professional = fill_test_db
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)
    mocker.patch('app.api.api_v1.endpoints.professionals.NudeDetector.detect', return_value=[])
    test_image_content = b'Test image content'
    test_image = io.BytesIO(test_image_content)
    client.post(f'/professionals/image', headers={"Authorization": f"Bearer {get_valid_token()}"}, files={"image": ("test_image.jpg", test_image, "image/jpeg")})
    
    updated_info: DbInfo = (db.query(DbInfo).filter(DbInfo.id == 'test-info-id').first())

    assert updated_info.picture is not None


@pytest.mark.asyncio
async def test_upload_explicit_content(client: TestClient, test_db, db, mocker, fill_test_db, fill_info_test_db):
    user, professional = fill_test_db
    test_image_content = b'Test image content'
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)
    mocker.patch('app.api.api_v1.endpoints.professionals.NudeDetector.detect', return_value=[{'class': 'BUTTOCKS_EXPOSED'}])
    test_image = io.BytesIO(test_image_content)
    response = client.post(f'/professionals/image', headers={"Authorization": f"Bearer {get_valid_token()}"}, files={"image": ("test_image.jpg", test_image, "image/jpeg")})
    
    data = response.json()
    updated_info: DbInfo = (db.query(DbInfo).filter(DbInfo.id == 'test-info-id').first())
    assert updated_info.picture is None
    assert data['detail'] == 'This photo is with explicit content.'


    
@pytest.mark.asyncio
async def test_approve_match(client: TestClient, test_db, db, mocker, fill_test_db, fill_jobs_matches_test_db):
    user, professional = fill_test_db
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)

    client.patch(f'/professionals/matches-approve', headers={"Authorization": f"Bearer {get_valid_token()}"},
                 params={'ad_id': 'test-resume-id-1'})
    approved_ad: DbJobsMatches = (db.query(DbJobsMatches).filter(DbJobsMatches.ad_id == 'test-resume-id-1').first())

    assert approved_ad.professional_approved == True


@pytest.mark.asyncio
async def test_get_all_matches(client: TestClient, test_db, db, mocker, fill_test_db, fill_resume_test_db, fill_jobs_matches_test_db):
    user, professional = fill_test_db
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)

    response = client.get(f'/professionals/matches-all', headers={"Authorization": f"Bearer {get_valid_token()}"})
    data = response.json()

    assert response.status_code == 200
    assert data == [
            {'ad_id': 'test-resume-id-1', 
             'description': 'test-resume-description-1',
             'location': 'Test First Location',
             'status': 'Active',
             'min_salary': 1000,
             'max_salary': 2000,
             'company_approved': False, 
             'professional_approved': False
        }
    ]

@pytest.mark.asyncio
async def test_search_for_matches(client: TestClient, test_db, db, mocker, fill_test_db, fill_info_test_db, fill_resume_test_db):
    user, professional = fill_test_db
    mocker.patch('app.core.auth.get_user_by_username', return_value=user)
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)
    mocker.patch('app.crud.crud_professional.calculate_similarity', return_value=True)
    user_company = DbUsers(
        id='company-user-id', username='company_user', password='company-password', email='company@email.com', type='company',
        is_verified=1, is_deleted=False
    )
    db.add(user_company)
    company = DbCompanies(
        id='test-company-id', name='test Company', contacts='contacts', user_id='company-user-id',
        is_deleted=False, info_id='test-info-company'
    )
    db.add(company)
    company_info = DbInfo(
        id='test-info-company', description='test info company', location='Test Location',
        picture=None, main_ad=None, is_deleted=False
    )
    db.add(company_info)

    job_ad = DbAds(
        id='test-company-ad-id', description='company ad description', location='Test First Location', status='Active', min_salary=1000,
        max_salary=2000, is_resume=0, is_deleted=False, info_id='test-info-company'
    )

    db.add(job_ad)
    db.commit()

    response = client.get(f'/professionals/matches-search', headers={"Authorization": f"Bearer {get_valid_token()}"},
                          params={'ad_id': 'test-resume-id-1', 'threshold': 0})
    data = response.json()

    matches:DbJobsMatches = (db.query(DbJobsMatches).all())
    
    assert response.status_code == 200
    assert data['message'] == 'You have new matches!'
    assert len(matches) == 1

 

    
    
    




    

