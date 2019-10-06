FROM kennethreitz/pipenv as build

ADD . /media_analyzer
WORKDIR /media_analyzer

# RUN apt-get update && apt-get install -y libpq-dev

RUN pipenv install \
 && pipenv lock -r > requirements.txt \
 && pipenv run python setup.py bdist_wheel

# ----------------------------------------------------------------------------
FROM python:3.6-alpine

# ARG DEBIAN_FRONTEND=noninteractive

COPY --from=build /media_analyzer/dist/*.whl ./
COPY  ./media_analyzer/api_keys.ini /usr/local/lib/python3.6/site-packages/media_analyzer/
COPY  ./media_analyzer/core/tweet.avsc /usr/local/lib/python3.6/site-packages/media_analyzer/core/

RUN apk --no-cache add libpq
RUN apk --no-cache add --virtual .builddeps \
    gcc \
    postgresql-dev \
    gfortran \
    musl-dev \
    g++ \
 && pip3 install *.whl \
 && apk del .builddeps \
 && rm -rf /root/.cache \
 && rm -f *.whl


COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["pull"]
