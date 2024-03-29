# BililiveRecorder-webhook-docker

[![Test](https://github.com/puzzlemoondev/BililiveRecorder-webhook-docker/actions/workflows/test.yml/badge.svg)](https://github.com/puzzlemoondev/BililiveRecorder-webhook-docker/actions/workflows/test.yml)
[![Publish](https://github.com/puzzlemoondev/BililiveRecorder-webhook-docker/actions/workflows/publish.yml/badge.svg)](https://github.com/puzzlemoondev/BililiveRecorder-webhook-docker/actions/workflows/publish.yml)
[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/puzzlemoondev/bililive-recorder-webhook?sort=semver)](https://hub.docker.com/r/puzzlemoondev/bililive-recorder-webhook)
[![Docker Image Size (latest semver)](https://img.shields.io/docker/image-size/puzzlemoondev/bililive-recorder-webhook?sort=semver)](https://hub.docker.com/r/puzzlemoondev/bililive-recorder-webhook)

Dockerized [BililiveRecorder](https://github.com/BililiveRecorder/BililiveRecorder) with `biliup`, `DanmakuFactory`,
`baidupcs` and `aliyunpan` upload webhook with [caddy](https://github.com/caddyserver/caddy) reverse proxy support for automated HTTPS.

The [webhook](https://github.com/adnanh/webhook) server listens for `FileClosed` events, uploads files, and removes them
after upload success.

[B 站专栏](https://www.bilibili.com/read/cv21367565)

## Why

- Parallelism (`celery` task queue)
- Lightweight enough to run on t2.micro
- Real time service & task monitoring and management (using `supervisor` & `flower`)
- Automated HTTPS (using `caddy`)

## Why not

- No GUI for configuration
- No GPU acceleration for `ffmpeg` tasks
- Multiple services in a docker container (to keep memory footprint low)
- Python

## How to use

> ⚠️ DO NOT TURN BURN_DANMAKU ON if your machine is low on resource.

- Add a [`.env` file](https://docs.docker.com/compose/environment-variables/#the-env-file) with these variables. Note that every variable is optional. For
  baidupcs, provide both bduss and stoken. For aliyunpan, provide rtoken. Providing credentials for both platform at the
  same time triggers upload to both platform concurrently.
  - RECORDER_USER: username for BiliveRecorder
  - RECORDER_PASS: password for BiliveRecorder
  - RECORDER_ADDRESS: needed if you want to use reverse proxy. defaults to `localhost`. If you have an A record in your DNS records you should use that instead.
  - BAIDUPCS_UPLOAD_DIR: baidupcs folder to upload files into
  - BAIDUPCS_BDUSS: bduss for baidupcs login.
    See [baidupcs](https://github.com/qjfoidnh/BaiduPCS-Go#%E7%99%BB%E5%BD%95%E7%99%BE%E5%BA%A6%E5%B8%90%E5%8F%B7) for
    how to retrieve.
  - BAIDUPCS_STOKEN: stoken for baidupcs login.
    See [baidupcs](https://github.com/qjfoidnh/BaiduPCS-Go#%E7%99%BB%E5%BD%95%E7%99%BE%E5%BA%A6%E5%B8%90%E5%8F%B7) for
    how to retrieve.
  - BAIDUPCS_MAX_UPLOAD_PARALLEL: parallel upload setting for SVIP user. Max 100.
  - ALIYUNPAN_UPLOAD_DIR: aliyunpan folder to upload files into
  - ALIYUNPAN_RTOKEN: refresh token for aliyunpan login.
    See [aliyunpan](https://github.com/tickstep/aliyunpan#%E5%A6%82%E4%BD%95%E8%8E%B7%E5%8F%96RefreshToken) for how to
    retrieve.
  - BURN_DANMAKU: pass 1 to turn danmaku burning on. This creates a separate video file with hardcoded danmaku.
  - BILIBILI_UPLOAD_BURNED: pass 1 to upload video with danmaku instead of the original.
  - REMOVE_LOCAL: pass 1 to remove local files after upload.

```bash
# without reverse proxy
make up
# with reverse proxy
make proxy-up
```

- Add webhook to settings
  - Go to Settings -> Webhook -> Webhook V2
  - Add this line: `http://localhost:9000/hooks/recorder-file-closed`

## How to Update

```bash
# without reverse proxy
make update
# with reverse proxy
make proxy-update
```

## Biliup Integration

- To use biliup, add your `cookies.json` under `biliup`. This directory will be mounted to `/etc/biliup` in the
  container. Alternatively, run `docker compose run --rm -w /etc/biliup webhook biliup login` to login interactively.
- (Optional) Add your config yaml and cover files (optional) under `biliup`. See sample for all supported
  fields. `title` and `desc` supports string interpolation. Run `biliup upload --help` to see default values.
- If you have multiple bilibili accounts, put all their cookies json inside `/etc/biliup` and specify their name in your
  config yaml.

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

## DanmakuFactory Integration

- To use DanmakuFactory, add your `DanmakuFactoryConfig.json` under `DanmakuFactory`. If not, default values will be
  used. This directory will be mounted to `/etc/DanmakuFactory` in the container.

### Sample `DanmakuFactoryConfig.json`

This is the default config file from https://github.com/hihkm/DanmakuFactory

```
{
    "resolution": [1920, 1080],
    "scrolltime": 12.000000,
    "fixtime": 5.000000,
    "density": 0,
    "fontname": "Microsoft YaHei",
    "fontsize": 38,
    "opacity": 180,
    "outline": 0,
    "shadow": 1,
    "displayArea": 1.000000,
    "scrollArea": 1.000000,
    "bold": true,
    "showUsernames": true,
    "showMsgbox": true,
    "msgboxSize": [500, 1080],
    "msgboxPos": [20, 0],
    "msgboxFontsize": 38,
    "giftMinPrice": 0.00,
    "blockmode": [],
    "statmode": []
}
```

## Monitoring

- We use [`flower`](https://github.com/mher/flower) to monitor task queues. Visit `http://[RECORDER_ADDRESS]:5555/flower` (or `https://[RECORDER_ADDRESS]/flower` for reverse proxy) to see the panel.
- For supervisor, visit `http://[RECORDER_ADDRESS]:9001` (or `https://[RECORDER_ADDRESS]/supervisor` for reverse proxy). Note that supervisor does not fully support reverse proxy so expect some weird behavior under reverse proxy.

## Dependencies

- [BililiveRecorder](https://github.com/BililiveRecorder/BililiveRecorder)
- [webhook](https://github.com/adnanh/webhook)
- [BaiduPCS-go](https://github.com/qjfoidnh/BaiduPCS-Go)
- [aliyunpan](https://github.com/tickstep/aliyunpan)
- [biliup-rs](https://github.com/ForgQi/biliup-rs)
- [DanmakuFactory](https://github.com/hihkm/DanmakuFactory)
- [caddy](https://github.com/caddyserver/caddy)
- ffmpeg
