from .celery import app
from .task import (
    BurnDanmakuTask,
    BurnDanmakuTaskInput,
    UploadAliyunpanTaskInput,
    UploadAliyunpanTask,
    UploadBaidupcsTask,
    UploadBaidupcsTaskInput,
    UploadBilibiliTask,
    UploadBilibiliTaskInput,
    RemoveTask,
    RemoveTaskInput,
)

RETRY_TASK_ARGS = dict(autoretry_for=(Exception,), default_retry_delay=10)


@app.task(**RETRY_TASK_ARGS)
def burn_danmaku(input_dict: dict) -> dict:
    input = BurnDanmakuTaskInput.from_dict(input_dict)
    task = BurnDanmakuTask(input)
    output = task.run()
    return output.to_dict()


@app.task(**RETRY_TASK_ARGS)
def upload_aliyunpan(input_dict: dict) -> dict:
    input = UploadAliyunpanTaskInput.from_dict(input_dict)
    task = UploadAliyunpanTask(input)
    output = task.run()
    return output.to_dict()


@app.task(**RETRY_TASK_ARGS)
def upload_baidupcs(input_dict: dict) -> dict:
    input = UploadBaidupcsTaskInput.from_dict(input_dict)
    task = UploadBaidupcsTask(input)
    output = task.run()
    return output.to_dict()


@app.task(**RETRY_TASK_ARGS)
def upload_bilibili(input_dict: dict) -> dict:
    input = UploadBilibiliTaskInput.from_dict(input_dict)
    task = UploadBilibiliTask(input)
    output = task.run()
    return output.to_dict()


@app.task(**RETRY_TASK_ARGS)
def remove(input_dict: dict) -> dict:
    input = RemoveTaskInput.from_dict(input_dict)
    task = RemoveTask(input)
    output = task.run()
    return output.to_dict()
