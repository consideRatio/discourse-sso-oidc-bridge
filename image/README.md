# About this image

The goal of this image is to host the `discourse_sso_oidc_bridge` Flask application using a webserver.

TAG=0.0.7 && docker build -t discourse-sso-oidc-bridge:$TAG . && docker run --rm -it -e SERVER_NAME=localhost -p 80:8080 discourse-sso-oidc-bridge:$TAG