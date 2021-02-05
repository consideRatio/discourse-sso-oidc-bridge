"""
Tests to verify most of the functionality
"""

import time
import json
from contextlib import contextmanager
import pytest
from base64 import b64decode
from urllib.parse import urlparse, unquote
from discourse_sso_oidc_bridge import create_app


@pytest.fixture
def client():
    app = create_app()

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    yield client  # this is where the testing happens!
    ctx.pop()


@contextmanager
def client_maker(config):
    app = create_app(config)

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    yield client  # this is where the testing happens!
    ctx.pop()


@pytest.fixture
def auth_data():
    return {
        "access_token": "test_access_token",
        "id_token": {
            "iss": "issuer1",
            "aud": "client1",
            "sub": "john_doe",
            "name": "John Doe",
            "iat": 1550961213,
            "exp": 1550964813,
        },
        # INSPECT id_token_jwt at:
        # https://jwt.io/#debugger-io?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJpc3N1ZXIxIiwiYXVkIjoiY2xpZW50MSIsInN1YiI6ImpvaG5fZG9lIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTUwOTYxMjEzLCJleHAiOjE1NTA5NjQ4MTN9.eiBu_D5m4vPVd11C-phlKkHha2VPlmaRQPTuV49QTIk
        "id_token_jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        ".eyJpc3MiOiJpc3N1ZXIxIiwiYXVkIjoiY2xpZW50MSIsInN1YiI6ImpvaG5fZG9lIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTUwOTYxMjEzLCJleHAiOjE1NTA5NjQ4MTN9"
        ".eiBu_D5m4vPVd11C-phlKkHha2VPlmaRQPTuV49QTIk",
        "userinfo": {
            "sub": "john_doe",
            "name": "John Doe",
            "email": "john_doe@example.com",
            "preferred_username": "john_doe",
        },
        "last_authenticated": time.time(),
    }


@pytest.fixture
def auth_data_custom_userinfo():
    return {
        "access_token": "test_access_token",
        "id_token": {
            "iss": "issuer1",
            "aud": "client1",
            "sub": "john_doe",
            "name": "John Doe",
            "iat": 1550961213,
            "exp": 1550964813,
        },
        # INSPECT id_token_jwt at:
        # https://jwt.io/#debugger-io?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJpc3N1ZXIxIiwiYXVkIjoiY2xpZW50MSIsInN1YiI6ImpvaG5fZG9lIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTUwOTYxMjEzLCJleHAiOjE1NTA5NjQ4MTN9.eiBu_D5m4vPVd11C-phlKkHha2VPlmaRQPTuV49QTIk
        "id_token_jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        ".eyJpc3MiOiJpc3N1ZXIxIiwiYXVkIjoiY2xpZW50MSIsInN1YiI6ImpvaG5fZG9lIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTUwOTYxMjEzLCJleHAiOjE1NTA5NjQ4MTN9"
        ".eiBu_D5m4vPVd11C-phlKkHha2VPlmaRQPTuV49QTIk",
        "userinfo": {
            "a_very_unique_sub": "john_doe",
            "name": "John Doe",
            "email": "john_doe@example.com",
            "preferred_username": "john_doe",
        },
        "last_authenticated": time.time(),
    }


@pytest.fixture
def discourse_nonce():
    return {
        "discourse_nonce": "nonce=cb68251eefb5211e58c00ff1395f0c0b",
    }


def test_health_check_endpoint(client):
    """Test that we can access the health check endpoint /health"""
    with client.get("/health") as res:
        assert res.status_code == 200
        assert res.content_type == "application/json"
        assert json.loads(res.get_data()).get("status") == "success"


def test_sso_login_with_ok_sso_and_sig(client):
    """Test the payload is properly managed and the user is sent to the
    authentication page
    """
    with client.get(
        "/sso/login?sso=bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGI%3D%0A&"
        "sig=d87265a513d3fa4c7602ada38cfa60318c9804da6c95785ab36885dc79641671"
    ) as res:
        assert res.status_code == 302
        assert urlparse(res.location).path == "/sso/auth"


def test_sso_login_with_bad_sig(client):
    """Test the error code 400 is sent if the signature do not match
    the payload
    """
    with client.get(
        "/sso/login?sso=bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGI%3D%0A&"
        "sig=2828aa29899722b35a2f191d34ef9b3ce695e0e6eeec47deb46d588d70c7cb58"
    ) as res:
        assert res.status_code == 400


def test_sso_login_with_no_sso(client):
    """Test the error code 400 is sent if the sso field is not provided"""
    with client.get(
        "/sso/login?sig=2828aa29899722b35a2f191d34ef9b3ce695e0e6eeec47deb46d588d70c7cb56"
    ) as res:
        assert res.status_code == 400


def test_sso_login_with_no_sig(client):
    """Test the error code 400 is sent if the sig field is not provided"""
    with client.get(
        "/sso/login?sso=bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGI%3D%0A&"
    ) as res:
        assert res.status_code == 400


def test_sso_auth_no_auth_data_in_session(client):
    """Test that we are redirected to the OIDC issuer if we lack auth data in the session"""
    res = client.get("/sso/auth")
    assert res.status_code == 302
    assert (
        "client_id=dummy_client_id&response_type=code&scope=openid+profile&redirect_uri=https%3A%2F%2Fdiscourse-sso.example.com%2Fredirect_uri"
        in urlparse(res.location).query
    )


def test_sso_auth_no_nonce(client, auth_data):
    """Test that nonce is required after valid auth data has been found in the session"""
    with client.session_transaction() as session:
        session.update(auth_data)

    # TODO: Decide if it makes sense to redirect this to discourse login instead
    #       Redirecting to /sso/login will fail as we need to get a nonce from
    #       discourse.
    res = client.get("/sso/auth")
    assert res.status_code == 403


def test_sso_auth_state_approved(client, discourse_nonce, auth_data):
    """Test the verified sso login -> sso auth attempt is redirected back to Discourse"""
    with client.session_transaction() as session:
        session.update(discourse_nonce)
        session.update(auth_data)

    res = client.get("/sso/auth")
    assert res.status_code == 302
    assert urlparse(res.location).path == "/session/sso_login"
    assert (
        urlparse(res.location).query
        == "sso=bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGImZW1haWw9am9obl9kb2UlNDBleGFtcGxlLmNvbSZuYW1lPUpvaG4lMjBEb2UmdXNlcm5hbWU9am9obl9kb2UmZXh0ZXJuYWxfaWQ9am9obl9kb2U%3D&sig=4e4617a08d20f8380e10ba801879e79700cd14051da6341fc93c8563d50a155e"
    )


def test_configured_oidc_scope():
    """Test the that scope can be configured"""
    with client_maker(
        {
            "OIDC_SCOPE": "openid,profile,a_very_unique_scope",
        }
    ) as client:
        res = client.get("/sso/auth")
        assert res.status_code == 302
        assert "a_very_unique_scope" in urlparse(res.location).query


def test_configured_oidx_extra_auth_request_params():
    """Test the that scope can be configured"""
    with client_maker(
        {
            "OIDC_SCOPE": "openid,profile,a_very_unique_scope",
            "OIDC_EXTRA_AUTH_REQUEST_PARAMS": {
                "my_extra_param": "a_very_unique_extra_param",
            },
        }
    ) as client:
        res = client.get("/sso/auth")
        assert res.status_code == 302
        assert "a_very_unique_scope" in urlparse(res.location).query
        assert (
            "my_extra_param=a_very_unique_extra_param" in urlparse(res.location).query
        )


def test_discourse_prefixed_userinfo_attributes(client, discourse_nonce, auth_data):
    """Test the that discourse prefixed userinfo maps correctly to sso attributes without the prefix"""
    auth_data["userinfo"]["discourse_admin"] = True

    with client.session_transaction() as session:
        session.update(discourse_nonce)
        session.update(auth_data)

    res = client.get("/sso/auth")
    assert res.status_code == 302
    # Reconstruct query parameters encoded in the sso query parameter
    query = urlparse(res.location).query
    # - Extract everything after sso= (four letters) and before &
    query = str.split(query, "&")[0][4:]
    # - Decode the embedded query parameters
    query = b64decode(unquote(query)).decode("utf8")
    assert ("?admin=true" in query) or ("&admin=true" in query)


def test_required_sso_attributes(client, discourse_nonce, auth_data_custom_userinfo):
    """Test the that required sso attributes are enforced"""
    with client.session_transaction() as session:
        session.update(discourse_nonce)
        session.update(auth_data_custom_userinfo)

    res = client.get("/sso/auth")
    assert res.status_code == 403


def test_configured_userinfo_sso_map(discourse_nonce, auth_data_custom_userinfo):
    """Test the that userinfo to sso mapping can be configured"""
    with client_maker(
        {
            "USERINFO_SSO_MAP": {
                "a_very_unique_sub": "external_id",
                "preferred_username": "username",
                "a_very_unique_groups": "groups",
            }
        }
    ) as client:
        with client.session_transaction() as session:
            session.update(discourse_nonce)
            session.update(auth_data_custom_userinfo)

        res = client.get("/sso/auth")
        assert res.status_code == 302
        assert urlparse(res.location).path == "/session/sso_login"
        assert (
            urlparse(res.location).query
            == "sso=bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGImZXh0ZXJuYWxfaWQ9am9obl9kb2UmZW1haWw9am9obl9kb2UlNDBleGFtcGxlLmNvbSZuYW1lPUpvaG4lMjBEb2UmdXNlcm5hbWU9am9obl9kb2U%3D&sig=75c84a0093669181d88602eafdb2ea2f06b29e1f1dec6887c262c070a9982617"
        )


def test_configured_default_sso_attributes(discourse_nonce, auth_data):
    """Test the that userinfo to sso mapping can be configured"""
    with client_maker(
        {
            "DEFAULT_SSO_ATTRIBUTES": {
                "username": "should_not_be_found",
                "groups": "should_be_found",
                "something_extra": "should_also_be_found",
            }
        }
    ) as client:
        with client.session_transaction() as session:
            session.update(discourse_nonce)
            session.update(auth_data)

        res = client.get("/sso/auth")
        assert res.status_code == 302
        assert urlparse(res.location).path == "/session/sso_login"
        # Reconstruct query parameters encoded in the sso query parameter
        query = urlparse(res.location).query
        # - Extract everything after sso= (four letters) and before &
        query = str.split(query, "&")[0][4:]
        # - Decode the embedded query parameters
        query = b64decode(unquote(query)).decode("utf8")
        assert "should_not_be_found" not in query
        assert "should_be_found" in query
        assert "should_also_be_found" in query


def test_dynamic_oidc_configuration():
    """Test the that scope can be configured"""
    with client_maker(
        {
            "OIDC_CLIENT_ID": "a_very_unique_client_id",
            "OIDC_CLIENT_SECRET": "a_very_unique_client_secret",
            "OIDC_SCOPE": "a_very_unique_scope",
        }
    ) as client:
        res = client.get("/sso/auth")
        assert res.status_code == 302
        assert "a_very_unique_client_id" in urlparse(res.location).query
        assert "a_very_unique_scope" in urlparse(res.location).query


def test_static_oidc_configuration_issuer():
    """Test the that scope can be configured"""
    with client_maker(
        {
            "OIDC_PROVIDER_METADATA": {
                "issuer": "https://op.example.com",
                "authorization_endpoint": "https://op.example.com/a_very_unique_auth",
            },
        }
    ) as client:
        res = client.get("/sso/auth")
        assert res.status_code == 302
        assert urlparse(res.location).netloc == "op.example.com"
        assert urlparse(res.location).path == "/a_very_unique_auth"
