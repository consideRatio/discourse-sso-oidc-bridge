
# docker build -t discourse-sso-oidc-bridge:0.0.4 .
FROM tiangolo/uwsgi-nginx-flask:python3.6

ENV LISTEN_PORT 8080
EXPOSE 8080

# RUN pip install --upgrade discourse-sso-oidc-bridge-consideratio

# RUN useradd -m -s /bin/bash -N -u 1000 bridge

COPY ./discourse_sso_oidc_bridge /app/pkg/discourse_sso_oidc_bridge
COPY ./README.md /app/pkg
COPY ./setup.py /app/pkg

ENV PATH=$PATH:/root/.local/bin
# RUN chown -R bridge /app

# USER bridge
RUN pip install --user -e /app/pkg
# USER root

# RUN touch \
#         /etc/nginx/conf.d/nginx.conf \
#         /etc/nginx/conf.d/upload.conf \
#         /var/run/supervisor.sock \
#     && \
#     chown bridge \
#         /etc/nginx/nginx.conf \
#         /etc/nginx/conf.d/nginx.conf \
#         /etc/nginx/conf.d/upload.conf \
#         /var/run

# RUN chown -R bridge \
#     /var/log \
#     /etc/supervisor

# RUN usermod -a -G www-data bridge
# RUN usermod -a -G nginx bridge

# USER bridge

COPY image/main.py /app/main.py
