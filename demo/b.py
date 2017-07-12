import asyncio
import collections
from collections import namedtuple
from enum import Enum

import aiohttp
from aiohttp import web

from flags import save_flag, show, main, BASE_URL

DEFAULT_CONCUR_REQ = 5
MAX_CONCUR_REQ = 1000

Result = namedtuple('Result', 'status data')
HTTPStatus = Enum('Status', 'ok not_found error')

# 自定义异常用于包装其他HTTP货网络异常，并获取country_code，以便报告错误
class FetchError(Exception):
    def __init__(self, country_code):
        self.country_code = country_code


@asyncio.coroutine
def http_get(url):
    resp = yield from aiohttp.request('GET', url)
    if resp.status == 200:
        ctype = resp.headers.get('Content-type', '').lower()
        if 'json' in ctype or url.endswith('json'):
            data = yield from resp.json()
        else:
            data = yield from resp.read()
        return data
    elif resp.status == 404:
        raise web.HttpNotFound()
    else:
        raise aiohttp.HttpProcessionError(
            code=resp.status, message=resp.reason,
            headers=resp.headers)


@asyncio.coroutine
def get_country(cc):
    url = "{}/{cc}/metadata.json".format(BASE_URL, cc=cc.lower())
    metadata = yield from http_get(url)
    return metadata['country']


@asyncio.coroutine
def get_flag(cc):
    url = "{}/{cc}/{cc}.gif".format(BASE_URL, cc=cc.lower())
    return (yield from http_get(url))


@asyncio.coroutine
def download_one(cc, semaphore):
    try:
        with (yield from semaphore):
            image = yield from get_flag(cc)
        with (yield from semaphore):
            country = yield from get_country(cc)
    except web.HTTPNotFound:
        status = HTTPStatus.not_found
        msg = 'not found'
    except Exception as exc:
        raise FetchError(cc) from exc
    else:
        country = country.replace(' ', '_')
        filename = '{}--{}.gif'.format(country, cc)
        print(filename)
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, save_flag, image, filename)
        status = HTTPStatus.ok
        msg = 'ok'
    return Result(status, cc)

@asyncio.coroutine
def downloader_coro(cc_list):
    counter = collections.Counter()
    # 创建一个 asyncio.Semaphore 实例，最多允许激活MAX_CONCUR_REQ个使用这个计数器的协程
    semaphore = asyncio.Semaphore(MAX_CONCUR_REQ)
    # 多次调用 download_one 协程，创建一个协程对象列表
    to_do = [download_one(cc, semaphore) for cc in sorted(cc_list)]
    # 获取一个迭代器，这个迭代器会在future运行结束后返回future
    to_do_iter = asyncio.as_completed(to_do)
    for future in to_do_iter:
        # 迭代允许结束的 future    
        try:
            res = yield from future # 获取asyncio.Future 对象的结果（也可以调用future.result）
        except FetchError as exc:
            # 抛出的异常都包装在FetchError  对象里
            country_code = exc.country_code
            try:
                # 尝试从原来的异常 （__cause__）中获取错误消息
                error_msg = exc.__cause__.args[0]
            except IndexError:
                # 如果在原来的异常中找不到错误消息，使用所连接异常的类名作为错误消息
                error_msg = exc.__cause__.__class__.__name__
            if error_msg:
                msg = '*** Error for {}: {}'
                print(msg.format(country_code, error_msg))
            status = HTTPStatus.error
        else:
            status = res.status
        counter[status] += 1
    return counter

def download_many(cc_list):
    loop = asyncio.get_event_loop()
    coro = downloader_coro(cc_list)
    counts = loop.run_until_complete(coro)
    loop.close()
    return counts


if __name__ == '__main__':
    main(download_many)