# Available on DockerHub as: consideratio/discourse-sso-oidc-bridge

# This Dockerfile was founded on the work of Yoan Blanc (@greut):
# https://github.com/greut/pipenv-to-wheel/blob/master/Dockerfile

# A good primitive test to verify everything isn't broken is to
# verify a container can start without errors.
# docker build --tag discourse-sso-oidc-bridge:local . && docker run --rm discourse-sso-oidc-bridge:local

FROM python:3.9 as build

ADD . /app
WORKDIR /app

RUN python setup.py bdist_wheel

# ----------------------------------------------------------------------------
FROM ubuntu:focal

ARG DEBIAN_FRONTEND=noninteractive

COPY --from=build /app/dist/*.whl .
COPY requirements.txt .

RUN set -xe \
 && apt-get update -q \
 && apt-get install -y -q \
        python3-minimal \
        python3-pip \
        python3-wheel \
        uwsgi-plugin-python3 \
 && python3 -m pip install -r requirements.txt *.whl \
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
