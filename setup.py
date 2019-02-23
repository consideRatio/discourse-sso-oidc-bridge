import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="discourse-sso-oidc-bridge-consideratio",
    version="0.0.1",
    author="Erik Sundell",
    author_email="erik.i.sundell@gmail.com",
    description="This flask app can help setup Discourse SSO through OIDC.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/consideratio/discourse-sso-oidc-bridge",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
