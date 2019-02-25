"""
SSO FLASK Application for Discourse
The configuration file is defined with the variable "DISCOURSE_SSO_CONFIG",
for the most significant values look at the sso/default.py file
"""

from flask import abort, Flask, redirect, render_template, request, url_for, session
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ProviderMetadata, ClientMetadata

import os
import base64
import hashlib
import hmac
import requests
import json
from urllib.parse import quote
from .constants import ALL_ATTRIBUTES, BOOL_ATTRIBUTES, REQUIRED_ATTRIBUTES
from .default_config import DefaultConfig

# Disable SSL certificate verification warning
requests.packages.urllib3.disable_warnings()

def create_app(config):
    app = Flask(__name__, instance_relative_config=True)

    # Load application config from various sources
    # ------------------------------------------------------------------------------
    # 1. Defaults from this package
    app.config.from_object(DefaultConfig)

    # 2. From a config.py file in the application directory
    app.config.from_pyfile(
        filename=os.path.join(os.getcwd(), "config.py"),
        silent=True
    )

    # 3. From a dynamically configurable file location
    if os.environ.get('CONFIG_LOCATION'):
        app.config.from_pyfile(
            filename=os.environ.get('CONFIG_LOCATION'),
            silent=False
        )
    
    # 4. Testing config
    if config:
        app.config.from_mapping(config)
    
    # 5. Load some final computed config
    #    NOTE: This is placed here as it relies on other config values that
    #          may be configured after the user provided config for example.
    oidc_logout_redirect_uri = os.environ.get('OIDC_LOGOUT_REDIRECT_URI', 'https://' + app.config['SERVER_NAME'] + '/logout')
    app.config.from_mapping({
        'OIDC_LOGOUT_REDIRECT_URI': oidc_logout_redirect_uri,
        'OIDC_CLIENT_METADATA': {
            'client_id': app.config['OIDC_CLIENT_ID'],
            'client_secret': app.config['OIDC_CLIENT_SECRET'],
            'post_logout_redirect_uris': str.split(oidc_logout_redirect_uri, ",")
        },
        'OIDC_AUTH_REQUEST_PARAMS': json.loads(
            os.environ.get('OIDC_AUTH_REQUEST_PARAMS',
                f"""
                {{
                    "scope": {json.dumps(str.split(app.config['OIDC_SCOPE'], ","))}
                }}
                """
            )
        ),
    })


    # Initialize OpenID Connect extension
    # ------------------------------------------------------------------------------

    # The client metadata will be consumed no matter what...
    # https://github.com/zamzterz/Flask-pyoidc#dynamic-provider-configuration
    client_metadata = ClientMetadata(**app.config['OIDC_CLIENT_METADATA'])

    # ... but if explicit OIDC provider information is provided, we use that
    # instead of the information dynamically provided by the
    # .well-known/openid-configuration endpoint.
    if app.config['OIDC_PROVIDER_METADATA']:
        provider_metadata = ProviderMetadata(**app.config['OIDC_PROVIDER_METADATA'])
        provider = ProviderConfiguration(
            provider_metadata=provider_metadata,
            client_metadata=client_metadata,
            auth_request_params=app.config['OIDC_AUTH_REQUEST_PARAMS'],
        )
    else:
        provider = ProviderConfiguration(
            issuer=app.config['OIDC_ISSUER'],
            client_metadata=client_metadata,
            auth_request_params=app.config['OIDC_AUTH_REQUEST_PARAMS'],
        )

    auth = OIDCAuthentication(
        provider_configurations={
            'default': provider,
        },
        app=app,
    )


    @app.route('/')
    def index():
        """
        If a user tries to access this application directly,
        just redirect them to Discourse.
        :return: Redirect to the configurated DISCOURSE_URL
        """
        return redirect(app.config.get('DISCOURSE_URL'), 302)


    @app.route('/sso/login')
    def payload_check():
        """
        Verify the payload and signature coming from a Discourse server and if
        correct redirect to the authentication page after saving the nonce in
        the session as discourse_nonce.
        
        :return: The redirection page to the authentication page
        """

        # Get payload and signature from Discourse request
        payload = request.args.get('sso', '')
        signature = request.args.get('sig', '')

        if not payload or not signature:
            abort(400)

        app.logger.debug('Request to login with payload="%s" signature="%s"', payload, signature)
        app.logger.debug('Session Secret Key: %s', app.secret_key)
        app.logger.debug('SSO Secret Key: %s', app.config.get('DISCOURSE_SECRET_KEY'))

        # Calculate and compare request signature
        dig = hmac.new(app.config.get('DISCOURSE_SECRET_KEY', '').encode('utf-8'),
                    payload.encode('utf-8'),
                    hashlib.sha256).hexdigest()
        app.logger.debug('Calculated hash: %s', dig)

        if dig != signature:
            abort(400)

        # Decode the payload and store in session
        decoded_msg = base64.b64decode(payload).decode('utf-8')
        session['discourse_nonce'] = decoded_msg  # This can't just be 'nonce' as Flask-pyoidc will steamroll it

        # Redirect to authorization endpoint
        return redirect(url_for('sso_auth'))


    @app.route('/sso/auth')
    @auth.oidc_auth('default')
    def sso_auth():
        """
        Read the user attributes provided by Flask-pyoidc and
        create the payload to send to Discourse.
        :return: The redirection page to Discourse
        """

        # Check to make sure we have a valid session
        if 'discourse_nonce' not in session:
            app.logger.debug('Discourse nonce not found in session, arriving to /sso/auth without coming from /sso/login?')
            abort(403)

        attribute_map = app.config.get('USERINFO_SSO_MAP')

        sso_attributes = {}
        userinfo = session['userinfo']

        # Check if the provided userinfo should be used to set information to be
        # passed to discourse. Do it by checking if the userinfo field is...
        # 1. explicitly mapped using the provided map 
        # 2. if it can match one of the known attributes with discourse_ prefixed
        # 3. if it can match one of the known attributes directly
        for userinfo_key, userinfo_value in userinfo.items():
            attribute_key = attribute_map.get(userinfo_key)

            if attribute_key:
                pass
            elif ("discourse_" + userinfo_key) in ALL_ATTRIBUTES:
                attribute_key = "discourse_" + userinfo_key
            elif userinfo_key in ALL_ATTRIBUTES:
                attribute_key = userinfo_key

            if attribute_key:
                if attribute_key in BOOL_ATTRIBUTES:
                    userinfo_value = "false" if str.lower(str(userinfo_value)) in ['false', 'f', '0'] else "true"
                sso_attributes[attribute_key] = userinfo_value
        
        # Check if we have a default value that should be utilized
        print(sso_attributes)
        default_sso_attributes = app.config.get('DEFAULT_SSO_ATTRIBUTES')
        for default_attribute_key, default_attribute_value in default_sso_attributes.items():
            if default_attribute_key not in sso_attributes:
                sso_attributes[default_attribute_key] = default_attribute_value

        # Check if we got the required attributes
        for required_attribute in REQUIRED_ATTRIBUTES:
            if not sso_attributes.get(required_attribute):
                app.logger.debug(f'{required_attribute} not found in userinfo: ' + json.dumps(session['userinfo']))
                abort(403)

        # All systems are go!
        app.logger.debug(f'Authenticating "{sso_attributes.get("external_id")}", named "{sso_attributes.get("name")}" with email: "{sso_attributes.get("email")}"')

        # Construct the response inner query parameters
        query = session['discourse_nonce']
        for sso_attribute_key, sso_attribute_value in sso_attributes.items():
            query += f'&{sso_attribute_key}={quote(sso_attribute_value)}'
        app.logger.debug('Query string to return: %s', query)

        # Encode response
        query_b64 = base64.b64encode(query.encode('utf-8'))
        app.logger.debug('Base64 query string to return: %s', query_b64)

        # Build URL-safe response
        query_urlenc = quote(query_b64)
        app.logger.debug('URLEnc query string to return: %s', query_urlenc)

        # Generate signature for response
        sig = hmac.new(app.config.get('DISCOURSE_SECRET_KEY').encode('utf-8'),
                    query_b64,
                    hashlib.sha256).hexdigest()
        app.logger.debug('Signature: %s', sig)

        # Build redirect URL
        redirect_url = (app.config.get('DISCOURSE_URL') +
                        '/session/sso_login?'
                        'sso=' + query_urlenc +
                        '&sig=' + sig)

        # Redirect back to Discourse
        return redirect(redirect_url)


    @app.route('/logout')
    @auth.oidc_logout
    def logout():
        """
        Handle logging a user out. Flask-pyoidc does the heavy lifting here.
        :return: Redirect to the application index
        """
        return redirect(url_for('index'), 302)


    @app.errorhandler(403)
    def attribute_not_provided(error):
        """
        Render a custom error page in case the IdP authenticate the user but does
        not provide the requested attributes
        :type error: object
        """
        return render_template('403.html'), 403

    return app
