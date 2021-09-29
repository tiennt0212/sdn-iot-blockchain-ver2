import sys
import os
import time
import threading

RESTAPI = "http://172.21.0.3:8008"
start = int(sys.argv[1])
end = int(sys.argv[2]) + 1
mid = int((start+end)/2)
cmd = "./ocean task-assign ./data/.secret/token{} ./data/task-assign.json node{}"

def firstThread (number, limit):
    while (number < limit):
        result = os.system(cmd.format(number, number))
        number += 1

def secondThread (number, limit):
    while (number < limit):
        result = os.system(cmd.format(number, number))
        number += 1

if __name__ == "__main__":
    x = threading.Thread(target=firstThread, args=(start, mid))
    y = threading.Thread(target=secondThread, args=(mid, end))
    x.start()
    y.start()
    x.join()
    y.join()
    os.system("curl " + RESTAPI + "/state")