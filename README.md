# BililiveRecorder-webhook-docker

[![Publish](https://github.com/puzzlemoondev/BililiveRecorder-webhook-docker/actions/workflows/publish.yml/badge.svg)](https://github.com/puzzlemoondev/BililiveRecorder-webhook-docker/actions/workflows/publish.yml)

Dockerized [BililiveRecorder](https://github.com/BililiveRecorder/BililiveRecorder) with biliup, baidupcs and aliyunpan upload webhook.

The [webhook](https://github.com/adnanh/webhook) server listens for `FileClosed` events, uploads files, and removes them after upload success.

[B 站专栏](https://www.bilibili.com/read/cv21367565)

## How to use

- Add a [`.env` file](https://docs.docker.com/compose/environment-variables/#the-env-file) with these variables. For baidupcs, provide both bduss and stoken. For aliyunpan, provide rtoken. Providing credentials for both platform at the same time triggers upload to both platform concurrently.
  - RECORDER_USER: username for BiliveRecorder
  - RECORDER_PASS: password for BiliveRecorder
  - BAIDUPCS_BDUSS: bduss for baidupcs login. See [baidupcs](https://github.com/qjfoidnh/BaiduPCS-Go#%E7%99%BB%E5%BD%95%E7%99%BE%E5%BA%A6%E5%B8%90%E5%8F%B7) for how to retrieve.
  - BAIDUPCS_STOKEN: stoken for baidupcs login. See [baidupcs](https://github.com/qjfoidnh/BaiduPCS-Go#%E7%99%BB%E5%BD%95%E7%99%BE%E5%BA%A6%E5%B8%90%E5%8F%B7) for how to retrieve.
  - ALIYUNPAN_RTOKEN: refresh token for aliyunpan login. See [aliyunpan](https://github.com/tickstep/aliyunpan#%E5%A6%82%E4%BD%95%E8%8E%B7%E5%8F%96RefreshToken) for how to retrieve.
- Run `docker compose up`
- Add webhook to settings
  - Go to Settings -> Webhook -> Webhook V2
  - Add this line: `http://webhook:9000/hooks/recorder-file-closed`

## Biliup Integration

- To use biliup, add your config yaml and cover files (optional) under `biliup`. This directory will be mounted to `/etc/biliup` in the container.
- See [here](https://biliup.github.io/biliup/Guide.html#%E5%AE%8C%E6%95%B4%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6%E7%A4%BA%E4%BE%8B) for full config file format. Note that only `user` and some of `streamers` fields are supported.
- `title` and `description` supports string interpolation. See sample.

### Sample `config.yml`

```
user:
  cookies:
    SESSDATA: "your SESSDATA"
    bili_jct: "your bili_jct"
    DedeUserID__ckMd5: "your DedeUserID__ckMd5"
    DedeUserID: "your DedeUserID"

streamers:
  "弥瑟里*": # supports unix glob syntax
    title: "【弥瑟里seri】%Y-%m-%dT%H:%M:%S录播_{title}"
    tid: 27
    copyright: 1
    tags:
      - 虚拟UP主
      - 直播
      - 录播
      - 直播录像
      - 弥瑟里seri
      - 弥瑟里
      - seri
  "*": # all supported fields
    title: "【{streamer}】%Y-%m-%dT%H:%M:%S录播_{title}"
    tid: 27
    copyright: 1
    source: ''
    cover_path: /etc/biliup/cover.png
    desc_format_id: 0
    description: |
      streamer: {streamer}
      title: {title}
      date: %Y-%m-%dT%H:%M:%S
    dynamic: ''
    tags:
      - 虚拟UP主
      - 直播
      - 录播
      - 直播录像
    dtime: 28800
```

## Monitoring

- We use [`flower`](https://github.com/mher/flower) to monitor task queues. Open `localhost:5555` to see the panel.
- For supervisor, open `localhost:9001`.

## Dependencies

- [BililiveRecorder](https://github.com/BililiveRecorder/BililiveRecorder)
- [webhook](https://github.com/adnanh/webhook)
- [BaiduPCS-go](https://github.com/qjfoidnh/BaiduPCS-Go)
- [aliyunpan](https://github.com/tickstep/aliyunpan)
- [biliup](https://github.com/biliup/biliup)
