from fastapi import HTTPException
import pytest
import app.crud.crud_user as crud_user
from app.schemas.company import CompanyCreate, CompanyDisplay
from app.schemas.professional import ProfessionalCreate, ProfessionalDisplay
from app.schemas.user import UserCreate
from sqlalchemy.exc import IntegrityError
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
            id = 'test-user-id-uuid',
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
    
    elif user_type =='company':
        return DbCompanies(
            name='TestCompany',
            user_id='test-user-id-uuid'
        )


@pytest.mark.asyncio
async def test_user_factory_create_db_user_returnsAdmin(db, mocker):
    mocker.patch('app.crud.crud_user.Hash.bcrypt', return_value=user.password)

    result = await crud_user.UserFactory.create_db_user(db, user, 'admin')

    assert result.username == user.username
    assert result.password == user.password
    assert result.email == user.email
    assert result.type == 'admin'


@pytest.mark.asyncio
async def test_user_factory_create_db_user_returnsProfessional(db, mocker):
    mocker.patch('app.crud.crud_user.Hash.bcrypt', return_value=user.password)

    result = await crud_user.UserFactory.create_db_user(db, user, 'professional')

    assert result.username == user.username
    assert result.password == user.password
    assert result.email == user.email
    assert result.type == 'professional'


@pytest.mark.asyncio
async def test_user_factory_create_db_user_returnsCompany(db, mocker):
    mocker.patch('app.crud.crud_user.Hash.bcrypt', return_value=user.password)

    result = await crud_user.UserFactory.create_db_user(db, user, 'company')

    assert result.username == user.username
    assert result.password == user.password
    assert result.email == user.email
    assert result.type == 'company'


@pytest.mark.asyncio
async def test_user_factory_create_db_user_risesHTTPException(db, mocker):
    mocker.patch.object(db, 'commit', side_effect=IntegrityError("", params=None, orig=None))

    with pytest.raises(HTTPException) as exception:
        result = await crud_user.UserFactory.create_db_user(db, user, 'admin')

    exception_info = exception.value
    assert exception_info.status_code == 409
    db.add.assert_called_once()
    db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_professional_factory_create_db_user(db, mocker) -> ProfessionalDisplay:
    mocker.patch('app.crud.crud_user.UserFactory.create_db_user', return_value=create_test_user('admin'))
    mocker.patch('app.crud.crud_user.send_email', return_value=None)

    result = await crud_user.ProfessionalFactory.create_db_user(db, professional, 'professional')

    assert result.username == user.username
    assert result.first_name == professional.first_name
    assert result.last_name == professional.last_name


@pytest.mark.asyncio
async def test_company_factory_create_db_user_success(db, mocker) -> CompanyDisplay:
    mocker.patch('app.crud.crud_user.UserFactory.create_db_user', return_value=create_test_user('admin'))
    mocker.patch('app.crud.crud_user.send_email', return_value=None)

    result = await crud_user.CompanyFactory.create_db_user(db, company, 'company')

    assert result.username == user.username
    assert result.name == company.name


@pytest.mark.asyncio
async def test_company_factory_create_db_user_risesHTTPError(db, mocker) -> CompanyDisplay:
    mocker.patch('app.crud.crud_user.UserFactory.create_db_user', return_value=create_test_user('admin'))
    mocker.patch.object(db, 'add', side_effect=IntegrityError("", params=None, orig=None))
    

    with pytest.raises(HTTPException) as exception:
        result = await crud_user.CompanyFactory.create_db_user(db, company, 'company')

    exception_info = exception.value
    assert exception_info.status_code == 409
    db.add.assert_called_once()

    

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
async def test_create_user_returnsAdmin(db, mocker) -> DbUsers:
    mock_create_user_factory = mocker.patch('app.crud.crud_user.create_user_factory', return_value=crud_user.UserFactory())
    mocker.patch('app.crud.crud_user.UserFactory.create_db_user', return_value=create_test_user('admin'))
    mocker.patch('app.crud.crud_user.send_email', return_value=None)
    
    result = await crud_user.create_user(db, user)

    mock_create_user_factory.assert_called_once_with("admin")

    assert result.username == 'dummyusername'
    assert result.password == 'dummypassword'
    assert result.email == 'dummyemail@mail.com'
    assert result.type == 'admin'
    assert result.id == 'test-user-id-uuid'


@pytest.mark.asyncio
async def test_create_user_returnsProfessional(db, mocker) -> DbProfessionals:
    mock_create_user_factory = mocker.patch('app.crud.crud_user.create_user_factory', return_value=crud_user.ProfessionalFactory())
    mocker.patch('app.crud.crud_user.ProfessionalFactory.create_db_user', return_value=create_test_user('professional'))
    mocker.patch('app.crud.crud_user.send_email', return_value=None)
    
    result = await crud_user.create_user(db, professional)

    mock_create_user_factory.assert_called_once_with("professional")

    assert result.first_name == professional.first_name
    assert result.last_name == professional.last_name
    assert result.user_id == 'test-user-id-uuid'


@pytest.mark.asyncio
async def test_create_user_returnsCompany(db, mocker) -> DbCompanies:
    mock_create_user_factory = mocker.patch('app.crud.crud_user.create_user_factory', return_value=crud_user.CompanyFactory())
    mocker.patch('app.crud.crud_user.CompanyFactory.create_db_user', return_value=create_test_user('company'))
    mocker.patch('app.crud.crud_user.send_email', return_value=None)
    
    result = await crud_user.create_user(db, company)

    mock_create_user_factory.assert_called_once_with("company")

    assert result.name == company.name
    assert result.user_id == 'test-user-id-uuid'