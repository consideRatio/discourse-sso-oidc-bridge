
# docker build -t discourse-sso-oidc-bridge:0.0.4 .
FROM tiangolo/uwsgi-nginx-flask:python3.7

# COPY ./discourse_sso_oidc_bridge /app/pkg/discourse_sso_oidc_bridge
# COPY ./README.md /app/pkg
# COPY ./setup.py /app/pkg
# RUN pip install --user -e /app/pkg
# COPY image/main.py /app/main.py

RUN pip install discourse_sso_oidc_bridge_consideratio
COPY ./main.py /app/main.py
