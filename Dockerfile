FROM golang AS build-go
WORKDIR /build

FROM gcc AS build-c
WORKDIR /build

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

FROM build-c AS danmaku-factory-build
ENV DANMAKU_FACTORY_VERSION 1.63
RUN wget https://github.com/hihkm/DanmakuFactory/archive/refs/tags/v${DANMAKU_FACTORY_VERSION}.tar.gz -O DanmakuFactory.tar.gz && \
    tar -xzf DanmakuFactory.tar.gz --strip 1 && \
    make && \
    cp DanmakuFactory /DanmakuFactory

FROM python:slim as recorder
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget && \
    wget https://dot.net/v1/dotnet-install.sh && \
    chmod +x dotnet-install.sh && \
    ./dotnet-install.sh -c 6.0 --runtime aspnetcore --install-dir /usr/local/bin && \
    apt-get purge -y --autoremove wget && \
    rm -rf dotnet-install.sh \
      /var/lib/apt/lists/*  \
      /tmp/*
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone
WORKDIR /recorder
COPY --from=bililive/recorder:2.6.2 /app .
EXPOSE 2356

FROM recorder as webhook
COPY --from=aliyunpan-build /aliyunpan /usr/local/bin/
COPY --from=baidupcs-build /baidupcs /usr/local/bin/
COPY --from=danmaku-factory-build /DanmakuFactory /usr/local/bin/
COPY --from=puzzlemoondev/biliup-rs /biliup /usr/local/bin/
COPY --from=puzzlemoondev/ffmpeg-static /ffmpeg /usr/local/bin/
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    webhook \
    redis-server \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/supervisord /var/redis
WORKDIR /webhook
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY webhook webhook
COPY hooks.json /etc/
COPY supervisord.conf /etc/
EXPOSE 5555 9001
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
