from celery.result import AsyncResult
from celery import chain, group
from tasks import *
from loguru import logger
import time

if __name__ == "__main__":
    # task_group = group(task_scrape_cases_on_schedule.s(item) for item in task_process_new_case())
    # task_group.apply_async()

    task_chain = chain(task_scrape_cases_on_schedule.s() | task_process_new_cases.s())
    task_chain.apply_async()

    # task = task_scrape_cases_on_schedule.delay()
    #
    # async_result = AsyncResult(task.id)
    # while not async_result.ready():
    #     time.sleep(0.5)
    #
    # if async_result.successful():
    #     for case in async_result.get():
    #         task_process_new_case.delay(case=case)
    # else:
    #     logger.error(
    #         f"Error in task {task.id}: {async_result.info}"
    #     )
