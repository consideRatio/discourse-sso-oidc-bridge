# Copyright 2015 INFN
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
SSO Application tests
"""

import time
from flask import url_for
import pytest
from urllib.parse import urlparse
from discourse_sso_oidc_bridge.app import create_app

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


@pytest.fixture
def auth_data():
    return {
        'access_token': 'test_access_token',
        'id_token': {
            'iss': 'issuer1',
            'aud': 'client1',
            'sub': 'john_doe',
            'name': 'John Doe',
            'iat': 1550961213,
            'exp': 1550964813,
        },
        # INSPECT id_token_jwt at:
        # https://jwt.io/#debugger-io?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJpc3N1ZXIxIiwiYXVkIjoiY2xpZW50MSIsInN1YiI6ImpvaG5fZG9lIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTUwOTYxMjEzLCJleHAiOjE1NTA5NjQ4MTN9.eiBu_D5m4vPVd11C-phlKkHha2VPlmaRQPTuV49QTIk
        'id_token_jwt': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
                        '.eyJpc3MiOiJpc3N1ZXIxIiwiYXVkIjoiY2xpZW50MSIsInN1YiI6ImpvaG5fZG9lIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTUwOTYxMjEzLCJleHAiOjE1NTA5NjQ4MTN9'
                        '.eiBu_D5m4vPVd11C-phlKkHha2VPlmaRQPTuV49QTIk',
        'userinfo': {
            'sub': 'john_doe',
            'name': 'John Doe',
            'email': 'john_doe@example.com',
            'preferred_username': 'john_doe',
        },
        'last_authenticated': time.time(),
    }


@pytest.fixture
def discourse_nonce():
    return {
        'discourse_nonce': 'nonce=cb68251eefb5211e58c00ff1395f0c0b',
    }


def test_payload_check(client):
    """Test the payload is properly managed and the user is sent to the
    authentication page
    """
    with client.get(
        '/sso/login?sso=bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGI%3D%0A&'
        'sig=d87265a513d3fa4c7602ada38cfa60318c9804da6c95785ab36885dc79641671'
    ) as res:
        assert res.status_code == 302
        assert urlparse(res.location).path == '/sso/auth'


def test_bad_payload_sig(client):
    """Test the error code 400 is sent if the signature do not match
    the payload
    """
    with client.get(
        '/sso/login?sso=bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGI%3D%0A&'
        'sig=2828aa29899722b35a2f191d34ef9b3ce695e0e6eeec47deb46d588d70c7cb58'
    ) as res:
        assert res.status_code == 400


def test_no_payload(client):
    """Test the error code 400 is sent if the sso field is not provided"""
    with client.get(
        '/sso/login?sig=2828aa29899722b35a2f191d34ef9b3ce695e0e6eeec47deb46d588d70c7cb56'
    ) as res:
        assert res.status_code == 400


def test_no_hash(client):
    """Test the error code 400 is sent if the sig field is not provided"""
    with client.get(
        '/sso/login?sso=bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGI%3D%0A&'
    ) as res:
        assert res.status_code == 400


def test_authentication_state_not_available(client, discourse_nonce):
    """Test the authentication are properly send to Discourse"""
    with client.session_transaction() as session:
        session.update(discourse_nonce)

    res = client.get('/sso/auth')
    assert res.status_code == 302
    assert '?client_id=dummy_client_id&response_type=code&scope=openid+profile&redirect_uri=http%3A%2F%2Fdiscourse-sso.example.com%2Fredirect_uri' in res.location


def test_authentication_state_available(client, discourse_nonce, auth_data):
    """Test the authentication are properly send to Discourse"""
    with client.session_transaction() as session:
        session.update(discourse_nonce)
        session.update(auth_data)

    res = client.get('/sso/auth')
    assert res.status_code == 302
    assert res.location == 'https://discourse.example.com/session/sso_login?sso=bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGImZW1haWw9am9obl9kb2UlNDBleGFtcGxlLmNvbSZuYW1lPUpvaG4lMjBEb2UmdXNlcm5hbWU9am9obl9kb2UmZXh0ZXJuYWxfaWQ9am9obl9kb2U%3D&sig=4e4617a08d20f8380e10ba801879e79700cd14051da6341fc93c8563d50a155e'
