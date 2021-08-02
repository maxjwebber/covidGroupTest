import random
import math
import csv

n = 720
k = 36
s = n//k
runs = 50000
groupsPerPartition = n//s

L = 10

filename = "grouptests_"+str(n)+"n_"+str(k)+"k_"+str(s)+"s_"+str(runs)+"runs.csv"
S = [(x//s) for x in range(n)]
digitsPerWord = int(math.log(pow(2,64), groupsPerPartition))
params = [n, groupsPerPartition, L, digitsPerWord]


with open(filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='|')
    writer.writerow(params)
    for run in range(runs*L):
        random.shuffle(S)
        writer.writerow(S)