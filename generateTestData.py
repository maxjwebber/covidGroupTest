import random
import csv


n = 720
k = 36
runs = 1000000
filename = "testdata_"+str(n)+"n_"+str(k)+"k_"+str(runs)+"runs.csv"

S = [1 if x < k else 0 for x in range(n)]

params = [n, 2, 1, 64]
# maxBytesPerDigit is the max number of bytes per digit, n is the length of the string, 2 is the base, 8 is the number of digits per byte.
with open(filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='|')
    writer.writerow(params)
    for run in range(runs):
        random.shuffle(S)
        writer.writerow(S)
