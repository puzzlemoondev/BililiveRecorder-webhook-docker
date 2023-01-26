# BililiveRecorder-webhook-docker

Dockerized [BililiveRecorder](https://github.com/BililiveRecorder/BililiveRecorder) with baidupcs and aliyunpan upload webhook.

The [webhook](https://github.com/adnanh/webhook) server listens for `FileClosed` events, uploads folder containing the file to baidupcs, and removes the folder after upload success.

[B站专栏](https://www.bilibili.com/read/cv21367565)

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

## Dependencies

- [BililiveRecorder](https://github.com/BililiveRecorder/BililiveRecorder)
- [webhook](https://github.com/adnanh/webhook)
- [BaiduPCS-go](https://github.com/qjfoidnh/BaiduPCS-Go)
- [aliyunpan](https://github.com/tickstep/aliyunpan)
