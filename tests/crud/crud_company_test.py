import pytest

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from app.crud import crud_company
from app.crud.crud_company import CRUDCompany
from app.db.models import DbCompanies, DbUsers, DbInfo, DbAds, DbProfessionals, DbJobsMatches
from app.schemas.company import CompanyInfoCreate


async def create_dummy_company() -> tuple[DbUsers, DbCompanies]:
    user = DbUsers(
        id='dummyId',
        username='dummyUsername',
        password='dummyPassword',
        email='dummyEmail',
        type='company',
        is_verified=True
    )
    company = DbCompanies(
        id='dummyCompanyId',
        name='dummyCompanyName',
        user_id=user.id,
    )
    return user, company


async def create_dummy_professional() -> tuple[DbUsers, DbProfessionals]:
    user = DbUsers(
        id='dummyId2',
        username='dummyUsername2',
        password='dummyPassword2',
        email='dummyEmail2',
        type='professional',
        is_verified=True
    )
    professional = DbProfessionals(
        id='dummyProfId',
        first_name='dummyFirstName',
        last_name='dummyLastName',
        user_id=user.id
    )
    return user, professional


async def create_dummy_ad() -> DbAds:
    ad = DbAds(
        id='dummyAdId',
        description='dummyDescription',
        location='dummyLocation',
        status='Active',
        min_salary=200,
        max_salary=300,
        info_id='dummyInfoId'
    )
    return ad


async def create_prof_ad():
    ad = DbAds(
        id='dummyAdId2',
        description='dummyDescription',
        location='dummyLocation',
        status='Active',
        min_salary=200,
        max_salary=300,
        info_id='dummyInfoId',
        is_resume=True,
    )
    return ad


async def create_info() -> DbInfo:
    info = DbInfo(
        id='dummyInfoId',
        description='dummyDescription',
        location='dummyLocation'
    )
    return info


async def create_prof_info() -> DbInfo:
    info = DbInfo(
        id='dummyProfInfoId',
        description='dummyDescription',
        location='dummyLocation'
    )
    return info


info_schema = CompanyInfoCreate(
    description='dummyDescription',
    location='dummyLocation'
)


async def fill_match_db(db):
    company_user, company = await create_dummy_company()
    prof_user, prof = await create_dummy_professional()
    company_info = await create_info()
    prof_info = await create_prof_info()
    prof.info_id = prof_info.id
    company.info_id = company_info.id
    company_ad = await create_dummy_ad()
    prof_ad = await create_prof_ad()
    company_ad.info_id = company_info.id
    prof_ad.info_id = prof_info.id
    db.add(company_info)
    db.add(prof_info)
    db.add(company_user)
    db.add(company)
    db.add(prof_user)
    db.add(prof)
    db.add(company_ad)
    db.add(prof_ad)
    db.commit()


@pytest.mark.asyncio
async def test_get_multi(db, test_db):
    user, company = await create_dummy_company()
    db.add(user)
    db.add(company)
    db.commit()

    result = await CRUDCompany.get_multi(db, None, 1)

    assert len(result) == 1
    assert result[0].id == 'dummyCompanyId'

    # Testing with nonexistent company name filter
    result = await CRUDCompany.get_multi(db, 'dummyName', 1)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_by_id(db, test_db):
    user, company = await create_dummy_company()
    db.add(user)
    db.add(company)
    db.commit()

    result = await CRUDCompany.get_by_id(db, company.id)

    assert result.id == company.id
    assert result.name == company.name

    # Testing with invalid id
    with pytest.raises(HTTPException) as exception:
        await CRUDCompany.get_by_id(db, 'invalidId')

    exception_info = exception.value
    assert exception_info.status_code == 404


@pytest.mark.asyncio
async def test_update(db, test_db):
    user, company = await create_dummy_company()
    db.add(user)
    db.add(company)
    db.commit()
    new_company_name = 'newDummyName'
    new_company_contact = 'dummyContact'

    result = await CRUDCompany.update(db, name=new_company_name, contact=new_company_contact,
                                      user_id=user.id)

    assert result.id == company.id
    assert result.name == new_company_name
    assert result.contacts == new_company_contact

    # Testing with deleted company
    company.is_deleted = True
    db.commit()

    with pytest.raises(HTTPException) as exception:
        await CRUDCompany.update(db, name=new_company_name, contact=new_company_contact,
                                 user_id=user.id)

    exception_info = exception.value
    assert exception_info.status_code == 404


@pytest.mark.asyncio
async def test_delete_by_id(db, test_db, mocker):
    user, company = await create_dummy_company()
    info = await create_info()
    company.info_id = info.id
    ad = await create_dummy_ad()
    db.add(user)
    db.add(info)
    db.add(company)
    db.add(ad)
    db.commit()
    mocker.patch('app.crud.crud_company.is_admin', return_value=False)
    mocker.patch('app.crud.crud_company.is_owner', return_value=False)

    # Test when user is neither admin nor owner
    with pytest.raises(HTTPException) as exception:
        await CRUDCompany.delete_by_id(db, 'dummyCompanyId', user)
    exception_info = exception.value
    assert exception_info.status_code == 403

    # Test when user is admin
    mocker.patch('app.crud.crud_company.is_admin', return_value=True)

    await CRUDCompany.delete_by_id(db, 'dummyCompanyId', user)

    assert company.is_deleted == True
    assert info.is_deleted == True
    assert ad.is_deleted == True

    # Test with invalid company id
    with pytest.raises(HTTPException) as exception:
        await CRUDCompany.delete_by_id(db, 'invalidId', user)

    exception_info = exception.value
    assert exception_info.status_code == 404


@pytest.mark.asyncio
async def test_is_admin(db, test_db):
    user = DbUsers(
        id='dummyId',
        username='dummyUsername',
        password='dummyPassword',
        email='dummyEmail',
        type='admin',
        is_verified=True
    )
    db.add(user)
    db.commit()

    assert await crud_company.is_admin(user) is True

    # Testing when user is not admin
    user.type = 'company'
    db.commit()

    assert await crud_company.is_admin(user) is False


@pytest.mark.asyncio
async def test_is_owner(db, test_db):
    user, company = await create_dummy_company()
    db.add(user)
    db.add(company)
    db.commit()

    assert await crud_company.is_owner(company, user.id) is True

    # Testing when user is not owner
    user.id = 'newDummyId'
    db.commit()

    assert await crud_company.is_owner(company, user.id) is False


@pytest.mark.asyncio
async def test_create_info(db, test_db, mocker):
    user, company = await create_dummy_company()
    db.add(user)
    db.add(company)
    db.commit()
    mocker.patch('app.crud.crud_company.CRUDCompany.get_by_id', return_value=company)

    result = await CRUDCompany.create_info(db, company.id, info_schema)

    assert company.info_id == result.id
    assert result.description == info_schema.description

    # Testing with already existing info
    mock_update_info = mocker.patch('app.crud.crud_company.CRUDCompany.update_info')

    result = await CRUDCompany.create_info(db, company.id, info_schema)
    mock_update_info.assert_called_once()


@pytest.mark.asyncio
async def test_get_info_by_id(db, test_db):
    user, company = await create_dummy_company()
    info = await create_info()
    company.info_id = info.id
    db.add(user)
    db.add(company)
    db.add(info)
    db.commit()

    result = await CRUDCompany.get_info_by_id(db, info.id, company.id)

    assert result.id == info.id
    assert result.active_job_ads == 0
    assert result.number_of_matches == 0

    # Test with invalid info id
    with pytest.raises(HTTPException) as exception:
        await CRUDCompany.get_info_by_id(db, 'invalidId', company.id)

    exception_info = exception.value
    assert exception_info.status_code == 404


@pytest.mark.asyncio
async def test_update_info(db, test_db):
    info = await create_info()
    db.add(info)
    db.commit()
    new_description = 'newDummyDescription'
    new_location = 'newDummyLocation'

    result = await CRUDCompany.update_info(db, info.id, new_description, new_location)

    assert result.id == info.id
    assert result.description == new_description
    assert result.location == new_location

    # Test with invalid info id
    with pytest.raises(HTTPException) as exception:
        await CRUDCompany.update_info(db, 'invalidId', new_description, new_location)

    exception_info = exception.value
    assert exception_info.status_code == 404


@pytest.mark.asyncio
async def test_delete_info(db, test_db, mocker):
    user, company = await create_dummy_company()
    info = await create_info()
    company.info_id = info.id
    db.add(user)
    db.add(company)
    db.add(info)
    db.commit()

    mocker.patch('app.crud.crud_company.is_admin', return_value=False)
    mocker.patch('app.crud.crud_company.is_owner', return_value=False)

    with pytest.raises(HTTPException) as exception:
        await CRUDCompany.delete_info_by_id(db, info.id, user)
    exception_info = exception.value
    assert exception_info.status_code == 403

    mocker.patch('app.crud.crud_company.is_owner', return_value=True)
    await CRUDCompany.delete_info_by_id(db, info.id, user)

    assert info.is_deleted == True

    # Test with invalid info id
    with pytest.raises(HTTPException) as exception:
        await CRUDCompany.delete_info_by_id(db, 'invalidId', user)

    exception_info = exception.value
    assert exception_info.status_code == 404


@pytest.mark.asyncio
async def test_upload(db, test_db):
    info = await create_info()
    db.add(info)
    db.commit()
    image = [23, 222, 31]

    result = await CRUDCompany.upload(db, info.id, bytearray(image))

    assert isinstance(result, StreamingResponse)

    # Test with invalid info id
    with pytest.raises(HTTPException) as exception:
        await CRUDCompany.upload(db, 'invalidId', bytearray(image))

    exception_info = exception.value
    assert exception_info.status_code == 404


@pytest.mark.asyncio
async def test_getimage(db, test_db):
    info = await create_info()
    db.add(info)
    db.commit()
    info.picture = bytearray([23, 222, 31])

    result = await CRUDCompany.get_image(db, info.id)

    assert isinstance(result, StreamingResponse)

    # Test with invalid info id
    with pytest.raises(HTTPException) as exception:
        await CRUDCompany.get_image(db, 'invalidId')

    exception_info = exception.value
    assert exception_info.status_code == 404


@pytest.mark.asyncio
async def test_find_matches(db, test_db, mocker):
    await fill_match_db(db)
    company = db.query(DbCompanies).first()
    mocker.patch('app.crud.crud_company.calculate_similarity', return_value=True)

    # Testing with no matching skills
    result = await CRUDCompany.find_matches(db, company, 'dummyAdId', 0.0)

    assert result.body == b'{"message":"You have new matches!"}'

    # Testing when match is already added
    result = await CRUDCompany.find_matches(db, company, 'dummyAdId', 0.0)

    assert result.body == b'{"message":"You have no matches!"}'

    # Testing with invalid ad id

    with pytest.raises(HTTPException) as exception:
        await CRUDCompany.find_matches(db, company, 'invalidId', 0.0)

    exception_info = exception.value
    assert exception_info.status_code == 404

    # Testing with no company info
    company.info_id = None
    db.commit()

    with pytest.raises(HTTPException) as exception:
        await CRUDCompany.find_matches(db, company, 'dummyAdId', 0.0)

        exception_info = exception.value
        assert exception_info.status_code == 404


@pytest.mark.asyncio
async def test_get_matches_multi(db, test_db):
    await fill_match_db(db)
    company = db.query(DbCompanies).first()

    result = await CRUDCompany.get_matches_multi(db, company)

    assert result == []

    # Testing with JobMatches entry
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

    result = await CRUDCompany.get_matches_multi(db, company)

    assert len(result) == 1


@pytest.mark.asyncio
async def test_approve_match(db, test_db):
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

    with pytest.raises(HTTPException) as exception:
        await CRUDCompany.approve_match(db, 'invalidId', 'invalidId')

        exception_info = exception.value
        assert exception_info.status_code == 404

    # Testing with valid ids

    result = await CRUDCompany.approve_match(db, prof_ad.id, company.id)

    assert result.body == b'{"message":"Match approved!"}'
    assert match.company_approved == True
