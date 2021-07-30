import csv
from opEliminate import processTestedGroups
import sys

if len(sys.argv)<3:
   print("usage is driver.py [csv of positives] [csv of negatives]")
   exit(1)

positiveGroups = list()
negativeGroups = list()
with open(sys.argv[1], newline='') as poscsvfile:
    posreader = csv.reader(poscsvfile, delimiter=' ', quotechar='|')
    for row in posreader:
        positiveGroups.append(row)
with open(sys.argv[2], newline='') as negcsvfile:
    negreader = csv.reader(negcsvfile, delimiter=' ', quotechar='|')
    for row in negreader:
        negativeGroups.append(row)

results = processTestedGroups(positiveGroups,negativeGroups)
outfilename = "eliminationResults.txt"
outfile = open(outfilename,"w")
print("--REMAINING GROUPS--")
outfile.write("--REMAINING GROUPS--\n")
for group in results['remainingGroups']:
    print(str(group))
    outfile.write(str(group)+"\n")
print("--IDENTIFIED POSITIVES--")
outfile.write("--IDENTIFIED POSITIVES--\n")
print(str(results['positiveSubjects']))
outfile.write(str(results['positiveSubjects'])+"\n")
print("--IDENTIFIED NEGATIVES--")
outfile.write("--IDENTIFIED NEGATIVES--\n")
print(str(results['negativeSubjects']))
outfile.write(str(results['negativeSubjects'])+"\n")

outfile.close()
choice = input(str(outfilename)+"saved.")



