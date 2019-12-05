# Available on DockerHub as: consideratio/discourse-sso-oidc-bridge

# This Dockerfile was founded on the work of Yoan Blanc (@greut):
# https://github.com/greut/pipenv-to-wheel/blob/master/Dockerfile

# A good primitive test to verify everything isn't broken is to
# verify a container can start without errors.
# docker build --tag discourse-sso-oidc-bridge:local . && docker run --rm discourse-sso-oidc-bridge:local

FROM kennethreitz/pipenv as pipenv

ADD . /app
WORKDIR /app

RUN pipenv install --dev \
 && pipenv lock -r > requirements.txt \
 && pipenv run python setup.py bdist_wheel

# ----------------------------------------------------------------------------
FROM ubuntu:bionic

ARG DEBIAN_FRONTEND=noninteractive

COPY --from=pipenv /app/dist/*.whl .

RUN set -xe \
 && apt-get update -q \
 && apt-get install -y -q \
        python3-minimal \
        python3-lib2to3 \
        python3-wheel \
        python3-pip \
        python3-setuptools \
        uwsgi-plugin-python3 \
 && python3 -m pip install *.whl \
 && apt-get remove -y python3-pip python3-wheel \
 && apt-get autoremove -y \
 && rm -f *.whl \
 && rm -rf /root/.cache \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /app \
 && useradd _uwsgi --no-create-home --user-group

USER _uwsgi

ENTRYPOINT ["/usr/bin/uwsgi", \
            "--master", \
            "--die-on-term", \
            "--plugin", "python3"]

EXPOSE 8080
CMD ["--http-socket", "0.0.0.0:8080", \
     "--processes", "2", \
     "--buffer-size", "65535", \
     "--chdir", "/app", \
     "--module", "discourse_sso_oidc_bridge:app"]
