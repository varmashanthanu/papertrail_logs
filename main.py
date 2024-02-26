import requests
import os
import json
from datetime import datetime, timedelta
import shutil
import gzip
import time
import pandas as pd

API_KEY_LABEL = 'PAPERTRAIL_API_KEY'
API_KEY = os.getenv(API_KEY_LABEL)
BASE_URL = 'https://papertrailapp.com/api/v1'

missing_invoice_ids = [1662433, 1662434, 1662435, 1662437]


def get_epoch_time(date: str) -> str:
    """
    Returns epoch time of the requested datetime string

    Args:
        date: string date time of format YYY-MM-DD

    Returns:

    """

    return str((datetime.strptime(date, '%Y-%m-%d') - datetime(1970, 1, 1)).total_seconds())


def search_logs(query: str, min_time: str = None, max_time: str = None) -> dict:
    """
    Get logs from live logs (not archives)
    Args:
        query:
        min_time:
        max_time:

    Returns:

    """
    headers = {
        "X-Papertrail-Token": API_KEY,
    }

    search_endpoint = f'events/search.json'
    url = f"{BASE_URL}/{search_endpoint}"
    data = {
        "q": query,
    }

    if min_time:
        data['min_time'] = get_epoch_time(min_time)
    if max_time:
        data['max_time'] = get_epoch_time(max_time)

    # Query papertrail api
    response = requests.get(url=url, headers=headers, data=data)

    return json.loads(response.text)


def search_log_archives(from_date: str, query: list, file_name: str = None) -> pd.DataFrame:
    """
    Search Archives starting from `from_date` up till 14 days from current date
    Args:
        from_date: starting date
        query: term to search for
        file_name: filename to store locally (not implemented)

    Returns:

    """
    headers = {
        "X-Papertrail-Token": API_KEY,
    }

    hour_range = [str(x).zfill(2) for x in range(0, 24)]

    today_date = datetime.now()
    current_date = datetime.strptime(from_date, '%Y-%m-%d')

    archives_endpoint = 'archives'
    valid_logs_list = []
    print('Initiating archive downloads...')
    while (today_date - current_date).days >= 14:
        current_date_str = current_date.strftime('%Y-%m-%d')
        current_date += timedelta(days=1)
        for hour in hour_range:
            gzip_file = f'log-{current_date_str}-{hour}.gz'
            text_file = f'log-{current_date_str}-{hour}.txt'
            url = f"{BASE_URL}/{archives_endpoint}/{current_date_str}-{hour}/download"
            response = requests.get(url=url, headers=headers, stream=True)
            print(f'Downloading archive for {current_date_str} hour {hour}...')
            start_time = time.time()
            with open(gzip_file, 'wb') as f:
                for chunk in response.raw.stream(1024, decode_content=False):
                    if chunk:
                        f.write(chunk)

            end_time = time.time()
            print(f'{round(end_time-start_time,2)}s: Downloaded. Extracting...')
            start_time = time.time()
            with gzip.open(gzip_file, 'rb') as f_in:
                with open(text_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            os.remove(gzip_file)
            end_time = time.time()
            print(f'{round(end_time-start_time,2)}s: Extracted. Reading...')
            start_time = time.time()

            with open(text_file, 'r') as large_file:
                for line in large_file:
                    timestamp = line.split('\t')[1]
                    message = line.split('\t')[9]
                    if any(q in message.lower() for q in query):
                        log = {
                            'timestamp': timestamp,
                            'message': message,
                        }
                        valid_logs_list.append(log)

            large_file.close()

            os.remove(text_file)
            end_time = time.time()
            print(f'{end_time - start_time}s: Done.')
    return pd.DataFrame(valid_logs_list)


result = search_log_archives(from_date='2024-01-19', query=['processing 1662433', '1662433'])

print('end')

