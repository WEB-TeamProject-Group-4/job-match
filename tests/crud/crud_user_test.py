from app.crud.crud_user import create_db_user
from app.schemas.user import UserCreate
import pytest
from unittest.mock import patch
from app.db.database import get_db
from app.db.models import DbUsers

user = UserCreate(
    username='dummyusername',
    password='dummypassword',
    email='dummyemail@mail.com'
)


def create_dummy_db_user(user_type: str):
    return DbUsers(
        username=user.username,
        password=user.password,
        email=user.email,
        type=user_type
    )


@pytest.fixture(scope='module')
def mock_create_user():
    with patch('app.crud.crud_user.create_user') as mock_create_user:
        mock_create_user.return_value = create_dummy_db_user('admin')
        yield mock_create_user


@pytest.fixture(scope='module')
def mock_create_professional():
    with patch('app.crud.crud_user.create_user') as mock_create_professional:
        mock_create_company.return_value = create_db_user('professional')
        yield mock_create_professional


@pytest.fixture
def mock_create_company(scope='module'):
    with patch('app.crud.crud_user.create_user') as mock_create_company:
        mock_create_company.return_value = create_db_user('company')
        yield mock_create_company


@pytest.fixture
def mock_send_email(scope='module'):
    with patch('app.crud.crud_user.send_email') as mock_send_email:
        yield mock_send_email


@pytest.mark.asyncio
async def test_create_db_user(mock_send_email, mock_create_user):
    db = get_db()

    result = await create_db_user(db, user)

    mock_create_user.assert_called_once_with(db, user, "admin")
    mock_send_email.assert_called_once_with([user.email], mock_create_user.return_value)
    assert result.username == user.username
    assert result.password == user.password
    assert result.email == user.email
    assert result.type == 'admin'
