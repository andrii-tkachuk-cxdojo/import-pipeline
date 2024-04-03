from typing import Final

from environs import Env

env = Env()
env.read_env()

CELERY_BROKER_URL: Final = env.str("CELERY_BROKER_URL")
CELERY_BACKEND_URL: Final = env.str("CELERY_BACKEND_URL")
