FROM alpine AS build-go
RUN apk add --upgrade --no-cache wget musl-dev go
WORKDIR /build

FROM --platform=$BUILDPLATFORM alpine AS build-rust-source
RUN apk add --upgrade --no-cache wget musl-dev cargo
WORKDIR /source
RUN mkdir .cargo

FROM alpine AS build-rust
RUN apk add --upgrade --no-cache musl-dev cargo
WORKDIR /build

FROM alpine AS build-c
RUN apk add --upgrade --no-cache wget musl-dev gcc make
WORKDIR /build

FROM build-go AS webhook-build
ENV WEBHOOK_VERSION 2.8.0
RUN wget https://github.com/adnanh/webhook/archive/refs/tags/${WEBHOOK_VERSION}.tar.gz -O webhook.tar.gz && \
    tar -xzf webhook.tar.gz --strip 1 && \
    go build -o /webhook

FROM build-go AS aliyunpan-build
ENV ALIYUNPAN_VERSION 0.2.5
RUN wget https://github.com/tickstep/aliyunpan/archive/refs/tags/v${ALIYUNPAN_VERSION}.tar.gz -O aliyunpan.tar.gz && \
    tar -xzf aliyunpan.tar.gz --strip 1 && \
    go build -o /aliyunpan

FROM build-go AS baidupcs-build
ENV BAIDUPCS_VERSION 3.9.0
RUN wget https://github.com/qjfoidnh/BaiduPCS-Go/archive/refs/tags/v${BAIDUPCS_VERSION}.tar.gz -O baidupcs.tar.gz && \
    tar -xzf baidupcs.tar.gz --strip 1 && \
    go build -o /baidupcs

FROM build-rust-source AS biliup-source
ENV BILIUP_VERSION 0.1.15
RUN wget https://github.com/ForgQi/biliup-rs/archive/refs/tags/v${BILIUP_VERSION}.tar.gz -O biliup.tar.gz && \
    tar -xzf biliup.tar.gz --strip 1 && \
    cargo vendor > .cargo/config

FROM build-rust AS biliup-build
COPY --from=biliup-source /source /build
RUN cargo build --release --offline --bin biliup && \
    cp target/release/biliup /biliup

FROM build-c AS danmaku-factory-build
ENV DANMAKU_FACTORY_VERSION 1.63
RUN wget https://github.com/hihkm/DanmakuFactory/archive/refs/tags/v${DANMAKU_FACTORY_VERSION}.tar.gz -O DanmakuFactory.tar.gz && \
    tar -xzf DanmakuFactory.tar.gz --strip 1 && \
    make && \
    cp DanmakuFactory /DanmakuFactory

FROM python:alpine as recorder
RUN apk add --upgrade --no-cache aspnetcore6-runtime tzdata
ENV TZ=Asia/Shanghai
WORKDIR /recorder
COPY --from=bililive/recorder:2.6.2 /app .
EXPOSE 2356

FROM recorder as webhook
COPY --from=webhook-build /webhook /usr/local/bin/
COPY --from=aliyunpan-build /aliyunpan /usr/local/bin/
COPY --from=baidupcs-build /baidupcs /usr/local/bin/
COPY --from=biliup-build /biliup /usr/local/bin/
COPY --from=danmaku-factory-build /DanmakuFactory /usr/local/bin/
RUN apk add --upgrade --no-cache redis ffmpeg font-noto font-noto-cjk font-noto-emoji
RUN mkdir -p /var/supervisord /var/redis
WORKDIR /webhook
COPY ./webhook/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./webhook .
COPY ./hooks.json /etc/
COPY ./supervisord.conf /etc/
EXPOSE 5555 9001
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
