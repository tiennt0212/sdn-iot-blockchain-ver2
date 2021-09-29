import sys
import os
import time
import threading

RESTAPI = "http://172.21.0.3:8008"
start = int(sys.argv[1])
end = int(sys.argv[2]) + 1
cmd = "./ocean register ./data/node1.json node"

if __name__ == "__main__":
    while (start < end):
        print("==================================================== {}".format(start))
        result = os.system(cmd+ str(start))
        start += 1
        # time.sleep(2)

    os.system("curl " + RESTAPI + "/state")