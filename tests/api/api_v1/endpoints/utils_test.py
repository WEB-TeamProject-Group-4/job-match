import pytest
from starlette.responses import HTMLResponse
from fastapi.exceptions import HTTPException

from fastapi.testclient import TestClient

from app.db.models import DbUsers


def test_email_verification_success(client: TestClient, test_db, db, mocker):
    db_user = DbUsers(
        username='TestUser',
        password='TestPassword',
        email='test.email@email.com',
        type='admin',
        is_verified=False
    )

    db.add(db_user)
    db.commit()

    mocker.patch('app.api.api_v1.endpoints.utils.very_token', return_value=db_user)
    mocker.patch('app.api.api_v1.endpoints.utils.Jinja2Templates.TemplateResponse',
                 return_value=HTMLResponse(content="<html>Verification Successful</html>", status_code=200))

    response = client.get('/verification', params={'token': 'valid_token'})

    assert response.status_code == 200
    assert "<html>Verification Successful</html>" in response.text
    assert db_user.is_verified


def test_email_verification_already_verified(client: TestClient, test_db, db, mocker):
    db_user2 = DbUsers(
        username='TestUser',
        password='TestPassword',
        email='test.email@email.com',
        type='admin',
        is_verified=True
    )

    db.add(db_user2)
    db.commit()

    mocker.patch('app.api.api_v1.endpoints.utils.very_token', return_value=db_user2)

    response = client.get('/verification', params={'token': 'valid_token'})

    assert response.status_code == 200

    db.refresh(db_user2)
    assert db_user2.is_verified


def test_email_verification_invalid_token(client: TestClient, mocker):
    mocker.patch('app.api.api_v1.endpoints.utils.very_token', side_effect=HTTPException(
        status_code=401, detail='Invalid token'))

    response = client.get('/verification', params={'token': 'invalid_token'})

    assert response.status_code == 401
    assert response.json().get('detail') == 'Invalid token'


def test_email_verification_token_returns_none(client: TestClient, mocker):
    mocker.patch('app.api.api_v1.endpoints.utils.very_token', return_value=None)

    response = client.get('/verification', params={'token': 'some_invalid_token'})

    assert response.status_code == 401
    assert response.json().get('detail') == 'Invalid token'
