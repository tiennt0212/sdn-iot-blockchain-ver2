register = open('1.timeHandleRegister', 'w')
modelrequest = open ('2.timeHandleModelRequest', 'w')
taskassign = open('3.timeHandleTaskAssign', 'w')
modelverify = open('4.timeHandleModelVerify', 'w')

with open('TimeHandle.txt', 'r') as f:
    for line in f:
        info = line.split('\t')
        if (info[0] == 'register'):
            register.write(info[1])
            continue;
        elif (info[0] == 'model-request'):
            modelrequest.write(info[1])
            continue;
        elif (info[0] == 'task-assign'):
            taskassign.write(info[1])
            continue;
        elif (info[0] == 'model-verify'):
            modelverify.write(info[1])
            continue

register.close()
modelrequest.close()
taskassign.close()
modelverify.close()