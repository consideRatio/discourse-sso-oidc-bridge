
# consideratio/discourse-sso-oidc-bridge:<PyPI version>
FROM tiangolo/uwsgi-nginx-flask:python3.7

ENV LOCAL_PORT=8080
EXPOSE ${LOCAL_PORT}

# COPY ./discourse_sso_oidc_bridge /app/pkg/discourse_sso_oidc_bridge
# COPY ./README.md /app/pkg
# COPY ./setup.py /app/pkg
# RUN pip install --user -e /app/pkg
# COPY image/main.py /app/main.py

RUN pip install discourse_sso_oidc_bridge_consideratio
COPY ./main.py /app/main.py
