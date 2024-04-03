# from typing import Dict, Any

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
# from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta


def scrape_cases_on_schedule(**kwargs):
    finish_data = [{"case_id": "case_id_1", "case_name": "case_name_1"},
                   {"case_id": "case_id_2", "case_name": "case_name_2"},
                   ...]
    return finish_data


def process_and_check_cases(cases, **kwargs):
    for case in cases:
        max_attempts = 3
        attempt = 0

        while attempt < max_attempts:
            processed_case = process_new_case(caca=case)
            quality_check_result = quality_check(processed_case=processed_case)

            if quality_check_result:
                print(f"Case {case['case_id']} passed quality check")
                save_to_db(case_processed=processed_case)
                break
            else:
                print(f"Case {case['case_id']} failed quality check, retrying...")
                attempt += 1

        if attempt == max_attempts:
            print(f"Case {case['case_id']} failed quality check after {max_attempts} attempts")


def process_new_case(**kwargs):
    case = kwargs['case']
    print(f"Processing case {case['case_id']}")
    case_processed = {"case_id": case['case_id'], "metadata": "metadata", "summary": "summary"}
    return case_processed


def quality_check(**kwargs):
    processed_case = kwargs['processed_case']
    print(f"Checking quality for case {processed_case['case_id']} with result: {processed_case}")

    if "error" in processed_case['metadata'] or "error" in processed_case['summary']:
        return False
    else:
        return True


def save_to_db(**kwargs):
    case_processed = kwargs['case_processed']
    print(f"Saving {case_processed['case_id']} to database")


start_date = datetime.now() + timedelta(minutes=2)

with DAG('my_dag', start_date=start_date, schedule_interval='@once', catchup=False) as dag:
    task_scrape_cases_on_schedule = PythonOperator(
        task_id='scrape_cases_on_schedule',
        python_callable=scrape_cases_on_schedule,
        provide_context=True
    )

    task_process_and_check_cases = PythonOperator(
        task_id='process_and_check_cases',
        python_callable=process_and_check_cases,
        op_kwargs={'cases': "{{ ti.xcom_pull(task_ids='scrape_cases_on_schedule') }}"},
        provide_context=True
    )

    task_scrape_cases_on_schedule >> task_process_and_check_cases
