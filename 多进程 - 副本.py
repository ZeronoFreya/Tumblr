# coding: utf-8
from concurrent.futures import ThreadPoolExecutor as Pool
from concurrent.futures import as_completed
import requests

URLS = ['http://qq.com']


def task(url, timeout=10):
    return requests.get(url, timeout=timeout)


with Pool(max_workers=1) as executor:
    future_tasks = [executor.submit(task, 'http://qq.com')]

    for f in future_tasks:
        if f.running():
            print('%s is running' % str(f))

    for f in as_completed(future_tasks):
        try:
            ret = f.done()
            if ret:
                f_ret = f.result()
                print('%s, done, result: %s, %s' % (str(f), f_ret.url, len(f_ret.content)))
        except Exception as e:
            f.cancel()
            print(str(e))