FROM alpine:edge

HEALTHCHECK --interval=20s CMD curl --max-time 3 --connect-timeout 2 -sSf http://127.0.0.1:8888/sitemap.xml || exit 1

RUN \
  apk add --no-cache curl python3 py3-flask py3-gevent \
  && pip3 install --no-cache-dir urllib3[secure] sitemap_python

COPY sitemap_from_json.py /opt/

ARG APP_CONFIG_VERSION
ENV APP_CONFIG_VERSION ${APP_CONFIG_VERSION:-unknown}

EXPOSE 8888

CMD python3 /opt/sitemap_from_json.py

