import time
from typing import Dict, List, Optional

from celery.signals import task_success
from celery_conf import celery_app
from loguru import logger


@celery_app.task(name="scrape_cases_on_schedule")
def task_scrape_cases_on_schedule(*args, **kwargs) -> List:
    logger.info(
        f"Start scraping process..."
    )
    finish_data = [{"case_id": "case_id_1", "case_name": "case_name_1"},
                   {"case_id": "case_id_2", "case_name": "case_name_2"}]
    return finish_data


@celery_app.task(name="process_new_case")
def task_process_new_case(*args, **kwargs) -> Dict:
    case = kwargs['case']
    logger.info(f"Processing case {case['case_id']}")
    processed_case = {"case": case, "metadata": "metadata", "summary": "summary"}
    task_quality_check.delay(processed_case=processed_case)
    return processed_case


@celery_app.task(name="quality_check")
def task_quality_check(*args, **kwargs) -> Optional[bool]:
    processed_case = kwargs['processed_case']
    logger.info(f"Checking quality for case {processed_case['case']['case_id']} with result: {processed_case}")

    if "error" in processed_case['metadata'] or "error" in processed_case['summary']:
        logger.info(f"Error in case {processed_case['case']['case_id']}")
        time.sleep(2)
        task_process_new_case.delay(case=processed_case['case'])
    else:
        return processed_case


@celery_app.task(name="save_to_db")
def task_save_to_db(**kwargs):
    processed_case = kwargs['processed_case']
    logger.info(f"Saving {processed_case['case']['case_id']} to database")


@task_success.connect(sender=task_quality_check)
def task_success_handler(sender, result, **kwargs) -> None:
    logger.info("Signal calls, that mean quality_check is SUCCESS")
    task_save_to_db.delay(processed_case=result)

# @task_failure.connect(sender=task_quality_check)
# def task_success_handler(sender, result, **kwargs) -> None:
#     logger.info("Signal calls, that mean quality_check is FAILURE")
#     task_process_new_case.delay(kwargs={"case_processed": result})
