import pytest

from fastapi import HTTPException

import app.crud.crud_user as crud_user
from app.schemas.company import CompanyCreate
from app.schemas.professional import ProfessionalCreate
from app.schemas.user import UserCreate
from app.db.models import DbCompanies, DbProfessionals, DbUsers

user = UserCreate(
    username='dummyusername',
    password='dummypassword',
    email='dummyemail@mail.com'
)

professional = ProfessionalCreate(
    username='Prof',
    password='profpassword',
    email='professional@mail.com',
    first_name='TestFirstName',
    last_name='TestLastName'
)

company = CompanyCreate(
    username='CompanyUsername',
    password='companypassword',
    email='company@mail.com',
    name='TestCompany'
)


def create_test_user(user_type: str):
    if user_type == 'admin':
        return DbUsers(
            id='test-user-id-uuid',
            username=user.username,
            password=user.password,
            email=user.email,
            type=user_type
        )

    elif user_type == 'professional':
        return DbProfessionals(
            first_name=professional.first_name,
            last_name=professional.last_name,
            user_id='test-user-id-uuid'
        )

    elif user_type == 'company':
        return DbCompanies(
            name='TestCompany',
            user_id='test-user-id-uuid'
        )


@pytest.mark.asyncio
async def test_user_factory_create_db_user_returns_admin(db, mocker, test_db):
    mocker.patch('app.crud.crud_user.Hash.bcrypt', return_value=user.password)

    result = await crud_user.UserFactory.create_db_user(db, user, 'admin')

    assert result.username == user.username
    assert result.password == user.password
    assert result.email == user.email
    assert result.type == 'admin'


@pytest.mark.asyncio
async def test_user_factory_create_db_user_returns_professional(db, mocker, test_db):
    mocker.patch('app.crud.crud_user.Hash.bcrypt', return_value=user.password)

    result = await crud_user.UserFactory.create_db_user(db, user, 'professional')

    assert result.username == user.username
    assert result.password == user.password
    assert result.email == user.email
    assert result.type == 'professional'


@pytest.mark.asyncio
async def test_user_factory_create_db_user_returns_company(db, mocker, test_db):
    mocker.patch('app.crud.crud_user.Hash.bcrypt', return_value=user.password)

    result = await crud_user.UserFactory.create_db_user(db, user, 'company')

    assert result.username == user.username
    assert result.password == user.password
    assert result.email == user.email
    assert result.type == 'company'


@pytest.mark.asyncio
async def test_user_factory_create_db_user_rises_HTTPException(db, test_db):
    test_user = create_test_user('admin')
    db.add(test_user)
    db.commit()
    with pytest.raises(HTTPException) as exception:
        result = await crud_user.UserFactory.create_db_user(db, user, 'admin')

    exception_info = exception.value
    assert exception_info.status_code == 409


@pytest.mark.asyncio
async def test_professional_factory_create_db_user(db, mocker, test_db):
    mocker.patch('app.crud.crud_user.send_email', return_value=None)

    result = await crud_user.ProfessionalFactory.create_db_user(db, professional, 'professional')

    assert result.username == professional.username
    assert result.first_name == professional.first_name
    assert result.last_name == professional.last_name


@pytest.mark.asyncio
async def test_company_factory_create_db_user_success(db, mocker, test_db):
    mocker.patch('app.crud.crud_user.send_email', return_value=None)

    result = await crud_user.CompanyFactory.create_db_user(db, company, 'company')

    assert result.username == company.username
    assert result.name == company.name


@pytest.mark.asyncio
async def test_company_factory_create_db_user_rises_HTTPError(db, test_db):
    test_company = create_test_user('company')
    db.add(test_company)
    db.commit()

    with pytest.raises(HTTPException) as exception:
        result = await crud_user.CompanyFactory.create_db_user(db, company, 'company')

    exception_info = exception.value
    assert exception_info.status_code == 409


@pytest.mark.parametrize("user_type, expected_factory", [
    ('admin', crud_user.UserFactory),
    ('professional', crud_user.ProfessionalFactory),
    ('company', crud_user.CompanyFactory),
    ('else', crud_user.UserFactory)
])
def test_create_user_factory(user_type, expected_factory):
    result = crud_user.create_user_factory(user_type)
    assert result == expected_factory


@pytest.mark.asyncio
async def test_create_user_returns_admin(db, mocker, test_db):
    mocker.patch('app.crud.crud_user.send_email', return_value=None)

    result = await crud_user.create_user(db, user)

    assert result.username == 'dummyusername'
    assert result.email == 'dummyemail@mail.com'
    assert result.type == 'admin'


@pytest.mark.asyncio
async def test_create_user_returns_professional(db, mocker, test_db):
    mocker.patch('app.crud.crud_user.send_email', return_value=None)

    result = await crud_user.create_user(db, professional)

    assert result.first_name == professional.first_name
    assert result.last_name == professional.last_name


@pytest.mark.asyncio
async def test_create_user_returns_company(db, mocker, test_db):
    mocker.patch('app.crud.crud_user.send_email', return_value=None)

    result = await crud_user.create_user(db, company)

    assert result.name == company.name
    assert result.username == company.username
