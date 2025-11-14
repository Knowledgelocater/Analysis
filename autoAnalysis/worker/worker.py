# worker/worker.py
from app.tasks import celery_app

if __name__ == "__main__":
    # Start worker from script (not common). Prefer CLI:
    # celery -A app.tasks.celery_app worker --loglevel=info
    celery_app.worker_main(["worker", "--loglevel=info"])
