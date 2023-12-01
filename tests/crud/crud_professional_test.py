import pytest

from fastapi import HTTPException
from app.crud import crud_professional

from app.db.models import DbAds, DbCompanies, DbInfo, DbJobsMatches, DbProfessionals, DbUsers
from app.schemas.professional import ProfessionalAdMatchDisplay, ProfessionalInfoDisplay


@pytest.fixture
def  filling_test_db(db, test_db):
    user = DbUsers(id='test-id-one', username='User3', password='password123', email='test3@example.com', type='professional', is_verified = 1)
    db.add(user)

    professional = DbProfessionals(id='professional-id-one', first_name='Prof1', last_name='Last1', status='active', user_id='test-id-one', info_id='test-info-id')
    db.add(professional)

    db.commit()
    return user, professional


@pytest.fixture
def  filling_info_test_db(db, test_db):
    info = DbInfo(id='test-info-id', description='test-description', location='Test location', picture=None, main_ad=None)
    db.add(info)
    db.commit()

    return info
    

@pytest.fixture
def  filling_resume_test_db(db, test_db):
    resume_1 = DbAds(id='test-resume-id-1', description='test-resume-description-1',
                    location='Test First Location', status='Active', min_salary=1000, max_salary=2000,
                    is_resume=1, is_deleted=False, info_id='test-info-id')
    db.add(resume_1)
    db.commit()


@pytest.mark.asyncio
async def test_edit_info_success(db, mocker, test_db, filling_test_db):
    user, professional = filling_test_db
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)

    result = await crud_professional.edit_info(db, user, first_name='Changed', last_name='Changed', location='Changed')

    assert result == {"message": "Update successful"}
    assert professional.first_name == 'Changed'
    assert professional.last_name == 'Changed'
    assert professional.info.location == 'Changed'


@pytest.mark.asyncio
async def test_create_professional_info_success(db, test_db, filling_test_db):
    _, professional = filling_test_db
    summary = 'Test summary'
    location = 'Test location'

    await crud_professional.create_professional_info(db, professional, summary, location)

    assert professional.info.description == 'Test summary'
    assert professional.info.location == 'Test location'


@pytest.mark.asyncio
async def test_create_professional_info_error400(db, test_db, filling_test_db):
    _, professional = filling_test_db
    
    with pytest.raises(HTTPException) as exception:
        await crud_professional.create_professional_info(db, professional, None, None)

    assert exception.value.status_code == 400
    assert exception.value.detail == "Fields should be valid: 'summary' and 'location'!"
    

@pytest.mark.asyncio
async def test_get_info_success(db, mocker, test_db, filling_test_db, filling_info_test_db):
    user, professional = filling_test_db
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)
    mocker.patch('app.crud.crud_professional.get_resumes', return_value=[])

    result = await crud_professional.get_info(db, user)

    assert result == ProfessionalInfoDisplay(first_name='Prof1', last_name='Last1', summary='test-description', 
        location='Test location', status='active', picture=None, active_resumes=0)
    

@pytest.mark.asyncio
async def test_get_info_error404(db, mocker, test_db, filling_test_db):
    user, professional = filling_test_db
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)

    with pytest.raises(HTTPException) as exception:
        await crud_professional.get_info(db, user)

    assert exception.value.status_code == 404
    assert exception.value.detail == 'Please edit your personal information.'


@pytest.mark.asyncio
async def test_get_resumes_success(db, test_db, filling_test_db, filling_info_test_db):
    _, professional = filling_test_db
    resume_1 = DbAds(id='test-resume-id-1', description='test-resume-description-1', location='Test First Location', status='active', min_salary=1000, max_salary=2000, info_id='test-info-id')
    db.add(resume_1)

    resume_2 = DbAds(id='test-resume-id-2', description='test-resume-description-2', location='Test Second Location', status='active', min_salary=1000, max_salary=2000, info_id='test-info-id')
    db.add(resume_2)

    db.commit()

    result = crud_professional.get_resumes(db, professional)

    assert result == [
        {'id': 'test-resume-id-1', 'description': 'test-resume-description-1', 'location': 'Test First Location', 'status': 'active', 'min_salary': 1000, 'max_salary': 2000},
        {'id': 'test-resume-id-2', 'description': 'test-resume-description-2', 'location': 'Test Second Location', 'status': 'active', 'min_salary': 1000, 'max_salary': 2000}
        ]
    

@pytest.mark.asyncio
async def test_get_resumes_noInfo(db, test_db, filling_test_db):
    _, professional = filling_test_db # no info for the professional

    result = crud_professional.get_resumes(db, professional)

    assert result == []


@pytest.mark.asyncio
async def test_change_status(db, mocker, test_db, filling_test_db):
    user, professional = filling_test_db
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)
    status = 'busy'

    result = await crud_professional.change_status(status, db, user)

    assert professional.status == 'busy'
    assert result['message'] == 'Status changed successfully!'


@pytest.mark.asyncio
async def test_get_professional_success(db, test_db, filling_test_db):
    user, _ = filling_test_db

    result = await crud_professional.get_professional(db, user)

    assert result.id == 'professional-id-one'
    assert result.first_name == 'Prof1' 
    assert result.last_name == 'Last1'    
    assert result.status == 'active'    
    assert result.user_id == 'test-id-one'    
    assert result.info_id == 'test-info-id'


@pytest.mark.asyncio
async def test_get_professional_error404(db, test_db):
    user = DbUsers(id='test-id-one', username='User3', email='test3@example.com', password='password123', type='professional', is_verified = 1)
    db.add(user)
    db.commit()

    with pytest.raises(HTTPException) as exception:
        await crud_professional.get_professional(db, user)

    assert exception.value.status_code == 404
    assert exception.value.detail == 'You are not logged as professional'

    
# @pytest.mark.asyncio
# async def test_delete_resume_by_id_success(db, mocker, test_db, filling_test_db, filling_info_test_db, filling_resume_test_db):
#     user, professional = filling_test_db
#     mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)

#     with pytest.raises(HTTPException) as exception:
#         await crud_professional.delete_resume_by_id(db, user, resume_id='test-resume-id-1')

#     assert exception.value.status_code == 204
#     assert exception.value.detail == 'Main resume changed successfully'


# @pytest.mark.asyncio
# async def test_delete_resume_by_id_error404(db, mocker, test_db, filling_test_db, filling_info_test_db):
#     user, professional = filling_test_db
#     mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)

#     with pytest.raises(HTTPException) as exception:
#         await crud_professional.delete_resume_by_id(db, user, resume_id='test-resume-id-1')

#     assert exception.value.status_code == 404
#     assert exception.value.detail == 'Resume not found'


@pytest.mark.asyncio
async def test_setup_main_resume_success(db, mocker, test_db, filling_test_db, filling_info_test_db , filling_resume_test_db):
    user, professional = filling_test_db
    info = filling_info_test_db
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)

    result = await crud_professional.setup_main_resume('test-resume-id-1', db, user)

    assert result['message'] == 'Main resume changed successfully'
    assert info.main_ad == 'test-resume-id-1'


@pytest.mark.asyncio
async def test_setup_main_resume_error404(db, mocker, test_db, filling_test_db, filling_info_test_db):
    user, professional = filling_test_db
    info = filling_info_test_db
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)

    result = await crud_professional.setup_main_resume('test-resume-id-1', db, user)

    assert result['message'] == 'Resume not found'
    assert info.main_ad == None


def test_is_user_verified_success(test_db, filling_test_db):
    user, _ = filling_test_db

    result = crud_professional.is_user_verified(user)

    assert result.is_verified == True


def test_is_user_verified_error403_notVerified(db, test_db):
    user = DbUsers(id='test-id-one', username='User3', email='test3@example.com', password='password123', type='professional', is_verified = 0) # this should not be counted, is_verified == 0
    db.add(user)

    with pytest.raises(HTTPException) as exception:
        crud_professional.is_user_verified(user)

    assert exception.value.status_code == 403
    assert exception.value.detail == 'Please verify your account'


def test_is_user_verified_error403(db, test_db):
    user = DbUsers(id='test-id-one', username='User3', email='test3@example.com', password='password123', type='company', is_verified = 1) # should be not allowed for companies type == 'company'
    db.add(user)

    with pytest.raises(HTTPException) as exception:
        crud_professional.is_user_verified(user)

    assert exception.value.status_code == 403


@pytest.mark.asyncio
async def test_edit_professional_summary_with_info(db, mocker, test_db, filling_test_db, filling_info_test_db):
    user, professional = filling_test_db
    info = filling_info_test_db
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)
    summary = 'changed summary'

    result = await crud_professional.edit_professional_summary(db, user, summary)

    assert result['message'] == 'Your summary has been updated successfully'
    assert info.description == 'changed summary'


@pytest.mark.asyncio
async def test_get_all_approved_professionals(db, test_db, filling_info_test_db):
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
        {'id': 'professional-id-one', 'first_name': 'Prof1', 'last_name': 'Last1', 'status': 'active', 'user_id': 'test-id-one', 'info_id': None},
        {'id': 'professional-id-two', 'first_name': 'Prof2', 'last_name': 'Last2', 'status':'busy', 'user_id': 'test-id-two', 'info_id': 'test-info-id'},
        {'id': 'professional-id-three', 'first_name': 'Prof3', 'last_name': 'Last3', 'status': 'active', 'user_id': 'test-id-three', 'info_id': None},
        {'id': 'professional-id-four', 'first_name': 'Prof4', 'last_name': 'Last4', 'status': 'active', 'user_id': 'test-id-four', 'info_id': None}

    ]

    for professional_data in professional_data_list:
        professional = DbProfessionals(**professional_data)
        db.add(professional)

    db.commit()
    first_name, last_name, status, location, page, page_items = 'Prof2', 'Last2', 'busy', 'Test location', None, None

    result = await crud_professional.get_all_approved_professionals(db, first_name, last_name, status, location, page, page_items)

    assert len(result) == 1


@pytest.mark.asyncio
async def test_edit_professional_summary_no_info(db, mocker, test_db, filling_test_db):
    user, professional = filling_test_db
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)
    summary = 'changed summary'

    result = await crud_professional.edit_professional_summary(db, user, summary)

    assert result['message'] == 'Your summary has been updated successfully'
    assert professional.info_id is not None


@pytest.mark.asyncio
async def test_delete_profile(db, mocker, test_db, filling_test_db, filling_info_test_db, filling_resume_test_db):
    _, professional = filling_test_db
    mocker.patch('app.crud.crud_professional.get_professional', return_value=professional)
    professional_id = 'professional-id-one'

    await crud_professional.delete_professional_by_id(db, professional_id)
    deleted_user: DbUsers = (db.query(DbUsers).filter(DbUsers.id == 'test-id-one').first())
    deleted_professional: DbProfessionals = (db.query(DbProfessionals).filter(DbProfessionals.id == 'professional-id-one').first())
    deleted_info: DbInfo = (db.query(DbInfo).filter(DbInfo.id == 'test-info-id').first())
    deleted_resume: DbAds = (db.query(DbAds).filter(DbAds.id == 'test-resume-id-1').first())
    
    assert deleted_user.is_deleted == True
    assert deleted_professional.is_deleted == True
    assert deleted_info.is_deleted == True
    assert deleted_resume.is_deleted == True


@pytest.mark.asyncio
async def test_upload_picture_success(db, test_db, filling_test_db, filling_info_test_db):
    info: DbInfo = filling_info_test_db
    test_image_content = b'Test image content'
    test_image = bytearray(test_image_content)

    result = await crud_professional.upload_picture(db, info.id, test_image)
    updated_info: DbInfo = (db.query(DbInfo).filter(DbInfo.id == 'test-info-id').first())

    assert result["message"] == 'Image uploaded successfully'
    assert updated_info.picture is not None


@pytest.mark.asyncio
async def test_upload_picture_raise404(db, test_db, filling_test_db):
    info_id = 'wrong-info-id'
    test_image_content = b'Test image content'
    test_image = bytearray(test_image_content)

    with pytest.raises(HTTPException) as exception:
        await crud_professional.upload_picture(db, info_id, test_image)

    assert exception.value.status_code == 404
    assert exception.value.detail == 'Please edit your personal information.'


@pytest.mark.asyncio
async def test_upload_picture_raise400(db, test_db, filling_test_db, filling_info_test_db):
    info: DbInfo = filling_info_test_db
    test_large_image_content = b'A' * (crud_professional.MAX_IMAGE_SIZE_BYTES + 1)
    test_large_image = bytearray(test_large_image_content)

    with pytest.raises(HTTPException) as exception:
        await crud_professional.upload_picture(db, info.id, test_large_image)

    assert exception.value.status_code == 400
    assert exception.value.detail == 'Image size exceeds the maximum allowed size.'


@pytest.mark.asyncio
async def test_get_image_success(db, test_db, filling_test_db, filling_info_test_db):
    info: DbInfo = filling_info_test_db
    test_image_content = b'Test image content'
    test_image = bytearray(test_image_content)
    info.picture = test_image
    db.commit()

    await crud_professional.get_image(db, info.id)
    updated_info: DbInfo = (db.query(DbInfo).filter(DbInfo.id == 'test-info-id').first())

    assert updated_info.picture is not None
    assert type(updated_info.picture) == bytes


@pytest.mark.asyncio
async def test_get_image_raise404(db, test_db, filling_test_db):
    info_id = 'wrong-info-id'

    with pytest.raises(HTTPException) as exception:
        await crud_professional.get_image(db, info_id)
    
    assert exception.value.status_code == 404
    assert exception.value.detail == 'Please edit your personal information.'


@pytest.mark.asyncio
async def test_find_matches_success(db, mocker, test_db, filling_test_db, filling_info_test_db, filling_resume_test_db):
    user, _ = filling_test_db
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
    mocker.patch('app.crud.crud_professional.calculate_similarity', return_value=True)

    result = await crud_professional.find_matches(db, user, threshold=0, ad_id='test-resume-id-1')
    matches: DbJobsMatches = db.query(DbJobsMatches).all()

    assert result['message'] == 'You have new matches!'
    assert len(matches) == 1


@pytest.mark.asyncio
async def test_find_matches_error404Resume(db, test_db, filling_test_db, filling_info_test_db, filling_resume_test_db):
    user, _ = filling_test_db

    with pytest.raises(HTTPException) as exception:
        await crud_professional.find_matches(db, user, threshold=0, ad_id='test-resume-id-2')
    
    assert exception.value.status_code == 404
    assert exception.value.detail == 'There is no resume with id: test-resume-id-2'


@pytest.mark.asyncio
async def test_find_matches_error404matches(db, mocker,test_db, filling_test_db, filling_info_test_db, filling_resume_test_db):
    user, _ = filling_test_db
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
    mocker.patch('app.crud.crud_professional.calculate_similarity', return_value=True)
    await crud_professional.find_matches(db, user, threshold=0, ad_id='test-resume-id-1')

    with pytest.raises(HTTPException) as exception:
        await crud_professional.find_matches(db, user, threshold=0, ad_id='test-resume-id-1')

    matches:DbJobsMatches = db.query(DbJobsMatches).all()
    assert exception.value.status_code == 404
    assert exception.value.detail == 'You have no new matches'
    assert len(matches) == 1


def test_calculate_similarity_returnsTrue(mocker):
    resume_skills = ["test-skills-1", "test-skills-2", "test-skills-3", "test-skills-4"]
    ad_skills = ["test-skills-1", "test-skills-2", "test-skills-3", "test-skills-4", "test-skills-5"]

    result = crud_professional.calculate_similarity(set(resume_skills), set(ad_skills), threshold=0.2)

    assert result == True


def test_calculate_similarity_returnsZeroDivision(mocker):
    resume_skills = []
    ad_skills = []

    result = crud_professional.calculate_similarity(set(resume_skills), set(ad_skills), threshold=0.2)

    assert result == 0


@pytest.mark.asyncio
async def test_get_potential_matches(db, test_db, filling_test_db, filling_resume_test_db):
    user, _ = filling_test_db
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

    result = await crud_professional.get_potential_matches(db, user)

    assert result == [
        ProfessionalAdMatchDisplay(
            ad_id='test-resume-id-1', 
            description='test-resume-description-1', 
            location='Test First Location',
            status='Active', 
            min_salary=1000, 
            max_salary=2000, 
            company_approved=False, 
            professional_approved=False)]


@pytest.mark.asyncio
async def test_approve_match_by_ad_id_success(db, test_db, filling_test_db, filling_resume_test_db):
    user, _ = filling_test_db
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

    result = await crud_professional.approve_match_by_ad_id(db, user, ad_id='test-resume-id-1')

    approved_match: DbJobsMatches = db.query(DbJobsMatches).filter(DbJobsMatches.ad_id == 'test-resume-id-1').first()
    assert result['message'] == 'Match approved!'
    assert approved_match.professional_approved == True


@pytest.mark.asyncio
async def test_approve_match_by_ad_id_error404(db, test_db, filling_test_db):
    user, _ = filling_test_db
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

    with pytest.raises(HTTPException) as exception:
        await crud_professional.approve_match_by_ad_id(db, user, ad_id='test-resume-id-2')

    assert exception.value.status_code == 404
    assert exception.value.detail == 'There is no ad with ID:test-resume-id-2'











   




















