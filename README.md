# Discourse SSO OIDC Bridge - A Python PyPI package

This Python package contains a Flask application that when deployed can be used
as and endpoint for Discourse when setting up it's SSO. It will then be able to
wrap a OIDC provider and avoid various [limitations](https://meta.discourse.org/t/sso-vs-oauth2-difference/76543/11)
of not being setup as a Discourse SSO provider.

This repo was made standing on the shoulders giants who made most of the initial
work. Thank you [__@fmarco76__](https://github.com/fmarco76) and [__@stevenmirabito__](https://github.com/stevenmirabito)!

- https://github.com/fmarco76/DiscourseSSO
- https://github.com/ComputerScienceHouse/DiscourseOIDC

I also did some refinements thanks to [__@greut__](https://github.com/greut) this [Medium article](https://medium.com/@greut/building-a-python-package-a-docker-image-using-pipenv-233d8793b6cc).

## Installation

Note that this is only a Flask application, you must use `gunicorn` or another
WSGI compatible webserver to host it and setup TLS etc.

> __WARNING__: Not yet tested with Discourse to function, but I'm working on it!

```sh
# NOTE: Currently onnly on PyPI's test servers
pip install --upgrade discourse-sso-oidc-bridge-consideratio
```

## Bridge Configuration

This is the common configuration that, [default.py](discourse-sso-oidc-bridge/default.py).

| __Config / ENV name__     | __Description__ |
|---------------------------|-|
| `SERVER_NAME`             | The domain where you host this app, example: `"discourse-sso.example.com"`. Note that `https://` will be assumed. |
| `SECRET_KEY`              | A secret for Flask, just generate one with `openssl rand -hex 32`. |
| `OIDC_ISSUER`             | An URL to the OIDC issuer. To verify you get this right you can try appending `/.well-known/openid-configuration` to it and see if you get various JSON details rather than a 404. |
| `OIDC_CLIENT_ID`          | A preregistered `client_id` on your OIDC issuer. |
| `OIDC_CLIENT_SECRET`      | The provided secret for the the preregistered `OIDC_CLIENT_ID`. |
| `OIDC_SCOPE`              | Comma seperated OIDC scopes, defaults to `"openid,profile"`. |
| `DISCOURSE_URL`           | The URL of your Discourse deployment, example `"https://discourse.example.com"`. |
| `DISCOURSE_SECRET_KEY`    | A shared secret between the bridge and Discourse, generate one with `openssl rand -hex 32`. |
| `USERINFO_SSO_MAP`        | Valid JSON object in a string mapping OIDC userinfo attribute names to to Discourse SSO attribute names. |
| `DEFAULT_SSO_ATTRIBUTES`  | Valid JSON object in a string mapping Discourse SSO attributes to default values. By default `sub` is mapped to `external_id` and `preferred_username` to `username`. |
| `CONFIG_LOCATION`         | The path to a Python file to be loaded as config where `OIDC_ISSUER` etc. could be set. |

## OIDC Provider Configuration

You must have a `client_id` and `client_secret` from your OIDC issuer. The
issuer must also accept redirecting back to `<bridge_url>/redirect_uri`, which
for example could be `https://discourse-sso.example.com/redirect_uri`.

## Development Notes

### To make changes and test them

1. Clone the repo

2. Install `pipenv` using `pip`.

    ```sh
    pip install pipenv
    ```

3. Setup a virtual development environment

    ```sh
    pipenv install --dev

    # Optionally enter the environment
    pipenv shell
    ```

4. Run tests

    ```sh
    pipenv run pytest
    ```

### Build and upload a PyPI release

1. Test, build and upload the package

    ```sh
    # Make sure you are up to date with what you have declared to require
    pipenv install --dev

    # Update changelog, fix requirements, etc.
    pipenv lock -r > requirements.txt

    # Run tests
    pipenv run pytest

    # Optionally commit and tag to influence the PyPI version
    # PBR will look for the latest tag and then append development
    # versions based on your git commits since the latest tag.
    git add .
    git commit
    git tag -a <package-version>

    # Build the package
    pipenv run python setup.py bdist_wheel

    # Upload the package to PyPI
    pipenv run twine upload --skip-existing --username consideratio dist/*
    ```

2. Build, run, and push a Docker image

    ```sh
    TAG=$(pipenv run python -c 'from pbr.version import VersionInfo; print(VersionInfo("discourse_sso_oidc_bridge").version_string())')
    docker build -t consideratio/discourse-sso-oidc-bridge:$TAG .
    docker run --rm consideratio/discourse-sso-oidc-bridge:$TAG
    docker push consideratio/discourse-sso-oidc-bridge:$TAG
    ```
