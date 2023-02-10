broker_url = "redis://redis"

result_backend = broker_url

imports = ["action.tasks"]

worker_concurrency = 4
