import pytest

from fastapi import HTTPException

from app.crud import crud_company
from app.crud.crud_company import CRUDCompany
from app.db.models import DbCompanies, DbUsers
from app.schemas.company import CompanyInfoCreate


async def create_dummy_company():
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


info_schema = CompanyInfoCreate(
    description='dummyDescription',
    location='dummyLocation'
)


@pytest.mark.asyncio
async def test_companies_crud(db, test_db):
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
async def test_get_company_by_id_crud(db, test_db):
    user, company = await create_dummy_company()
    db.add(user)
    db.add(company)
    db.commit()

    result = await CRUDCompany.get_by_id(db, company.id)

    assert result.id == company.id
    assert result.name == company.name


@pytest.mark.asyncio
async def test_update_company_crud(db, test_db):
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


@pytest.mark.asyncio
async def test_delete_company_by_id_crud(db, test_db, mocker):
    user, company = await create_dummy_company()
    db.add(user)
    db.add(company)
    db.commit()
    mocker.patch('app.crud.crud_company.is_admin', return_value=False)
    mocker.patch('app.crud.crud_company.is_owner', return_value=False)

    # Test when user is neither admin nor owner
    with pytest.raises(HTTPException) as exception:
        await CRUDCompany.delete_by_id(db, 'dummyCompanyId', 'dummyId')
    exception_info = exception.value
    assert exception_info.status_code == 403

    # Test when user is admin
    mocker.patch('app.crud.crud_company.is_admin', return_value=True)

    await CRUDCompany.delete_by_id(db, 'dummyCompanyId', 'dummyId')

    assert db.query(DbCompanies).all() == []


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
async def test_create_company_info_crud(db, test_db, mocker):
    user, company = await create_dummy_company()
    db.add(user)
    db.add(company)
    db.commit()
    mocker.patch('app.crud.crud_company.CRUDCompany.get_by_id', return_value=company)

    result = await CRUDCompany.create_info(db, company.id, info_schema)

    assert company.info_id == result.id
    assert result.description == info_schema.description
