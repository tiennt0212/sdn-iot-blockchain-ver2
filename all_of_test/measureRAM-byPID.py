import os
import sys
import psutil
import time

SLEEP = 0.1

def measureRAM(destFile, pid):
    python_process = psutil.Process(pid)
    while(True):
        memoryUse = python_process.memory_info()[0]
        destFile.write("{}\n".format(memoryUse));
        time.sleep(SLEEP)

if __name__ == "__main__":
    pid = int(sys.argv[1]);
    f = open('./realtimeRAM','w+');
    measureRAM(f, pid);
    f.close();