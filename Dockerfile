FROM golang:alpine AS build
RUN apk add --update --no-cache wget
WORKDIR /app

FROM build AS baidupcs-go-build
ENV BAIDUPCS_VERSION 3.9.0
RUN wget https://github.com/qjfoidnh/BaiduPCS-Go/archive/refs/tags/v${BAIDUPCS_VERSION}.tar.gz -O baidupcs-go.tar.gz && \
    tar -xzf baidupcs-go.tar.gz --strip 1 && \
    go get -d && \
    go build -o /usr/local/bin/baidupcs-go

FROM build AS aliyunpan-build
ENV ALIYUNPAN_VERSION 0.2.5
RUN wget https://github.com/tickstep/aliyunpan/archive/refs/tags/v${ALIYUNPAN_VERSION}.tar.gz -O aliyunpan.tar.gz && \
    tar -xzf aliyunpan.tar.gz --strip 1 && \
    go get -d && \
    go build -o /usr/local/bin/aliyunpan

FROM build AS webhook-build
ENV WEBHOOK_VERSION 2.8.0
RUN wget https://github.com/adnanh/webhook/archive/refs/tags/${WEBHOOK_VERSION}.tar.gz -O webhook.tar.gz && \
    tar -xzf webhook.tar.gz --strip 1 && \
    go get -d && \
    go build -o /usr/local/bin/webhook

FROM python:3.11-alpine as python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME=/opt/poetry \
    POETRY_VENV=/opt/poetry-venv \
    POETRY_CACHE_DIR=/opt/.cache \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

FROM python-base as poetry-base
ENV POETRY_VERSION 1.3.2
RUN apk add --update --no-cache gcc musl-dev libffi-dev && \
    python3 -m venv $POETRY_VENV && \
    $POETRY_VENV/bin/pip install -U pip setuptools supervisor && \
    $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}
WORKDIR /action
COPY ./action/pyproject.toml .
RUN $POETRY_VENV/bin/poetry install --no-cache --only main

FROM python-base as webhook
COPY --from=webhook-build /usr/local/bin/webhook /usr/local/bin/webhook
COPY --from=baidupcs-go-build /usr/local/bin/baidupcs-go /usr/local/bin/baidupcs-go
COPY --from=aliyunpan-build /usr/local/bin/aliyunpan /usr/local/bin/aliyunpan
COPY --from=poetry-base ${POETRY_VENV} ${POETRY_VENV}
ENV PATH="$PATH:$POETRY_VENV/bin"
RUN apk --no-cache --update add redis
RUN mkdir -p /var/supervisord /var/redis
COPY ./supervisord.conf /etc/supervisord.conf
EXPOSE 5555 9000 9001
ENTRYPOINT ["supervisord", "-c", "/etc/supervisord.conf"]