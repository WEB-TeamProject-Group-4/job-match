import pytest

from fastapi import HTTPException

from app.crud import crud_company
from app.db.models import DbCompanies, DbUsers


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


@pytest.mark.asyncio
async def test_companies_crud(db, test_db):
    user, company = await create_dummy_company()
    db.add(user)
    db.add(company)
    db.commit()

    result = await crud_company.get_companies_crud(db, None, 1)

    assert len(result) == 1
    assert result[0].id == 'dummyCompanyId'

    # Testing with nonexistent company name filter
    result = await crud_company.get_companies_crud(db, 'dummyName', 1)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_company_by_id_crud(db, test_db):
    user, company = await create_dummy_company()
    db.add(user)
    db.add(company)
    db.commit()

    result = await crud_company.get_company_by_id_crud(db, company.id)

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

    result = await crud_company.update_company_crud(db, name=new_company_name, contact=new_company_contact,
                                                    user_id=user.id)

    assert result.id == company.id
    assert result.name == new_company_name
    assert result.contacts == new_company_contact


@pytest.mark.asyncio
async def test_check_company_delete_permission(db, test_db):
    user, company = await create_dummy_company()
    db.add(user)
    db.add(company)
    db.commit()

    result = await crud_company.check_company_delete_permission(db, company.id, user.id)

    assert result.id == company.id
    assert result.name == company.name

    # Testing when user is not admin and not owner of the company
    user.id = 'newDummyId'
    db.commit()

    with pytest.raises(HTTPException) as exception:
        await crud_company.check_company_delete_permission(db, company.id, user.id)

    exception_info = exception.value
    assert exception_info.status_code == 403


@pytest.mark.asyncio
async def test_delete_company_by_id_crud(db, test_db, mocker):
    user, company = await create_dummy_company()
    db.add(user)
    db.add(company)
    db.commit()
    mocker.patch('app.crud.crud_company.check_company_delete_permission', return_value=company)

    await crud_company.delete_company_by_id_crud(db, 'dummyId', 'dummyId')

    assert db.query(DbCompanies).all() == []
