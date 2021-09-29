import sys
import os

os.system("ls --full-time -lrt | grep 'token' > temp")

index = 1
with open('./temp', 'r') as f:
    for line in f:
        file = line.split(" ")[-1].strip()
        cmd = "mv {} token{}".format(file, index)
        os.system(cmd)
        index+=1