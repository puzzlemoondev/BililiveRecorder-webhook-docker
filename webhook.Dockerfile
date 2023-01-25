FROM golang AS build
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

FROM ubuntu AS webhook
RUN apt-get update && \
    apt-get install -y jq
COPY --from=webhook-build /usr/local/bin/webhook /usr/local/bin/webhook
COPY --from=baidupcs-go-build /usr/local/bin/baidupcs-go /usr/local/bin/baidupcs-go
COPY --from=aliyunpan-build /usr/local/bin/aliyunpan /usr/local/bin/aliyunpan
ENV PATH=/usr/local/bin:$PATH
VOLUME [ "/etc/webhook" ]
EXPOSE 9000
ENTRYPOINT [ "webhook" ]
CMD [ "-verbose", "-hooks=/etc/webhook/hooks.json", "-hotreload" ]