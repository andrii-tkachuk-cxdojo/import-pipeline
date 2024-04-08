from celery import Celery
from celery.schedules import crontab
from constants import CELERY_BROKER_URL


class BaseCeleryConfig:
    broker_url = CELERY_BROKER_URL
    # result_backend = CELERY_BACKEND_URL

    # result_extended = True
    # result_expires = 3600

    task_track_started = True
    task_acks_late = True
    task_default_expires = 3600
    task_reject_on_worker_lost = True

    task_time_limit = 3600
    task_soft_time_limit = 3600

    worker_send_task_events = True
    worker_start_timeout = 120
    worker_lost_wait = 60

    broker_heartbeat = 30
    broker_connection_timeout = 120
    broker_connection_max_retries = 2
    broker_connection_retry_on_startup = True


class AppCeleryConfig(BaseCeleryConfig):
    worker_prefetch_multiplier = 3
    worker_concurrency = 3


def create_celery_app(name, config_class, task_routes) -> Celery:
    app = Celery(name, include=["tasks"])
    app.config_from_object(config_class)
    app.conf.task_routes = task_routes
    app.conf.beat_schedule = {
        'import_pipeline.tasks.run_task_chain': {
            'task': 'import_pipeline.tasks.run_task_chain',
            'schedule': crontab(hour=3, minute=0),
        },
    }
    return app


celery_app = create_celery_app(
    "celery_ai",
    AppCeleryConfig,
    {
        "import_pipeline.tasks.run_task_chain": {"queue": "case"},
        "scrape_cases_on_schedule": {"queue": "case"},
        "process_new_cases": {"queue": "case"},
        "quality_check": {"queue": "case"},
        "reprocess_one_case": {"queue": "case"},
        "save_to_db": {"queue": "case"},
    },
)
