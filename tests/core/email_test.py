from unittest.mock import AsyncMock
import pytest
from app.email import send_email
from app.db.models import DbUsers

dummy_email = ['dummy@email.com']
dummy_user = DbUsers(
    id='dummyId',
    username='dummyUsername',
    password='dummyPassword',
    email=dummy_email[0],
    type='dummyType'
)


@pytest.mark.asyncio
async def test_send_mail(mocker):
    mock_create_access_token = mocker.patch('app.email.create_access_token', return_value='valid_token')
    mock_send_message = mocker.patch('app.email.FastMail.send_message', new_callable=AsyncMock)

    await send_email(dummy_email, dummy_user)

    mock_create_access_token.assert_called_once()
    mock_send_message.assert_called_once()
