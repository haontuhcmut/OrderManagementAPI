from celery import Celery

c_app = Celery("worker", broker=broker_url, backend=result_backend)