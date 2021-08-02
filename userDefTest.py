import csv
import math
import sys
from collections import defaultdict


def launchHW(n, # sequence length
                k): #number of 1s)
    sequence = [None] * n
    HWdriver(n,k,sequence,n-1) #suffix to append

def HWdriver(n, # sequence length
                k, #number of 1s
                s, #sequence
            index): #current index

    if k >= 0 and k <= n:
        # 0 ≤ k ≤ n
        if n==0:
           countString(s)
        else:
           s[index] = 0
           HWdriver(n-1,k,s,index-1)
           s[index] = 1
           HWdriver(n-1,k-1,s,index-1)

results = 0
numStringsB = 0
numStringsAandB = 0
renumbered = 0

def countString(s):
    #this will count the strings that make B true as well as those that make A int. B true for each subject.
    global results, numStringsB, numStringsAandB, renumbered
    #if it makes B true.
    allGroupsTestPositive = True
    for group in results['remainingGroups']:
        if all(s[renumbered[subject]] == 0 for subject in group):
            allGroupsTestPositive = False
            break
    if allGroupsTestPositive:
        numStringsB+=1
        for subject in results['remainingSubjects']:
            if s[renumbered[subject]] == 1:
                numStringsAandB[subject]+=1

def processTestedGroups(positiveGroups,negativeGroups):
    # if x is in a group that tested negative then
    # report that x is negative
    # remove x from all groups
    negativeSubjects = set()
    for negGroup in negativeGroups:
        for x in negGroup:
            negativeSubjects.add(x)
            for posGroup in positiveGroups:
                if x in posGroup:
                    posGroup.remove(x)

    # if x is the only person left in a group that tested positive
    # report that x is positive

    positiveSubjects = set()
    remainingGroups = list()
    remainingSubjects = set()
    for posGroup in positiveGroups:
        if len(posGroup) == 1:
            positiveSubjects.add(posGroup[0])
        else:
            remainingGroups.append(posGroup)
    i = 0
    while i < len(remainingGroups):
        cullGroup = False
        for x in remainingGroups[i]:
            if x in positiveSubjects:
                cullGroup = True
            else:
                remainingSubjects.add(x)
        if cullGroup:
            remainingGroups.remove(remainingGroups[i])
        else:
            i+=1
    remainingGroups = [group for group in remainingGroups if len(group) != 0]

    return {'negativeSubjects': list(negativeSubjects), 'positiveSubjects': list(positiveSubjects), 'remainingGroups': remainingGroups, 'remainingSubjects': list(remainingSubjects)}


if len(sys.argv)<3:
   print("usage is userDefTest.py [csv of positives] [csv of negatives]")
   exit(1)

positiveGroups = list()
negativeGroups = list()
with open(sys.argv[1], newline='') as poscsvfile:
    posreader = csv.reader(poscsvfile, delimiter=',', quotechar='|')
    for row in posreader:
        positiveGroups.append(row)
with open(sys.argv[2], newline='') as negcsvfile:
    negreader = csv.reader(negcsvfile, delimiter=',', quotechar='|')
    for row in negreader:
        negativeGroups.append(row)

results = processTestedGroups(positiveGroups,negativeGroups)
outfilename = "eliminationResults.txt"
outfile = open(outfilename,"w")
print("--IDENTIFIED POSITIVES--")
outfile.write("--IDENTIFIED POSITIVES--\n")
print(str(results['positiveSubjects']))
outfile.write(str(results['positiveSubjects'])+"\n")
print("--IDENTIFIED NEGATIVES--")
outfile.write("--IDENTIFIED NEGATIVES--\n")
print(str(results['negativeSubjects']))
outfile.write(str(results['negativeSubjects'])+"\n")
print("--REMAINING GROUPS--")
outfile.write("--REMAINING GROUPS--\n")
for group in results['remainingGroups']:
    print(str(group))
    outfile.write(str(group)+"\n")
print("--REMAINING SUBJECTS--")
outfile.write("--REMAINING SUBJECTS--\n")
print(str(results['remainingSubjects']))
outfile.write(str(results['remainingSubjects'])+"\n")

outfile.close()
myChoioe = ""
print(str(outfilename)+" saved.")
if len(results['remainingSubjects']) > 0:
    if len(results['remainingSubjects']) > 29:
        print("Calculating probability for 30 or more subjects is not recommended and could take a long time.")
    while myChoioe != 'y' and myChoioe != 'n':
        myChoioe = input("Would you like to calculate probability for the remaining subjects? (Y or N): ").lower()
    if myChoioe == 'y':
        myChoioe = -1
        while myChoioe < 0 or myChoioe > 1:
            myChoioe = float(input("Please provide the a priori probability of infection (between 0 and 1): "))
        p = float(myChoioe)
        myChoice = float(input("What margin of error will you target (0 is recommended, higher values may be less accurate): "))
        while myChoioe < 0 or myChoioe > 1:
            myChoice = float(input("What margin of error will you target (0 is recommended, higher values may be less accurate): "))

        numStringsB = 0
        numStringsAandB = defaultdict(int)
        outfilename = "probability_results.txt"
        outfile = open(outfilename, "w")
        '''
            count the number of n-bit strings with k 1s that make A int. B, B true
            multiply by (p^k)(1-p)^(n-k), you get P(A int. B int. X = k) , P(B int. X=k)
            
            sum P(A int. B int. X = k) for all k (or until we hit limit), sum P(A int. B int. X = k) for all k (or until we hit limit)...
            you get P(A int. B int. X <= k), P(B int. X <= k)
            P(A int. B int. X <= k) / P(B int. X <= k) = Probability that a person x is infected given that these remaining groups test positive.
        '''
        errorMargin = myChoice
        probsB = list()
        probsAandB = defaultdict(list)
        renumbered = dict()
        midpointEstimates = list()
        intervals = list()
        numSubjects = len(results['remainingSubjects'])
        m = numSubjects * p
        probsX = list()
        probXgreaterthan = list()
        for i in range(numSubjects+1):
            probsX.append(math.comb(numSubjects, i) * pow(p, i) * pow(1 - p, numSubjects - i))
            probXgreaterthan.append(1-sum(sorted(probsX[0:i])))


        # outerKeyIndex is the index of our "key subject". once a key subject's bounds have converged, increment the index.
        keyIndex = 0
        k = 0
        if numSubjects > 0:
            while keyIndex < numSubjects and k <= numSubjects:
                print("k=" + str(k))
                numStringsB = 0
                numStringsAandB.clear()
                renumbered.clear()
                for index, subject in enumerate(results['remainingSubjects']):
                    renumbered[subject] = index
                launchHW(numSubjects, k)
                probComponent = pow(p, k) * pow(1 - p, numSubjects - k)
                probsB.append(numStringsB * probComponent)
                for subject in results['remainingSubjects']:
                    if subject in numStringsAandB:
                        probsAandB[subject].append(numStringsAandB[subject] * probComponent)
                    else:
                        probsAandB[subject].append(0)

                numStringsXequalsk = math.comb(numSubjects, k)
                probBandXlessthanorequaltok = sum(sorted(probsB))
                checkingBounds = True
                while probBandXlessthanorequaltok > 0 and checkingBounds:
                    key = results['remainingSubjects'][keyIndex]
                    probAandBandXlessthanorequaltok = sum(sorted(probsAandB[key]))
                    # upperBound =  (P(A and B and X ≤ k) + P(X>k))/(P(B and X ≤ k) + P(X>k))
                    upperBound = (probAandBandXlessthanorequaltok + probXgreaterthan[k]) / (
                                probBandXlessthanorequaltok + probXgreaterthan[k])
                    # lowerBound = (P(A and B and X ≤ k) + P(A and B | X=k)P(X>k)) / (P(B and X ≤ k) + P(X > k))
                    lowerBound = (probAandBandXlessthanorequaltok + (numStringsAandB[key] / numStringsXequalsk) *
                                  probXgreaterthan[k]) / (probBandXlessthanorequaltok + probXgreaterthan[k])
                    absoluteError = upperBound - lowerBound
                    print(str(lowerBound) + " < " + "estimate for subject " + str(key) + " < " + str(upperBound))
                    if errorMargin > 0 and absoluteError < errorMargin:
                        midpointEstimates.append((upperBound + lowerBound) / 2)
                        intervals.append(absoluteError / 2)
                        keyIndex += 1
                        if keyIndex == numSubjects:
                            checkingBounds = False
                    elif errorMargin == 0 and k == numSubjects:
                        midpointEstimates.append((upperBound + lowerBound) / 2)
                        keyIndex += 1
                        if keyIndex == numSubjects:
                            checkingBounds = False
                    else:
                        checkingBounds = False
                k += 1

        if numSubjects == 0:
            print("All subjects identified.")
            outfile.write("All subjects identified.\n")
        else:
            outfile.write("stopped after k=" + str(k - 1) + "\n")
            if len(results['remainingSubjects']) == 0:
                print("All groups eliminated.")
                outfile.write("All groups eliminated.\n")
            else:
                print("Remaining Groups:")
                for group in results['remainingGroups']:
                    print(str(group))
                    outfile.write(str(group) + "\n")

            if errorMargin > 0:
                for subjectIndex in range(numSubjects):
                    subject = results['remainingSubjects'][subjectIndex]
                    print("subject #" + str(subject) + " has a " + str(
                        round(midpointEstimates[subjectIndex] * 100,3)) + " + or - " + str(
                        round(intervals[subjectIndex] * 100,3)) + " percent chance to be positive.")
                    outfile.write("subject #" + str(subject) + " has a " + str(
                        round(midpointEstimates[subjectIndex] * 100,3)) + " + or - " + str(
                        round(intervals[subjectIndex] * 100,3)) + " percent chance to be positive.\n")
            else:
                for subjectIndex in range(numSubjects):
                    subject = results['remainingSubjects'][subjectIndex]
                    print("subject #" + str(subject) + " has a " + str(
                        round(midpointEstimates[subjectIndex] * 100,3)) + " percent chance to be positive.")
                    outfile.write("subject #" + str(subject) + " has a " + str(
                        round(midpointEstimates[subjectIndex] * 100, 3)) + " percent chance to be positive.\n")
outfile.close()
