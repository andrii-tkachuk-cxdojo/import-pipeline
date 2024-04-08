from typing import Final

from environs import Env

env = Env()
env.read_env()

CELERY_BROKER_URL: Final = env.str("CELERY_BROKER_URL")
# CELERY_BACKEND_URL: Final = env.str("CELERY_BACKEND_URL")

AWS_S3_BUCKET_CASE: Final = env.str("AWS_S3_BUCKET_CASE")
AWS_S3_BUCKET_RAW_DATA: Final = env.str("AWS_S3_BUCKET_RAW_DATA")
AWS_S3_FOLDER_NAME_SUCCESS: Final = env.str("AWS_S3_FOLDER_NAME_SUCCESS")
AWS_S3_FOLDER_NAME_ERROR: Final = env.str("AWS_S3_FOLDER_NAME_ERROR")
