# Discourse SSO to OIDC bridge

This is a python flask app that, that when hosted, can be used as an endpoint for Discourse when setting up it's SSO. While you can utilize OIDC directly, it comes with some limitations, see [this discussion](https://meta.discourse.org/t/sso-vs-oauth2-difference/76543/11).

## Development notes


### Python package setup

See: https://packaging.python.org/tutorials/packaging-projects/

```
# install things required for development
python3 -m pip install --user --upgrade setuptools wheel
python3 -m pip install --user --upgrade twine

# generate the package
python3 setup.py sdist bdist_wheel

# upload the package
python3 -m twine upload --skip-existing --repository-url https://test.pypi.org/legacy/ --username consideratio dist/*

# install package
python3 -m pip install --index-url https://test.pypi.org/simple/ discourse-sso-oidc-bridge-consideratio
```
