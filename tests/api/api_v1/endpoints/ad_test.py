import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.security import SECRET_KEY
from app.db.models import DbAds, DbProfessionals, DbCompanies, DbInfo, DbUsers, DbSkills
from app.schemas.ad import ResumeStatus, AdStatusCreate


def get_valid_token():
    return jwt.encode({'username': 'dummyUserId'}, SECRET_KEY, algorithm='HS256')


async def create_user(db) -> DbUsers:
    user = DbUsers(id='dummyUserId',
                   username='dummyUsername',
                   password='dummyPassword',
                   email='dummy@email.com',
                   type='company',
                   is_verified=True)

    db.add(user)
    db.commit()

    return user


async def create_company(db) -> tuple[DbUsers, DbCompanies]:
    user = await create_user(db)
    company = DbCompanies(id='dummyCompanyId', name='dummyName', user_id=user.id)

    db.add(company)
    db.commit()

    return user, company


async def create_professional(db) -> tuple[DbUsers, DbProfessionals]:
    user = await create_user(db)

    user.type = 'professional'
    professional = DbProfessionals(id='dummyProfessionalId', first_name='dummyFirstName', last_name='dummyLastName',
                                   user_id=user.id)

    db.add(professional)
    db.commit()

    return user, professional


async def create_info(db) -> DbInfo:
    info = DbInfo(
        id='dummyInfoId',
        description='dummyDescription',
        location='dummyLocation',
        main_ad=None)

    db.add(info)
    db.commit()

    return info


async def create_ad(db, info: DbInfo) -> DbAds:
    ad = DbAds(
        id='dummyAdId',
        description='dummyDescription',
        location='dummyLocation',
        status=AdStatusCreate.ACTIVE,
        min_salary=1500,
        max_salary=2000,
        info_id=info.id,
        is_resume=False,
        is_deleted=False)

    db.add(ad)
    db.commit()

    return ad


async def create_skill(db) -> DbSkills:
    skill = DbSkills(name='dummySkill')

    db.add(skill)
    db.commit()

    return skill


ad_data_list = [
    {'id': 'dummy-id1', "description": "dummy desc1", "location": "Sofia", "status": "Hidden",
     'min_salary': 1000, 'max_salary': 1500, 'info_id': 'dummy_info_id1', 'is_resume': True, 'is_deleted': False},
    {'id': 'dummy-id2', "description": "dummy desc2", "location": "Plovdiv", "status": "Private",
     'min_salary': 1500, 'max_salary': 2000, 'info_id': 'dummy_info_id2', 'is_resume': True, 'is_deleted': False},
    {'id': 'dummy-id3', "description": "dummy desc3", "location": "Varna", "status": "Active",
     'min_salary': 2000, 'max_salary': 2500, 'info_id': 'dummy_info_id3', 'is_resume': False, 'is_deleted': False},
    {'id': 'dummy-id4', "description": "dummy desc4", "location": "Burgas", "status": "Archived",
     'min_salary': 2500, 'max_salary': 3000, 'info_id': 'dummy_info_id3', 'is_resume': False, 'is_deleted': True}
]

skill_data_list = [
    {'name': 'dummySkill1'}, {'name': 'dummySkill2'}, {'name': 'dummySkill3'}, {'name': 'dummySkill4'},
    {'name': 'dummySkill5'}
]


@pytest.mark.asyncio
async def test_create_ad(client: TestClient, test_db, db, mocker):
    user, company = await create_company(db)
    info = await create_info(db)

    company.info_id = info.id
    db.commit()

    schema = {
        'description': 'dummyDescription',
        'location': 'dummyLocation',
        'status': 'Active',
        'min_salary': '1500',
        'max_salary': '3000',
    }

    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.post('/ads', headers={"Authorization": f"Bearer {get_valid_token()}"},
                           json=schema)

    assert response.status_code == 200
    assert response.json().get('description') == 'dummyDescription'
    assert response.json().get('max_salary') == 3000


@pytest.mark.asyncio
async def test_get_resumes(client: TestClient, test_db, db, mocker):
    user, company = await create_company(db)

    ads = [DbAds(**ad) for ad in ad_data_list]
    db.add_all(ads)
    db.commit()

    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.get('/ads/companies', headers={"Authorization": f"Bearer {get_valid_token()}"})
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2  # Only 2 out of 4 data entries match the criteria

    # Testing with professional
    user.type = 'professional'
    db.commit()

    response = client.get('/ads/companies', headers={"Authorization": f"Bearer {get_valid_token()}"})

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_job_ads(client: TestClient, test_db, db, mocker):
    user, professional = await create_professional(db)

    ads = [DbAds(**ad) for ad in ad_data_list]
    db.add_all(ads)
    db.commit()

    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.get('/ads/professionals', headers={"Authorization": f"Bearer {get_valid_token()}"})
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1  # Only 1 out of 4 data entries match the criteria

    # Testing with company
    user.type = 'company'
    db.commit()

    response = client.get('/ads/professionals', headers={"Authorization": f"Bearer {get_valid_token()}"})

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_resumes(client: TestClient, db, test_db, mocker):
    user, professional = await create_professional(db)
    info = await create_info(db)

    professional.info_id = info.id
    db.add(info)
    db.commit()

    ad = await create_ad(db, info)
    ad.is_resume = True  # change status to update resume
    db.commit()

    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.put(f'/ads/professionals/{ad.id}', headers={"Authorization": f"Bearer {get_valid_token()}"},
                          params={'description': 'newDescription', 'location': 'newLocation',
                                  'ad_status': ResumeStatus.MATCHED.value, 'min_salary': 1600, 'max_salary': 2100})

    assert response.status_code == 200
    assert response.json().get('description') == 'newDescription'
    assert response.json().get('location') == 'newLocation'
    assert response.json().get('status') == 'Matched'
    assert response.json().get('min_salary') == 1600
    assert response.json().get('max_salary') == 2100

    # Testing with company user
    user.type = 'company'
    db.commit()

    response = client.put(f'/ads/professionals/{ad.id}', headers={"Authorization": f"Bearer {get_valid_token()}"},
                          params={'description': 'newDescription',
                                  'location': 'dummyLocation',
                                  'status': 'Active', 'min_salary': '1600', 'max_salary': '2100'})

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_job_ads(client: TestClient, db, test_db, mocker):
    user, company = await create_company(db)
    info = await create_info(db)

    company.info_id = info.id
    db.add(info)
    db.commit()

    ad = await create_ad(db, info)
    db.add(ad)
    db.commit()

    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.put(f'/ads/companies/{ad.id}', headers={"Authorization": f"Bearer {get_valid_token()}"},
                          params={'description': 'newDescription', 'location': 'newLocation',
                                  'status': 'Active', 'min_salary': 1600, 'max_salary': 2100})

    assert response.status_code == 200
    assert response.json().get('description') == 'newDescription'
    assert response.json().get('location') == 'newLocation'
    assert response.json().get('status') == 'Active'
    assert response.json().get('min_salary') == 1600
    assert response.json().get('max_salary') == 2100

    # Testing with professional user
    user.type = 'professional'
    db.commit()

    response = client.put(f'/ads/companies/{ad.id}', headers={"Authorization": f"Bearer {get_valid_token()}"},
                          params={'description': 'newDescription', 'location': 'newLocation',
                                  'status': 'Active', 'min_salary': 1600, 'max_salary': 2100})

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_ad(client: TestClient, db, test_db, mocker):
    user, company = await create_company(db)

    info = await create_info(db)
    company.info_id = info.id
    db.add(info)
    db.commit()

    ad = await create_ad(db, info)

    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.delete(f'/ads/{ad.id}', headers={"Authorization": f"Bearer {get_valid_token()}"})

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_ad_by_id(client: TestClient, db, test_db, mocker):
    user, professional = await create_professional(db)

    info = await create_info(db)
    professional.info_id = info.id
    db.add(info)
    db.commit()

    ad = await create_ad(db, info)

    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.get(f'/ads/{ad.id}', headers={"Authorization": f"Bearer {get_valid_token()}"})

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_skill(client: TestClient, test_db, db, mocker):
    user, company = await create_company(db)

    schema = {"name": 'dummySkill'}

    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.post('/skills', headers={"Authorization": f"Bearer {get_valid_token()}"}, json=schema)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_skills(client: TestClient, test_db, db, mocker):
    user, company = await create_company(db)

    for skill in skill_data_list:
        skill = DbSkills(**skill)
        db.add(skill)
    db.commit()

    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.get('/skills', headers={"Authorization": f"Bearer {get_valid_token()}"})
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 5


@pytest.mark.asyncio
async def test_update_skill(client: TestClient, test_db, db, mocker):
    user, company = await create_company(db)
    skill = await create_skill(db)

    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.patch('/skills', headers={"Authorization": f"Bearer {get_valid_token()}"},
                            params={'skill_name': skill.name, 'new_name': 'newDummySkill'})

    assert response.status_code == 200
    assert response.json().get('name') == 'newDummySkill'


@pytest.mark.asyncio
async def test_delete_skill(client: TestClient, test_db, db, mocker):
    user, professional = await create_professional(db)
    skill = await create_skill(db)

    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.delete('/skills', headers={"Authorization": f"Bearer {get_valid_token()}"},
                             params={'skill_name': skill.name})

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_add_and_remove_ad_skill(client: TestClient, test_db, db, mocker):
    user, professional = await create_professional(db)

    info = await create_info(db)
    professional.info_id = info.id
    db.add(info)
    db.commit()

    ad = await create_ad(db, info)
    skill = await create_skill(db)

    mocker.patch('app.core.auth.get_user_by_username', return_value=user)

    response = client.post(f'/ads/{ad.id}/skills', headers={"Authorization": f"Bearer {get_valid_token()}"},
                           params={'skill_name': skill.name, 'level': 'Beginner'})

    assert response.status_code == 200
    assert response.json().get('skill_name') == 'dummySkill'
    assert response.json().get('level') == 'Beginner'

    # Remove skill from ad
    response = client.delete(f'/ads/{ad.id}/skills', headers={"Authorization": f"Bearer {get_valid_token()}"},
                             params={'skill_name': skill.name})

    assert response.status_code == 204
