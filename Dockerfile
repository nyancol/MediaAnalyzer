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

RUN apk --no-cache add --virtual .builddeps \
    gcc \
    postgresql-dev \
    gfortran \
    musl-dev \
    libpq \
    g++ \
 && pip3 install *.whl \
 && apk del .builddeps \
 && rm -rf /root/.cache \
 && rm -f *.whl

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["pull"]
