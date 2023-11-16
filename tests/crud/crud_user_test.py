import app.crud.crud_user as crud
from app.schemas.company import CompanyCreate
from app.schemas.professional import ProfessionalCreate
from app.schemas.user import UserCreate
import pytest
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from app.db.database import get_db
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


@pytest.fixture
def db():
    return MagicMock(spec=Session)


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
@pytest.mark.parametrize("user_type, expected_factory", [
    ('admin', crud.UserFactory),
    ('professional', crud.ProfessionalFactory),
    ('company', crud.CompanyFactory),
    ('else', crud.UserFactory)
])
async def test_create_user_factory(user_type, expected_factory):
    result = crud.create_user_factory(user_type)
    assert result == expected_factory


@pytest.mark.asyncio
async def test_create_user_returnsAdmin(db, mocker) -> DbUsers:
    mock_create_user_factory = mocker.patch('app.crud.crud_user.create_user_factory', return_value=crud.UserFactory())
    mocker.patch('app.crud.crud_user.UserFactory.create_db_user', return_value=create_test_user('admin'))
    mocker.patch('app.crud.crud_user.send_email', return_value=None)
    
    result = await crud.create_user(db, user)

    mock_create_user_factory.assert_called_once_with("admin")

    assert result.username == 'dummyusername'
    assert result.password == 'dummypassword'
    assert result.email == 'dummyemail@mail.com'
    assert result.type == 'admin'
    assert result.id == 'test-user-id-uuid'


@pytest.mark.asyncio
async def test_create_user_returnsProfessional(db, mocker) -> DbProfessionals:
    mock_create_user_factory = mocker.patch('app.crud.crud_user.create_user_factory', return_value=crud.ProfessionalFactory())
    mocker.patch('app.crud.crud_user.ProfessionalFactory.create_db_user', return_value=create_test_user('professional'))
    mocker.patch('app.crud.crud_user.send_email', return_value=None)
    
    result = await crud.create_user(db, professional)

    mock_create_user_factory.assert_called_once_with("professional")

    assert result.first_name == professional.first_name
    assert result.last_name == professional.last_name
    assert result.user_id == 'test-user-id-uuid'


@pytest.mark.asyncio
async def test_create_user_returnsCompany(db, mocker) -> DbCompanies:
    mock_create_user_factory = mocker.patch('app.crud.crud_user.create_user_factory', return_value=crud.CompanyFactory())
    mocker.patch('app.crud.crud_user.CompanyFactory.create_db_user', return_value=create_test_user('company'))
    mocker.patch('app.crud.crud_user.send_email', return_value=None)
    
    result = await crud.create_user(db, company)

    mock_create_user_factory.assert_called_once_with("company")

    assert result.name == company.name
    assert result.user_id == 'test-user-id-uuid'
