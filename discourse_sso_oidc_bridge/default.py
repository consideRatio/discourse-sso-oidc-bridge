"""
Default configuration for FLASK app
"""

import os, json

class Config(object):
    #######################
    # Flask Configuration #
    #######################

    DEBUG = True if os.environ.get('SSO_DEBUG', 'false') == 'true' else False
    IP = os.environ.get('SSO_IP', '0.0.0.0')
    PORT = int(os.environ.get('SSO_PORT', '8080'))
    
    SERVER_NAME = os.environ.get('SSO_SERVER_NAME', 'discourse-sso.example.com')
    SECRET_KEY = os.environ.get('SSO_SECRET_KEY', 'vWr,-n7NlGPv9SyIGBMr4ehwThUY92DpWPqIuh2NP_6Of-_8b3,h')

    ################################
    # OpenID Connect Configuration #
    ################################

    # For _dynamic_ provider configuration (recommended)
    # https://github.com/zamzterz/Flask-pyoidc#dynamic-provider-configuration
    # The issuer should be what you can append '.well-known/openid-configuration' to and get a valid response
    OIDC_ISSUER = os.environ.get('SSO_OIDC_ISSUER', 'https://login.salesforce.com/')

    # For _static_ provider configuration (not recommended)
    # https://github.com/zamzterz/Flask-pyoidc#static-provider-configuration
    OIDC_PROVIDER_METADATA = json.loads(
        os.environ.get('SSO_OIDC_PROVIDER_METADATA',
            """
            {}
            """
        )
    )

    OIDC_CLIENT_METADATA = {
        'client_id': os.environ.get('SSO_OIDC_CLIENT_ID', 'dummy_client_id'),
        'client_secret': os.environ.get('SSO_OIDC_CLIENT_SECRET', 'dummy_client_secret'),
        'post_logout_redirect_uris': [os.environ.get('SSO_OIDC_LOGOUT_REDIRECT_URI',
                                                    'https://' + SERVER_NAME + '/logout')]
    }
    OIDC_AUTH_REQUEST_PARAMS = json.loads(
        os.environ.get('SSO_OIDC_AUTH_REQUEST_PARAMS',
            """
            {
                "scope": ["openid", "profile"]
            }
            """
        )
    )

    ###########################
    # Discourse Configuration #
    ###########################

    # Discourse URL to send the user back
    DISCOURSE_URL = os.environ.get('SSO_DISCOURSE_URL', 'http://discourse.example.com')

    # Secret key shared with the Discourse server
    DISCOURSE_SECRET_KEY = os.environ.get('SSO_DISCOURSE_SECRET_KEY', 'dummy_discourse_secret_key')

    # Attribute to read from the environment after user validation
    DISCOURSE_USER_MAP = json.loads(
        os.environ.get('SSO_DISCOURSE_USER_MAP',
            # See: https://meta.discourse.org/t/official-single-sign-on-for-discourse-sso/13045
            """
            {
                "email": "email",
                "require_activation": "require_activation",
                "external_id": "sub",
                "username": "preferred_username",
                "name": "name",
                "bio": "profile",
                "avatar_url": "discourse_avatar_url",
                "avatar_force_update": "discourse_avatar_force_update",
                "admin": "discourse_admin",
                "moderator": "discourse_moderator",
                "suppress_welcome_message": "discourse_suppress_welcome_message"
            }
            """
        )
    )
