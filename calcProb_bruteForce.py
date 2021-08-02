'''
One-Round Group Testing Algorithm

n = number of people to be tested
p = prevalence (estimated fraction of infected people in our test group)
p = k / n where k is the number of infected people
s = group size
partition = number of partitions to perform

S = the set of people to be tested
Form partition partitions of S into n/s groups of s people (all together there are rn/s groups)
Test every group
for each person x
     if x is in a group that tested negative then
    report that x is negative
    remove x from all groups
for each person x
     if x is the only person left in a group that tested positive
           report that x is positive
'''
import math
import pickle
from os import path
import sys
from collections import defaultdict


if len(sys.argv) < 2:
    print("Input should be: calcProb_bruteForce.py [remaining].p")
    exit(1)
if not path.exists(sys.argv[1]):
    print("File not found: " + sys.argv[1])
    exit(1)

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


def countString(s):
    #this will count the strings that make B true as well as those that make A int. B true for each subject.
    global remaining, numStringsB, numStringsAandB, sequencesCollected, renumbered
    #if it makes B true.
    allGroupsTestPositive = True
    for group in remaining[run][partition]['groups']:
        if all(s[renumbered[subject]] == 0 for subject in group):
            allGroupsTestPositive = False
            break
    if allGroupsTestPositive:
        numStringsB+=1
        for subject in remaining[run][partition]['subjects']:
            if s[renumbered[subject]] == 1:
                numStringsAandB[subject]+=1




# global variables for calculating probabilty:
numStringsB = 0
numStringsAandB = defaultdict(int)
outfilename = "probability_bf"+sys.argv[1][9:-1]+"txt"
outfile = open(outfilename,"w")
debugfilename = "probB_bf.txt"
debugfile = open(debugfilename,"w")

with open(sys.argv[1], 'rb') as infile:
    remaining = pickle.load(infile)
    p = remaining['k']/remaining['n']
    print("a priori probability of infection is "+str(p))
    outfile.write("a priori probability of infection is "+str(p)+"\n")
    for run in range(1,2):
        print("---RUN "+str(run)+"---")
        outfile.write("---RUN "+str(run)+"---\n")
        for partition in range(4,5):
            numSubjects = len(remaining[run][partition]['subjects'])
            if numSubjects < 40:

                print("partition " + str(partition + 1)+", "+str(numSubjects)+" subjects")
                outfile.write("partition " + str(partition + 1)+", "+str(numSubjects)+" subjects\n")
                '''
                count the number of n-bit strings with k 1s that make A int. B, B true
                multiply by (p^k)(1-p)^(n-k), you get P(A int. B int. X = k) , P(B int. X=k)
                sum P(A int. B int. X = k) for all k (or until we hit limit), sum P(A int. B int. X = k) for all k (or until we hit limit)...
                you get P(A int. B int. X <= k), P(B int. X <= k)
                P(A int. B int. X <= k) / P(B int. X <= k) = Probability that a person x is infected given that these remaining groups test positive.
                '''

                probsB = list()
                probsAandB = defaultdict(list)
                renumbered = dict()
                midpointEstimates = list()
                intervals = list()

                m = numSubjects*p
                probSum = 0
                probXgreaterthan = dict()
                if remaining['k'] >= m:
                    for i in range(numSubjects,int(numSubjects*p)-1,-1):
                        probXgreaterthan[i] = probSum
                        probSum += math.comb(numSubjects, i) * pow(p, i) * pow(1-p, numSubjects-i)
                else:
                    for i in range(0,int(numSubjects * p)):
                        probSum += math.comb(numSubjects, i) * pow(p, i) * pow(1-p, numSubjects-i)
                        probXgreaterthan[i] = 1 - probSum
                #outerKeyIndex is the index of our "key subject". once a key subject's bounds have converged, increment the index.
                keyIndex = 0
                k = 0
                if numSubjects > 0:
                    while keyIndex<numSubjects and k <= numSubjects:
                        print("k="+str(k))
                        outfile.write("k=" + str(k)+"\n")
                        numStringsB = 0
                        numStringsAandB.clear()
                        renumbered.clear()
                        for index, subject in enumerate(remaining[run][partition]['subjects']):
                            renumbered[subject] = index
                        launchHW(numSubjects, k)
                        probComponent = pow(p, k) * pow(1-p, numSubjects-k)
                        probsB.append(numStringsB*probComponent)
                        for subject in remaining[run][partition]['subjects']:
                            if subject in numStringsAandB:
                                probsAandB[subject].append(numStringsAandB[subject]*probComponent)
                            else:
                                probsAandB[subject].append(0)

                        debugfile.write(str(probsB[k])+"\n")
                        numStringsXequalsk = math.comb(numSubjects,k)
                        probBandXlessthanorequaltok = sum(sorted(probsB))
                        checkingBounds = True
                        while probBandXlessthanorequaltok > 0 and checkingBounds:
                            key = remaining[run][partition]['subjects'][keyIndex]
                            probAandBandXlessthanorequaltok = sum(sorted(probsAandB[key]))
                            # upperBound =  (P(A and B and X ≤ k) + P(X>k))/(P(B and X ≤ k) + P(X>k))
                            upperBound = (probAandBandXlessthanorequaltok + probXgreaterthan[k]) / (probBandXlessthanorequaltok + probXgreaterthan[k])
                            # lowerBound = (P(A and B and X ≤ k) + P(A and B | X=k)P(X>k)) / (P(B and X ≤ k) + P(X > k))
                            lowerBound = (probAandBandXlessthanorequaltok + (numStringsAandB[key] / numStringsXequalsk) * probXgreaterthan[k]) / (probBandXlessthanorequaltok + probXgreaterthan[k])
                            absoluteError = upperBound - lowerBound
                            print(str(lowerBound)+" < "+"estimate for subject "+str(key)+ " < "+str(upperBound))
                            outfile.write(str(lowerBound)+" < "+"estimate for subject "+str(key)+ " < "+str(upperBound) + "\n")
                            if absoluteError < .01:
                                midpointEstimates.append((upperBound + lowerBound)/2)
                                intervals.append(absoluteError/2)
                                keyIndex+=1
                                if keyIndex == numSubjects:
                                    checkingBounds = False
                            else:
                                checkingBounds = False
                        k+=1






                if numSubjects == 0:
                    print("All subjects identified.")
                    outfile.write("All subjects identified.\n")
                else:
                    outfile.write("stopped after k=" + str(k-1) + "\n")
                    if len(remaining[run][partition]['groups']) == 0:
                        print("All groups eliminated.")
                        outfile.write("All groups eliminated.\n")
                    else:
                        print("Remaining Groups:")
                        for group in remaining[run][partition]['groups']:
                            print(str(group))
                            outfile.write(str(group)+"\n")


                    for subjectIndex in range(numSubjects):
                        subject = remaining[run][partition]['subjects'][subjectIndex]
                        print("subject #" + str(subject) + " has a " + str(round(midpointEstimates[subjectIndex]*100,3))+" ±" + str(round(intervals[subjectIndex]*100,3)) + " percent chance to be positive.")
                        outfile.write("subject #" + str(subject) + " has a "+ str(round(midpointEstimates[subjectIndex]*100,3))+" ±" + str(round(intervals[subjectIndex]*100,3)) + " percent chance to be positive.\n")

