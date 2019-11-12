#!/usr/bin/python
# -*-coding:utf-8-*-

import os
import sys
import codecs
import multiprocessing.dummy
from multiprocessing import Pool as ProcessPool
from multiprocessing.dummy import Pool as ThreadPool
from time import sleep, time
import chardet
from random import randrange
import itertools
import logging

def handler(sec, seq):
    threadName = multiprocessing.dummy.current_process().name
    s = '%s.%s, now I will sleep %s seconds' % (seq, threadName, sec)
    sleep(sec)
    print s

    return threadName


def handler_args(args):
    """Convert `f([1,2])` to `f(1,2)` call."""
    # return handler(*args)
    (path, seq) = args
    return convert(path, seq)


def get_pool(b_dummy=True, num=4):
    """
    if b_dummy is True then get ThreadPool, or get process pool
    :param b_dummy: dummy thread Pool or Process pool
    :param num: thread or process num
    :return: pool object
    """
    if b_dummy:
        pool = ThreadPool(num)
    else:
        pool = ProcessPool(num)

    return pool

def convert(filename, seq, out_enc="UTF-8"):
    start_time = time()
    # processName = multiprocessing.current_process().name
    # threadName = multiprocessing.dummy.current_process().name
    # threadName = threading.currentThread().getName()
    str = ""
    source_encoding = ""
    try:

        fpath, fname = os.path.split(filename)
        # codecs.open()这个方法打开的文件读取返回的将是unicode。
        content = codecs.open(filename, 'r').read()
        # chardet.detect 获取编码格式
        source_encoding = chardet.detect(content)['encoding']
        if None != source_encoding:  # 空的文件,返回None
            s = ""
            if source_encoding != 'utf-8':
                if source_encoding == 'GB2312':
                    content = content.decode('GB18030').encode(out_enc)
                else:
                    content = content.decode(source_encoding).encode(out_enc)
                codecs.open(filename, 'w').write(content)
                s = "<---ok--->"
            else:
                s = "do nothing"

            str = s

        else:
            str = "not find"

    except IOError as err:
        str = "I/O error:{0}".format(err)
    # sleep(1)
    #logging.info("seq=%s, consume=%s seconds \n\t%s", seq, time() - start_time, str)
    logging.info("[%15s]->[UTF-8]=[%s]\t%s", source_encoding.upper(), str, filename)
    return seq


def explore(dir, source_encoding_list):
    start_time = time()
    seq = 0
    for root, dirs, files in os.walk(dir, topdown=True):
        for file in files:
            # os.path.splitext(path)  分割路径，返回路径名和文件扩展名的元组
            if os.path.splitext(file)[1] in source_encoding_list:
                path = os.path.join(root, file)
                convert(path, seq)
                seq = seq + 1
    logging.info('time consume %s seconds', time() - start_time)


def exploreThread(dir, source_encoding_list):
    start_time = time()
    global pool
    pool = get_pool(b_dummy=False, num=4)
    func_var = []
    seq = 0
    for root, dirs, files in os.walk(dir, topdown=True):
        for file in files:
            # os.path.splitext(path)  分割路径，返回路径名和文件扩展名的元组
            if os.path.splitext(file)[1] in source_encoding_list:
                path = os.path.join(root, file)
                # convert(path)
                # func_var.append(randrange(3, 10))
                func_var.append((path, seq))
                seq = seq + 1

    # results = pool.map(handler_args, itertools.izip(func_var1, func_var2))
    results = pool.map(handler_args, func_var)
    pool.close()
    pool.join()
    logging.info('time consume %s seconds', time() - start_time)


def main():
    # srcPath是待转换的GBK文件的所在目录的路径, 可根据需要自行修改.
    srcPath = sys.argv[1]
    print("rootdir=" + srcPath)
    # explore(srcPath, ['.xml', '.java', '.js', '.txt', '.css', '.jsp', '.html', '.htm', '.tpl'])
    exploreThread(srcPath, ['.c', '.cpp', '.h', '.xml', '.java', '.js', '.txt', '.css', '.jsp', '.html', '.htm', '.tpl'])

#logging.basicConfig(level=logging.INFO, format='%(levelname)s %(asctime)s %(processName)s %(threadName)s %(message)s', datefmt='%Y-%m-%d %I:%M:%S')
logging.basicConfig(level=logging.INFO, format='')

if __name__ == "__main__":
    main()
