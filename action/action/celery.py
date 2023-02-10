from celery import Celery

from action import celeryconfig

app = Celery("action")
app.config_from_object(celeryconfig)

if __name__ == "__main__":
    app.start()
