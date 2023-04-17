# burnCpuMem

##可以根据机器的负载自动调整

##内存加压

###目标值50%，时间300s

python burnCpuMem.py   --ram 50 --time 300

##CPU加压

###目标值90%到92%， 时间300s

python burnCpuMem.py   --min-cpu 90 --max-cpu 92--time 300
