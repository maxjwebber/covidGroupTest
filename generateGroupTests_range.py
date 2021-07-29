import random
import math
import csv

n = 720
k = 36
runsPerS = 10000
L = 1
sList = list()


smin = n//(4*k) if n//(4*k) > 1 else 2
smax = (2*n)//k if (2*n)//k < n else n//2
for size in range(smin,smax+1):
    if n%size==0:
        sList.append(size)

for s in sList:
    if n%s == 0:
        groupsPerPartition = n//s
        S = [(x // s) for x in range(n)]
        digitsPerWord = int(math.log(pow(2, 64), groupsPerPartition))
        params = [n, groupsPerPartition, L, digitsPerWord]
        filename = "grouptests_"+str(n)+"n_"+str(k)+"k_"+str(s)+"s_"+str(runsPerS)+"runs.csv"
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|')
            writer.writerow(params)
            for run in range(runsPerS*L):
                random.shuffle(S)
                writer.writerow(S)
            print(filename+" complete")
            csvfile.close()
