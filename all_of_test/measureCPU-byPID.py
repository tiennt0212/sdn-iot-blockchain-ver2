import os
import sys
import psutil
import time

def measureCPU(destFile, pid):
    python_process = psutil.Process(pid)
    while(True):
        cpuUse = python_process.cpu_percent(interval=0.1);
        destFile.write("{}\n".format(cpuUse));

if __name__ == "__main__":
    pid = int(sys.argv[1]);
    f = open('./realtimeCPU','w+');
    measureCPU(f, pid);
    f.close();