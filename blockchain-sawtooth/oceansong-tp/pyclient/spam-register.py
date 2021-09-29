import sys
import os
import time
import threading

RESTAPI = "http://172.21.0.3:8008"
start = int(sys.argv[1])
end = int(sys.argv[2]) + 1
mid = int((start+end)/2)
cmd = "./ocean register ./data/node1.json node"

def firstThread (number, limit):
    while (number < limit):
        startMeasure = time.time()
        result = os.system(cmd+ str(number))
        stopMeasure = time.time()
        file.write("1\t" + str(number) + "\t" + str(stopMeasure-startMeasure) + '\n')
        number += 1

def secondThread (number, limit):
    while (number < limit):
        startMeasure = time.time()
        result = os.system(cmd+ str(number))
        time.sleep(2)
        stopMeasure = time.time()
        file.write("2\t" + str(number) + "\t" + str(stopMeasure-startMeasure) + '\n')
        number += 1

if __name__ == "__main__":
    file.write("=======================\n")
    x = threading.Thread(target=firstThread, args=(start, mid))
    y = threading.Thread(target=secondThread, args=(mid, end))
    x.start()
    y.start()
    x.join()
    y.join()
    file.close()
    os.system("curl " + RESTAPI + "/state")