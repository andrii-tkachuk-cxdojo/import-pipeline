from typing import Dict, Any

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime


def scrape_cases_on_schedule(**kwargs):
    # Условно логика скрапинга новых кейсов
    # Возвращаем список диктов новых кейсов
    return [{"case_id": "case_id_1", "case_name": "case_name_1"}, {"case_id": "case_id_2", "case_name": "case_name_2"},
            ...]


def process_new_case(case_data: Dict[str, Any], **kwargs):
    # Условно логика обработки нового кейса
    print(f"Processing case {case_data['case_id']}")
    # Условно возвращаем результат обработки кейса
    return {"metadata": "metadata", "summary": "summary"}


def save_to_db(case_id, **kwargs):
    # Логика сохранения данных кейса в базу данных
    task_instance = kwargs['ti']
    process_result = task_instance.xcom_pull(task_ids=f'case_processing_group.task_process_new_case_{case_id}')
    print(f"Saving {process_result} to database")


def quality_check(case_id, **kwargs):
    # Извлечение результата предыдущей задачи из XCom
    task_instance = kwargs['ti']
    process_result = task_instance.xcom_pull(task_ids=f'case_processing_group.task_process_new_case_{case_id}')
    # Условно логика проверки качества кейса
    print(f"Checking quality for case {case_id} with result: {process_result}")
    # Если качество неудовлетворительное, возвращаем ID задачи для повторной обработки
    if "error" in process_result['metadata'] or "error" in process_result['summary']:
        return f'task_process_new_case_{case_id}'
    # Если качество удовлетворительное, возвращаем ID задачи для сохранения в БД
    return f'save_to_db_task_{case_id}'


with DAG('my_dag', start_date=datetime(2021, 1, 1), schedule_interval='@daily') as dag:
    task_scrape_cases_on_schedule = PythonOperator(
        task_id='task_scrape_cases_on_schedule',
        python_callable=scrape_cases_on_schedule,
        provide_context=True
    )

    with TaskGroup(group_id='case_processing_group') as processing_group:
        cases = scrape_cases_on_schedule.execute({})  # Получаем список диктов кейсов
        for case_id in cases:
            task_process_new_case = PythonOperator(
                task_id=f'task_process_new_case_{case_id}',
                python_callable=process_new_case,
                op_kwargs={'case_id': case_id},
                provide_context=True
            )

            task_quality_check = PythonOperator(
                task_id=f'task_quality_check_{case_id}',
                python_callable=quality_check,
                op_kwargs={'case_id': case_id},
                provide_context=True
            )

            save_to_db_task = PythonOperator(
                task_id=f'save_to_db_task_{case_id}',
                python_callable=save_to_db,
                op_kwargs={'case_id': case_id},
                provide_context=True
            )

            task_process_new_case >> task_quality_check >> [task_process_new_case, save_to_db_task]

    task_scrape_cases_on_schedule >> processing_group
