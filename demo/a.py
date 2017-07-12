# sinner_thread.py

import threading
import itertools
import time
import sys


class Signal: # 这个类定义一个可变对象，用于从外部控制线程
    go = True

def spin(msg, signal):  # 这个函数会在单独的线程中运行，signal 参数是前边定义的Signal类的实例
    write, flush = sys.stdout.write, sys.stdout.flush
    for char in itertools.cycle('|/-\\'):  # itertools.cycle 函数从指定的序列中反复不断地生成元素
        status = char + ' ' + msg
        write(status)
        flush()
        write('\x08' * len(status))  # 使用退格符把光标移回行首
        time.sleep(.1)  # 每 0.1 秒刷新一次
        if not signal.go:  # 如果 go属性不是 True，退出循环
            break

    write(' ' * len(status) + '\x08' * len(status))  # 使用空格清除状态消息，把光标移回开头


def slow_function():  # 模拟耗时操作
    # 假装等待I/O一段时间
    time.sleep(3)  # 调用sleep 会阻塞主线程，这么做事为了释放GIL，创建从属线程
    return 42


def supervisor():  # 这个函数设置从属线程，显示线程对象，运行耗时计算，最后杀死进程
    signal = Signal()
    spinner = threading.Thread(target=spin,
                               args=('thinking!', signal))
    print('spinner object:', spinner)  # 显示线程对象 输出 spinner object: <Thread(Thread-1, initial)>
    spinner.start()  # 启动从属进程
    result = slow_function()  # 运行slow_function 行数，阻塞主线程。同时丛书线程以动画形式旋转指针
    signal.go = False
    spinner.join()  # 等待spinner 线程结束
    return result

def main():
    result = supervisor()  
    print('Answer', result)


if __name__ == '__main__':
    main()