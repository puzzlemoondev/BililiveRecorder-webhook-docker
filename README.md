# BililiveRecorder-webhook-docker

[![Publish](https://github.com/puzzlemoondev/BililiveRecorder-webhook-docker/actions/workflows/publish.yml/badge.svg)](https://github.com/puzzlemoondev/BililiveRecorder-webhook-docker/actions/workflows/publish.yml)
[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/puzzlemoondev/bililive-recorder-webhook?sort=semver)](https://hub.docker.com/r/puzzlemoondev/bililive-recorder-webhook)
[![Docker Image Size (latest semver)](https://img.shields.io/docker/image-size/puzzlemoondev/bililive-recorder-webhook?sort=semver)](https://hub.docker.com/r/puzzlemoondev/bililive-recorder-webhook)

Dockerized [BililiveRecorder](https://github.com/BililiveRecorder/BililiveRecorder) with biliup, DanmakuFactory,
baidupcs and aliyunpan upload webhook.

The [webhook](https://github.com/adnanh/webhook) server listens for `FileClosed` events, uploads files, and removes them
after upload success.

[B 站专栏](https://www.bilibili.com/read/cv21367565)

## How to use

> ⚠️ DO NOT TURN BURN_DANMAKU ON if your machine is low on resource.

- Add a [`.env` file](https://docs.docker.com/compose/environment-variables/#the-env-file) with these variables. For
  baidupcs, provide both bduss and stoken. For aliyunpan, provide rtoken. Providing credentials for both platform at the
  same time triggers upload to both platform concurrently.
    - RECORDER_USER: username for BiliveRecorder
    - RECORDER_PASS: password for BiliveRecorder
    - BAIDUPCS_BDUSS: bduss for baidupcs login.
      See [baidupcs](https://github.com/qjfoidnh/BaiduPCS-Go#%E7%99%BB%E5%BD%95%E7%99%BE%E5%BA%A6%E5%B8%90%E5%8F%B7) for
      how to retrieve.
    - BAIDUPCS_STOKEN: stoken for baidupcs login.
      See [baidupcs](https://github.com/qjfoidnh/BaiduPCS-Go#%E7%99%BB%E5%BD%95%E7%99%BE%E5%BA%A6%E5%B8%90%E5%8F%B7) for
      how to retrieve.
    - ALIYUNPAN_RTOKEN: refresh token for aliyunpan login.
      See [aliyunpan](https://github.com/tickstep/aliyunpan#%E5%A6%82%E4%BD%95%E8%8E%B7%E5%8F%96RefreshToken) for how to
      retrieve.
    - BURN_DANMAKU: pass 1 to turn danmaku burning on. This creates a separate video file with hardcoded danmaku.
    - BILIBILI_UPLOAD_BURNED: pass 1 to upload video with danmaku instead of the original.
    - REMOVE_LOCAL: pass 1 to remove local files after upload.
- Run `docker compose up`
- Add webhook to settings
    - Go to Settings -> Webhook -> Webhook V2
    - Add this line: `http://localhost:9000/hooks/recorder-file-closed`

## Biliup Integration

- To use biliup, add your `cookies.json` under `biliup`. This directory will be mounted to `/etc/biliup` in the
  container. Alternatively, run `docker compose run --rm -w /etc/biliup webhook biliup login` to login interactively.
- (Optional) Add your config yaml and cover files (optional) under `biliup`. See sample for all supported
  fields. `title` and `desc` supports string interpolation. Run `biliup upload --help` to see default values.
- If you have multiple bilibili accounts, put all their cookies json inside `/etc/biliup` and specify their name in your
  config yaml.

## DanmakuFactory Integration

- To use DanmakuFactory, add your `DanmakuFactoryConfig.json` under `DanmakuFactory`. If not, default values will be
  used. This directory will be mounted to `/etc/DanmakuFactory` in the container.
- For config file format, visit https://github.com/hihkm/DanmakuFactory

### Sample `config.yml`

```
line: kodo
limit: 3
streamers:
  "弥瑟里*": # supports unix glob syntax
    title: "【弥瑟里seri】%Y-%m-%dT%H:%M:%S录播_{title}"
    tid: 27
    copyright: 1
    tag:
      - 虚拟UP主
      - 直播
      - 录播
      - 直播录像
      - 弥瑟里seri
      - 弥瑟里
      - seri
  "*": # all supported fields
    user_cookie: cookies_for_another_account.json # defaults to cookies.json
    copyright: 1
    source: ''
    tid: 27
    cover: /etc/biliup/cover.png
    title: "【{streamer}】%Y-%m-%dT%H:%M:%S录播_{title}"
    desc: |
      streamer: {streamer}
      title: {title}
      date: %Y-%m-%dT%H:%M:%S
    dynamic: ''
    tag:
      - 虚拟UP主
      - 直播
      - 录播
      - 直播录像
    dtime: 28800
    dolby: 0
    hires: 0
    no_reprint: 1
    open_elec: 0
```

## Monitoring

- We use [`flower`](https://github.com/mher/flower) to monitor task queues. Open `localhost:5555` to see the panel.
- For supervisor, open `localhost:9001`.

## Dependencies

- [BililiveRecorder](https://github.com/BililiveRecorder/BililiveRecorder)
- [webhook](https://github.com/adnanh/webhook)
- [BaiduPCS-go](https://github.com/qjfoidnh/BaiduPCS-Go)
- [aliyunpan](https://github.com/tickstep/aliyunpan)
- [biliup-rs](https://github.com/ForgQi/biliup-rs)
- [DanmakuFactory](https://github.com/hihkm/DanmakuFactory)
- ffmpeg
