#! /usr/bin/env python
# coding: utf-8
from multiprocessing import Process
import multiprocessing
import time
import subprocess
import argparse
import sys
import os
import datetime
import shutil
from threading import Event
import signal
# get args

parser = argparse.ArgumentParser(description='Script to run very simple stress tests')
parser.add_argument('--min-cpu', dest='minCpus', type=int, default=50,help='min of CPU using.(default: 50) Use 50% to stress all the CPUs')
parser.add_argument('--max-cpu', dest='maxCpus', type=int, default=55,help='Max of CPU using.(default: 55) Use 55% to stress all the CPUs')
parser.add_argument('--time', dest='time', type=int, default=20, help='Time for the test in seconds (default: 20)')
parser.add_argument('--ram', dest='rams', type=int, default=0, help='Allocate RAM percent (default is 0).')
args = parser.parse_args()
global currProcList
sleep = Event() #event is used to have an interruptable sleep

#Signal wrapper to stop tests
def exit_child(x,y):
  global currProcList
  if currProcList.__len__() != 0:
     for p in currProcList:
         p.terminate()
  sleep.set()
signal.signal(signal.SIGINT, exit_child)

def getCpuUse(x,result_queue):
    p = subprocess.Popen("vmstat 1 3 | awk 'END {print (100-$(NF-2))}'", shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = int(p.stdout.readlines().__getitem__(0))
    result_queue.put(result)

def getMemUse(x,result_queue):
    p = subprocess.Popen("awk '/MemTotal/{total=$2}/MemFree/{free=$2}END{print (total-free)/total*100}' /proc/meminfo", shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = int(float(p.stdout.readlines().__getitem__(0)))
    result_queue.put(result)
    
def task_cpu(x):
    while True:
        x*x

if __name__ == '__main__':
    multiprocessing.set_start_method('forkserver') #python3特性，支持子进程和父进程分离，不会复制父进程的内存资源
    result_queue = multiprocessing.Queue()
    #multiprocessing.set_start_method('spawn')
    start_time = time.time()
    minCpus = args.minCpus
    maxCpus = args.maxCpus
    rams = args.rams
    currProcList = []
    ramblock = []
    file = open('/home/ddoms/cpudemo.log.' + str(os.getpid()), mode='w')
    while True:
        if time.time() - start_time >= args.time:
          if currProcList.__len__() != 0:
            for p in currProcList:
              p.terminate()
          break
        p = multiprocessing.Process(target=getMemUse, args=(1,result_queue))
        p.start()
        p.join()
        result = result_queue.get()
        curMem = result
        p1 = multiprocessing.Process(target=getCpuUse, args=(1,result_queue))
        p1.start()
        p1.join()
        result1 = result_queue.get()
        curCpus =result1
        n_time = datetime.datetime.now()
        file.write('%s CPU is: %s%% ,MEM is: %s%%, task: %s, mem_test: %sGB \n' % (n_time,curCpus,curMem,currProcList.__len__(),len(ramblock) ))
        file.flush()
        if rams != 0 and curMem <= rams :
              print("Allocating 1GB of RAM" )
              ramblock.append('x' * 1048576*1024)
        elif rams != 0 and curMem > rams and (curMem - rams) >= 4 :
              ramblock = ramblock[:-1]
        elif rams ==0 and curCpus <= minCpus:
            p = Process(target=task_cpu, args=(1,))
            currProcList.append(p)
            p.start()
        elif rams ==0 and curCpus >= maxCpus:
            if currProcList.__len__() != 0:
                p = currProcList.__getitem__(0)
                p.terminate()
                currProcList.remove(p)
        else:
            if(sleep.wait(10)):
               break
    exit_child(0,0)
    sys.exit(0)
