import json
import time
from datetime import datetime

from celery.signals import task_failure

from tasks_handlers import DependencyManager
from celery import signals, chain
# from celery.signals import task_success
from celery_conf import celery_app
from constants import AWS_S3_BUCKET_RAW_DATA, AWS_S3_FOLDER_NAME_SUCCESS, AWS_S3_FOLDER_NAME_ERROR
from loguru import logger


@signals.worker_process_init.connect
def setup_model(signal, sender, **kwargs):
    manager = DependencyManager()
    _ = manager.s3_client


@celery_app.task(name='import_pipeline.tasks.run_task_chain')
def run_task_chain() -> None:
    task_chain = chain(task_scrape_cases_on_schedule.s() | task_process_new_cases.s())
    task_chain.apply_async()


@celery_app.task(name="scrape_cases_on_schedule")
def task_scrape_cases_on_schedule(*args, **kwargs) -> str:
    logger.info(
        f"Start scraping process..."
    )
    finish_data = [{"case_id": "case_id_5", "case_name": "case_name_5"},
                   {"case_id": "case_id_6", "case_name": "case_name_6"}]

    file_name = f'{AWS_S3_FOLDER_NAME_SUCCESS}/{datetime.now().strftime('%Y-%m-%d_%H-%M')}.json'
    s3_client = DependencyManager().s3_client
    s3_client.put_object(Body=json.dumps(finish_data), Bucket=AWS_S3_BUCKET_RAW_DATA, Key=file_name)
    logger.info(f'File {file_name} uploaded to S3 SUCCESS.')
    return f's3://{AWS_S3_BUCKET_RAW_DATA}/{file_name}'


@celery_app.task(name="process_new_cases")
def task_process_new_cases(json_path) -> None:
    logger.info(f"Processing cases in {json_path}")

    s3_client = DependencyManager().s3_client
    bucket_name, key = json_path.replace('s3://', '').split('/', 1)
    response = s3_client.get_object(Bucket=bucket_name, Key=key)
    data = json.load(response['Body'])

    for case in data:
        print(f'Processing case: {case}')
        processed_case = {"case": case, "metadata": "metadata", "summary": "error"}
        task_quality_check.delay(processed_case=processed_case)


@celery_app.task(name="reprocess_one_case")
def task_reprocess_one_case(case, retries=0) -> None:
    logger.info(f"Reprocessing case {case['case_id']}, attempt {retries + 1}")

    if retries < 5:
        processed_case = {"case": case, "metadata": "metadata", "summary": "summary"}
        task_quality_check.delay(processed_case=processed_case, retries=retries + 1)
    else:
        logger.warning(f"Reached max retries for case {case['case_id']}")
        file_name = f'{AWS_S3_FOLDER_NAME_ERROR}/{case['case_id']}.json'
        s3_client = DependencyManager().s3_client
        s3_client.put_object(Body=json.dumps(case), Bucket=AWS_S3_BUCKET_RAW_DATA, Key=file_name)
        logger.warning(f"Case {case['case_id']} saved to S3 in {file_name}")


@celery_app.task(name="quality_check")
def task_quality_check(processed_case, retries=0) -> None:
    logger.info(f"Checking quality for case {processed_case['case']['case_id']}, attempt {retries}")

    if "error" in processed_case['metadata'] or "error" in processed_case['summary']:
        logger.warning(f"Error in case {processed_case['case']['case_id']}")
        time.sleep(2)
        task_reprocess_one_case.delay(case=processed_case['case'], retries=retries)
    else:
        task_save_to_db.delay(processed_case=processed_case)


@celery_app.task(name="save_to_db")
def task_save_to_db(processed_case) -> None:
    logger.info(f"Saving {processed_case['case']['case_id']} to database SUCCESS")


# @task_success.connect(sender=task_quality_check)
# def task_success_handler(sender, result, **kwargs) -> None:
#     logger.info("Signal calls, that mean quality_check is SUCCESS")
#     task_save_to_db.delay(processed_case=result)
#

@task_failure.connect(sender=task_scrape_cases_on_schedule)
@task_failure.connect(sender=task_process_new_cases)
@task_failure.connect(sender=task_quality_check)
@task_failure.connect(sender=task_reprocess_one_case)
@task_failure.connect(sender=task_save_to_db)
def task_failure_handler(
        sender=None,
        task_id=None,
        exception=None,
        args=None,
        kwargs=None,
        traceback=None,
        einfo=None,
        **other_kwargs
):
    error_data = {
        "task_name": sender.name,
        "task_id": task_id,
        "exception": str(exception),
        "args": args,
        "kwargs": kwargs,
        "traceback": str(traceback)
    }
    logger.error(f"Task {sender.name} with ID {task_id} failed:\n{error_data}")
