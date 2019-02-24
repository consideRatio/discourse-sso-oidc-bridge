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

import os
import time
from flask import url_for, session
from flask.testing import FlaskClient
import pytest
from urllib.parse import urlparse
from werkzeug.exceptions import BadRequest, Forbidden
from flask_pyoidc.user_session import UserSession
from discourse_sso_oidc_bridge import sso


@pytest.fixture
def data():
    return {
        'access_token': 'test_access_token',
        'id_token': {
            'iss': 'issuer1',
            'aud': 'client1',
            'sub': 'john_doe',
            'name': 'John Doe',
            'iat': 1550961213,
            'exp': 1550964813
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


def test_payload_check():
    """Test the payload is properly managed and the user is sent to the
    authentication page
    """
    with sso.app.test_request_context('/sso/login?sso=bm9uY2U9Y2I2ODI1MWVlZm'
                                    'I1MjExZTU4YzAwZmYxMzk1ZjBjMGI%3D%0A&'
                                    'sig=d87265a513d3fa4c7602ada38cfa60318'
                                    'c9804da6c95785ab36885dc79641671',
                                    method='GET'):
        res = sso.payload_check()
        assert res.status_code == 302
        assert urlparse(res.location).path == url_for('user_authz')

def test_bad_payload_sig():
    """Test the error code 400 is sent if the signature do not match
    the payload
    """
    with sso.app.test_request_context('/sso/login?sso=bm9uY2U9Y2I2ODI1MWVlZm'
                                    'I1MjExZTU4YzAwZmYxMzk1ZjBjMGI%3D%0A&'
                                    'sig=2828aa29899722b35a2f191d34ef9b3ce'
                                    '695e0e6eeec47deb46d588d70c7cb58',
                                    method='GET'):
        with pytest.raises(BadRequest):
            sso.payload_check()

def test_no_payload():
    """Test the error code 400 is sent if the sso field is not provided"""
    with sso.app.test_request_context('/sso/login?sig=2828aa29899722b35a2f191'
                                    'd34ef9b3ce695e0e6eeec47deb46d588d70c7c'
                                    'b56',
                                    method='GET'):
        with pytest.raises(BadRequest):
            sso.payload_check()

def test_no_hash():
    """Test the error code 400 is sent if the sig field is not provided"""
    with sso.app.test_request_context('/sso/login?sso=bm9uY2U9Y2I2ODI1MWVlZm'
                                    'I1MjExZTU4YzAwZmYxMzk1ZjBjMGI%3D%0A&',
                                    method='GET'):
        with pytest.raises(BadRequest):
            sso.payload_check()


def test_authentication_state_not_available(data):
    """Test the authentication are properly send to Discourse"""
    with sso.app.test_request_context('/sso/auth', method='GET') as req:
        req.session['discourse_nonce'] = 'nonce=cb68251eefb5211e58c00ff1395f0c0b'
        resp = sso.user_authz()
        assert resp.status_code == 302
        assert resp.location.startswith('https://login.salesforce.com/services/oauth2/authorize?client_id=dummy_client_id&response_type=code&scope=openid+profile&redirect_uri=http%3A%2F%2Fdiscourse-sso.example.com%2Fredirect_uri')


def test_authentication_state_available(data):
    """Test the authentication are properly send to Discourse"""
    with sso.app.test_request_context('/sso/auth', method='GET') as req:
        req.session['discourse_nonce'] = 'nonce=cb68251eefb5211e58c00ff1395f0c0b'
        UserSession(req.session, provider_name='default').update(**data)
        resp = sso.user_authz()
        assert resp.status_code == 302
        assert resp.location == 'http://discourse.example.com/session/sso_login?sso=bm9uY2U9Y2I2ODI1MWVlZmI1MjExZTU4YzAwZmYxMzk1ZjBjMGImZXh0ZXJuYWxfaWQ9am9obl9kb2UmbmFtZT1Kb2huJTIwRG9lJmVtYWlsPWpvaG5fZG9lJTQwZXhhbXBsZS5jb20mdXNlcm5hbWU9am9obl9kb2U%3D&sig=240679cc6a8a56fa47d6db681868466e1e166befa794d87a774049185a299598'


def test_error_page_403():
    """Test the correct error code is propagated"""
    with sso.app.test_request_context('/sso/auth',
                                    method='GET',
                                    environ_base={
                                        'givenName': 'sam',
                                        'sn': '',
                                        'username': 'samsam',
                                        'mail': 'test@test.com',
                                        'eppn': 'hello123'}
                                    ):
        resp = sso.attribuete_not_provided(None)
        assert resp[1] == 403
