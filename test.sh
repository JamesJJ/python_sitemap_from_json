#!/bin/bash

BASE="ops/web-sitemap"

TAG="test-$(date -u '+%Y%m%d')-$(git log | head -n 1 | sed 's/^commit //')"

which autopep8
if [ $? -eq 0 ]
then
  autopep8 -a -a -a -a --ignore-local-config --in-place sitemap_from_json.py
else
  echo '**** "autopep8" not found. Please run "pip3 install --upgrade autopep8" to install it ****'
  sleep 30
fi

docker build --build-arg "APP_CONFIG_VERSION=${TAG}" -t "${BASE}:${TAG}" .  \
  && docker run --env LOG_LEVEL="DEBUG" -it -p 8888:8888 "${BASE}:${TAG}"

echo
echo "${BASE}:${TAG}"
echo


