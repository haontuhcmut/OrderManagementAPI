celery -A app.celery_tasks.c_app worker -l info &
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload