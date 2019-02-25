"""
Delayed advanced configuration for the Flask app
"""

import os, json
class DelayedConfig(object):
    # Advanced OpenID Connect config: probably best to ignore...
    # --------------------------------------------------------------------------
    # For _static_ provider configuration (not recommended)
    # https://github.com/zamzterz/Flask-pyoidc#static-provider-configuration
    OIDC_PROVIDER_METADATA = json.loads(os.environ.get('OIDC_PROVIDER_METADATA', '{}'))
    
    # FIXME: Issue #1 - Imagine a user overriding the configuration value of
    # SERVER_NAME instead of setting it through an environment variable...
    # Environment ariables are loaded before and set before this config code
    # is executed, but an external config may not be...
    # Perhaps we can attempt to load config from CONFIG_LOCATION from here?
    OIDC_LOGOUT_REDIRECT_URI = os.environ.get('OIDC_LOGOUT_REDIRECT_URI', 'https://' + SERVER_NAME + '/logout')
 
    # FIXME: Another issue #1.
    OIDC_CLIENT_METADATA = {
        'client_id': OIDC_CLIENT_ID,
        'client_secret': OIDC_CLIENT_SECRET,
        'post_logout_redirect_uris': [OIDC_LOGOUT_REDIRECT_URI]
    }

    # FIXME: Another issue #1.
    OIDC_AUTH_REQUEST_PARAMS = json.loads(
        os.environ.get('OIDC_AUTH_REQUEST_PARAMS',
            f"""
            {{
                "scope": {json.dumps(str.split(OIDC_SCOPE, ","))}
            }}
            """
        )
    )