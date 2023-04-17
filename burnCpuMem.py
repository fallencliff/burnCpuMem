#! /usr/bin/env python
# coding: utf-8
from multiprocessing import Process
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



def getCpuUse():
    p = subprocess.Popen("vmstat 1 3 | awk 'END {print (100-$(NF-2))}'", shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = int(p.stdout.readlines().__getitem__(0))
    return result

def getMemUse():
    p = subprocess.Popen("awk '/MemTotal/{total=$2}/MemFree/{free=$2}END{print (total-free)/total*100}' /proc/meminfo", shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = int(float(p.stdout.readlines().__getitem__(0)))
    return int(result)
    
def task_cpu(x):
    while True:
        x*x


if __name__ == '__main__':
    start_time = time.time()
    minCpus = args.minCpus
    maxCpus = args.maxCpus
    rams = args.rams
    currProcList = []
    ramblock = []
    if rams != 0:
      file = open('/home/ddoms/memdemo.log', mode='w')
    else:
      file = open('/home/ddoms/cpudemo.log', mode='w')
    while True:
        print time.time() - start_time
        if time.time() - start_time >= args.time:
          if currProcList.__len__() != 0:
            for p in currProcList:
              p.terminate()
          break
        curCpus = getCpuUse()
        curMem = getMemUse()
        n_time = datetime.datetime.now()
        file.write('%s CPU is: %s%% ,MEM is: %s%%, task: %s, mem_test: %sGB \n' % (n_time,curCpus,curMem,currProcList.__len__(),len(ramblock) ))
        file.flush()
        if rams != 0:
          if curMem <= rams :
              print("Allocating 1GB of RAM" )
              ramblock.append('x' * 1048576*1024)
          elif curMem > rams and (curMem- rams) > 1:
              ramblock = ramblock[:-1]
        elif curCpus <= minCpus:
            p = Process(target=task_cpu, args=(1,))
            currProcList.append(p)
            p.start()
        elif curCpus >= maxCpus:
            if currProcList.__len__() != 0:
                p = currProcList.__getitem__(0)
                p.terminate()
                currProcList.remove(p)
        else:
            if(sleep.wait(10)):
               break
    exit_child(0,0)
    sys.exit(0)