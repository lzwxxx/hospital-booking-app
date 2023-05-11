import time

from airflow import DAG
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator
from airflow.utils.dates import days_ago
import requests

from datetime import datetime

args = {
    'owner': 'airflow',
}

def avg_appointment_by_hour(appt_data):

    res = []
    for hour in range(0,24):
        row = {}

        dates = set()
        total = 0
        for each_dict in appt_data:
            if hour == int(each_dict['time']):
                # print(hour,each_dict['date'],len(dates),total)
                dates.add(each_dict['date'])
                total += 1
        n = total 
        d = len(dates)

        row['hour'] = hour
        row['average_num_patients'] = n//d if d != 0 else 0 

        # print(hour,n,d,"row",row)

        res.append(row)
    
    return res
    
with DAG(
    dag_id='analytics_dag',
    default_args=args,
    schedule_interval='@weekly',
    start_date=days_ago(2),
    is_paused_upon_creation=False
) as dag:

    def backup_avg_appt_hourly():
        try:
            res = requests.get("http://analytics:5001/weekly_average_patient/all")
            res_json = res.json()

            data = res_json['data']['average_patients']

            updated_at = datetime.today().strftime('%Y-%m-%d')

            for row in data:
                row['snapshot_timestamp'] = updated_at

            payload = {
                'snapshot' : data
            }
            
            post_res = requests.post("http://analytics:5001/snapshot_weekly_average_patient", json=payload)
                

        except Exception as e:
            print(e)

        # pass
    
    def avg_appt_hourly():
        try:
            res = requests.get("http://appointment:5001/appointment")
            res_json = res.json()
            appt_data = res_json['data']['appointments']
            print(appt_data)
            
            avg_patients_per_hour_list = avg_appointment_by_hour(appt_data)
            print(avg_patients_per_hour_list)
            
            payload = {
                'average_patients': avg_patients_per_hour_list
            }
            
            # print(payload)

            res = requests.post("http://analytics:5001/weekly_average_patient", json=payload)
                
            if res.json()['code'] == 200: 
                print('Updated done!')
                                    
        except Exception as e:
            print(e)

    t1 = PythonOperator(
        task_id='backup_avg_appt_hourly',
        python_callable=backup_avg_appt_hourly
    )
    
    t2 = PythonOperator(
        task_id='update_avg_patient',
        python_callable=avg_appt_hourly
    )
    
    t1 >> t2
