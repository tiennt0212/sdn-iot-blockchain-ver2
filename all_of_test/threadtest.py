import logging
import threading
import time

start = 1
end = 51
mid = int((start + end)/2)

file = open("./threadprint.txt","a+")

def first(number, limit):
    while(number < limit):
        file.write("First Threading: " + str(number) + '\n')
        number += 1
        time.sleep(0.1)

def second(number, limit):
    while(number < limit):
        file.write("Second Threading: " + str(number) + '\n')
        number += 1
        time.sleep(0.1)

if __name__ == "__main__":
    logging.info("Start threading")
    x = threading.Thread(target=first, args=(start, mid))
    y = threading.Thread(target=second, args=(mid, end))
    x.start()
    y.start()
    x.join()
    y.join()
    file.close()