# import-pipeline

### Example .env

```env
CELERY_BROKER_URL=redis://celery-redis:6379/10
CELERY_BACKEND_URL='db+postgresql+psycopg2://celery:postgres@celery-db:5234/celery_db'

FLOWER_USER=flower
FLOWER_PASSWORD=password
FLOWER_PORT=6655

POSTGRES_DB=celery_db
POSTGRES_PASSWORD=postgres
POSTGRES_USER=celery
POSTGRES_PORT=5234
```