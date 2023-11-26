import pytest

from fastapi import HTTPException

from app.crud import crud_company
from app.crud.crud_company import CRUDCompany
from app.db.models import DbCompanies, DbUsers, DbInfo
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
        user_id=user.id
    )
    return user, company


async def create_info() -> DbInfo:
    info = DbInfo(
        id='dummyInfoId',
        description='dummyDescription',
        location='dummyLocation'
    )
    return info


info_schema = CompanyInfoCreate(
    description='dummyDescription',
    location='dummyLocation'
)


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
    db.add(user)
    db.add(company)
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

    assert result.id == info.id
    assert result.picture == bytearray(image)

    # Test with invalid info id
    with pytest.raises(HTTPException) as exception:
        await CRUDCompany.upload(db, 'invalidId', bytearray(image))

    exception_info = exception.value
    assert exception_info.status_code == 404
