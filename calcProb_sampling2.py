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
import random
import timeit
from os import path
import sys
from collections import defaultdict


if len(sys.argv) < 2:
    print("Input should be: calcProb_sampling2.py [remaining].p")
    exit(1)
if not path.exists(sys.argv[1]):
    print("File not found: " + sys.argv[1])
    exit(1)


def countString(s):
    #this will count the strings that make B true as well as those that make A int. B true for each subject.
    global remaining, numStringsB, numStringsAandB,  renumbered

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
outfilename = "probability_sampling"+sys.argv[1][9:-1]+"txt"
outfile = open(outfilename,"w")
starttime = timeit.default_timer()
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
            if (numSubjects > 29 and numSubjects < 40):
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
                upperBound = 0
                lowerBound = 0
                m = numSubjects*p
                probSum = 0
                probXgreaterthan = dict()
                for i in range(numSubjects):
                    probSum += math.comb(numSubjects, i) * pow(p, i) * pow(1-p, numSubjects-i)
                    probXgreaterthan[i] = 1 - probSum
                #outerKeyIndex is the index of our "key subject". once a key subject's bounds have converged, increment the index.
                outerKeyIndex = 0
                k = 0
                if numSubjects > 0:
                    renumbered.clear()
                    for index, subject in enumerate(remaining[run][partition]['subjects']):
                        renumbered[subject] = index

                    while outerKeyIndex<numSubjects and k<=numSubjects:
                        print("k="+str(k))
                        outfile.write("k=" + str(k)+"\n")
                        numStringsB = 0
                        numStringsAandB.clear()
                        numStringsXequalsk = 0
                        probComponent = pow(p, k) * pow(1 - p, numSubjects - k)
                        nchoosek = math.comb(numSubjects, k)
                        samplesSoFar = 0
                        numSamples = 1
                        sequence = [1 if x < k else 0 for x in range(numSubjects)]
                        innerKeyIndex = 0
                        while innerKeyIndex<numSubjects:
                            for sample in range(samplesSoFar, numSamples):
                                random.shuffle(sequence)
                                countString(sequence)
                            samplesSoFar = numSamples
                            if numStringsB > 0:
                                key = remaining[run][partition]['subjects'][innerKeyIndex]
                                probBgivenXequalsk = numStringsB / numSamples
                                probAandBgivenXequalsk = numStringsAandB.get(key, 0)/numSamples
                                # upperBound is (P(A ∩ B | X=k) + 3sqrt(P(A ∩ B | X=k)(1-P(A ∩ B | X=k)/m) / (P(B | X=k) - 3sqrt(P(B | X=k)(1-P(B |X=k)/m))
                                upperBound = (probAandBgivenXequalsk + 3*math.sqrt(probAandBgivenXequalsk*(1-probAandBgivenXequalsk/numSamples))) / (probBgivenXequalsk - 3*math.sqrt(probBgivenXequalsk*(1-probBgivenXequalsk/numSamples)))
                                # lowerBound is (P(A ∩ B | X=k) - 3sqrt(P(A ∩ B | X=k)(1-P(A ∩ B | X=k)/m) / (P(B | X=k) + 3sqrt(P(B | X=k)(1-P(B |X=k)/m))
                                lowerBound = (probAandBgivenXequalsk - 3*math.sqrt(probAandBgivenXequalsk*(1-probAandBgivenXequalsk/numSamples))) / (probBgivenXequalsk + 3*math.sqrt(probBgivenXequalsk*(1-probBgivenXequalsk/numSamples)))
                                if .001/numSubjects > upperBound - lowerBound:
                                    innerKeyIndex += 1
                                else:
                                    print(upperBound - lowerBound)
                                    numSamples *= 2
                            else:
                                #we can't keep checking bounds if no strings exist that make B true for this k. If we haven't found a single hit after checking as many strings as brute force would, it's time to move on to the next k.
                                if nchoosek<numSamples:
                                    break
                                numSamples *= 2

                        print(str(numSamples) + " samples used. Bounds differ by " + str(upperBound - lowerBound))
                        outfile.write(str(numSamples) + " samples used. Bounds differ by " + str(upperBound - lowerBound) + "\n")
                        probsB.append((numStringsB / numSamples) * nchoosek * probComponent)
                        for subject in remaining[run][partition]['subjects']:
                            if subject in numStringsAandB:
                                probsAandB[subject].append((numStringsAandB[subject]/numSamples) * nchoosek * probComponent)
                            else:
                                probsAandB[subject].append(0)

                        probBandXlessthanorequaltok = sum(sorted(probsB))
                        checkingBounds = True
                        while checkingBounds:
                            key = remaining[run][partition]['subjects'][outerKeyIndex]
                            probAandBandXlessthanorequaltok = sum(sorted(probsAandB[key]))
                            # upperBound =  (P(A and B and X ≤ k) + P(X>k))/(P(B and X ≤ k) + P(X>k))
                            upperBound = (probAandBandXlessthanorequaltok + probXgreaterthan[k]) / (probBandXlessthanorequaltok + probXgreaterthan[k])
                            # lowerBound = (P(A and B and X ≤ k) + P(A and B | X=k)P(X>k)) / (P(B and X ≤ k) + P(X > k))
                            lowerBound = (probAandBandXlessthanorequaltok + (numStringsAandB[key] / numSamples) * probXgreaterthan[k]) / (probBandXlessthanorequaltok + probXgreaterthan[k])
                            error = upperBound - lowerBound
                            print(str(lowerBound)+" < "+"estimate for subject "+str(key)+ " < "+str(upperBound))
                            outfile.write(str(lowerBound)+" < "+"estimate for subject "+str(key)+ " < "+str(upperBound) + "\n")
                            if error < .01*(1-((k+1)/numSubjects)):
                                midpointEstimates.append((upperBound + lowerBound)/2)
                                intervals.append(error / 2)
                                outerKeyIndex+=1
                                if outerKeyIndex == numSubjects:
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
                    print("subject #" + str(subject) + " has a " + str(midpointEstimates[subjectIndex]*100)+" + or - " + str(intervals[subjectIndex]*100) + " percent chance to be positive.")
                    outfile.write("subject #" + str(subject) + " has a " + str(midpointEstimates[subjectIndex]*100)+" + or - " + str(intervals[subjectIndex]*100) + " percent chance to be positive.\n")

print(timeit.default_timer()-starttime)

