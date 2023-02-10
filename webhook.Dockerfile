FROM golang AS build
ENV GOPROXY https://proxy.golang.com.cn,direct
RUN apt-get update && \
    apt-get install -y wget
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

FROM continuumio/miniconda3 AS worker
COPY --from=baidupcs-go-build /usr/local/bin/baidupcs-go /usr/local/bin/baidupcs-go
COPY --from=aliyunpan-build /usr/local/bin/aliyunpan /usr/local/bin/aliyunpan
ENV POETRY_VERSION 1.3.1
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false
RUN conda install -c conda-forge gcc 'python>=3.11' poetry=${POETRY_VERSION}
WORKDIR /action
COPY ./action .
RUN poetry install
ENTRYPOINT [ "poetry", "run" ]

FROM worker AS webhook
COPY --from=webhook-build /usr/local/bin/webhook /usr/local/bin/webhook
VOLUME [ "/etc/webhook" ]
EXPOSE 9000
ENTRYPOINT [ "webhook" ]