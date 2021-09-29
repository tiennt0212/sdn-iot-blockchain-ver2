import sys
import os

start = int(sys.argv[1])
end = int(sys.argv[2]) + 1

cmd = "sawtooth keygen node"

for i in range(start, end):
    result = os.system(cmd+ str(i))

os.system("ls ~/.sawtooth/keys")