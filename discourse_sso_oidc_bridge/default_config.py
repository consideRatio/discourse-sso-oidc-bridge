"""
Default configuration for FLASK app
"""

import os, json

class DefaultConfig(object):
    #######################
    # Flask Configuration #
    #######################

    DEBUG = str.lower(os.environ.get('DEBUG', '')) == 'true'
    IP = os.environ.get('IP', '0.0.0.0')
    PORT = int(os.environ.get('PORT', '8080'))
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME', 'https')
    # IMPORTANT: If you leave SERVER_NAME set to something that isn't
    # how you access it from a browser, then a 'Host' header will not
    # match a rule setup how to redirect the traffic. So you will end
    # up will a 404 response.
    # To fiddle around with this, you can try:
    # curl -H 'Host: discourse-sso.example.com' http://localhost:8080/
    # curl -H 'Host: something.else.com' http://localhost:8080/
    # If it works, you should be redirected (302) rather than get 404.
    SERVER_NAME = os.environ.get('SERVER_NAME', 'discourse-sso.example.com')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dummy_secret_key')

    ################################
    # OpenID Connect Configuration #
    ################################

    # For _dynamic_ provider configuration (recommended)
    # The issuer should be what you can append '.well-known/openid-configuration' to and get a valid response
    # https://github.com/zamzterz/Flask-pyoidc#dynamic-provider-configuration
    OIDC_ISSUER = os.environ.get('OIDC_ISSUER', 'https://login.salesforce.com/')

    OIDC_CLIENT_ID = os.environ.get('OIDC_CLIENT_ID', 'dummy_client_id')
    OIDC_CLIENT_SECRET = os.environ.get('OIDC_CLIENT_SECRET', 'dummy_client_secret')
    OIDC_SCOPE = os.environ.get('OIDC_SCOPE', 'openid,profile')
    OIDC_EXTRA_AUTH_REQUEST_PARAMS = json.loads(os.environ.get('OIDC_EXTRA_AUTH_REQUEST_PARAMS', '{}'))

    # Advanced OpenID Connect config: probably best to ignore...
    # --------------------------------------------------------------------------
    # For _static_ provider configuration (not recommended)
    # https://github.com/zamzterz/Flask-pyoidc#static-provider-configuration
    OIDC_PROVIDER_METADATA = json.loads(os.environ.get('OIDC_PROVIDER_METADATA', '{}'))

    ###########################
    # Discourse Configuration #
    ###########################

    # Discourse URL to send the user back
    DISCOURSE_URL = os.environ.get('DISCOURSE_URL', 'https://discourse.example.com')

    # Secret key shared with the Discourse server
    DISCOURSE_SECRET_KEY = os.environ.get('DISCOURSE_SECRET_KEY', 'dummy_discourse_secret_key')

    ########################
    # Bridge Configuration #
    ########################

    # You can provide a file path for an additional config file to be consumed
    # by setting the environment variable CONFIG_LOCATION.
    # Example: CONFIG_LOCATION='/var/discourse-sso-oidc-bridge/config.py'
    # Example content of the provided config:
    #
    # DISCOURSE_URL = "https://discourse."
    # OIDC_ISSUER = "https://my-okta-instance.okta.com/"
    # OIDC_CLIENT_ID = "ac8t5ngz91"
    # OIDC_CLIENT_SECRET = "lkjasdlfkhj21l3hjtkgjbsdv"

    # Attribute to read from the environment after user validation. Pass a valid
    # JSON object as a string where keys are userinfo attributes from OIDC and
    # values are Discourse SSO attribute they should map to.
    USERINFO_SSO_MAP = json.loads(
        os.environ.get('USERINFO_SSO_MAP',
            """
            {
                "sub": "external_id",
                "preferred_username": "username"
            }
            """
        )
    )

    # If you want some default values to be sent back to discourse, you can add
    # such defaults here. Note that you probably only want to set those that
    # discourse knows about.
    # See: https://github.com/discourse/discourse/blob/master/lib/single_sign_on.rb
    # Example JSON formatted string that could be passed.
    # """
    # {
    #     "add_groups": "crazy_cat_club",
    #     "locale": "sv",
    #     "suppress_welcome_message": "true"
    # }
    # """
    DEFAULT_SSO_ATTRIBUTES = json.loads(os.environ.get('DEFAULT_SSO_ATTRIBUTES', '{}'))
