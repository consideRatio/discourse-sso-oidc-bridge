#!/usr/bin/env python3

import sys
from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()

setup(
    name="discourse-sso-oidc-bridge-consideratio",
    description="A Flask app, wrapping a single OpenID Connect issuer with a Discourse SSO provider interface.",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    py_modules=["discourse-sso-oidc-bridge-consideratio"],
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Erik Sundell",
    author_email="erik+pypi@sundellopensource.se",
    url="https://github.com/consideratio/discourse-sso-oidc-bridge",
    license="Apache License 2.0",
    platforms="Linux, Mac OS X",
    keywords=["discourse", "oidc", "sso"],
    python_requires=">=3.6",
    install_requires=[
        "flask-pyoidc==3.7.*",
        "flask==2.0.*",
        "healthcheck",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
