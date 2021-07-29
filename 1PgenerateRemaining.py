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
import copy
import pickle

WORD_SIZE_BYTES = 8
from os import path
import sys



def repToInt(arr, base):
    llen = len(arr)
    power = 1
    num = 0

    # int equivalent is arr[len-1]*1 +
    # arr[len-2]*base + arr[len-3]*(base^2) + ...
    for i in range(llen - 1, -1, -1):
        if int(arr[i]) >= base:
            print('Invalid Number passed to repToDec:' + arr[i])
            exit(1)
        num += int(arr[i]) * power
        power = power * base
    return num


def intToRep(inputNum, base):
    # Convert input number to given base
    # by repeatedly dividing it by base
    # and taking remainder
    if inputNum == 0:
        return [0]
    result = list()
    while (inputNum > 0):
        result.append(inputNum % base)
        inputNum = inputNum // base
    # Reverse the result
    result = result[::-1]

    return result

class TestGroup:
    def __init__(self):
        self.set = set()
        self.testsPositive = None


if len(sys.argv) < 3:
    print("Input should be: generateIsoClasses.py testdata.bin grouptests.bin")
    exit(1)
if not path.exists(sys.argv[1]):
    print("File not found: " + sys.argv[1])
    exit(1)
if not path.exists(sys.argv[2]):
    print("File not found: " + sys.argv[2])
    exit(1)

idPositive = set()
idNegative = set()
groups = list()
newPositives = set()


testfile = open(sys.argv[1], "rb")
groupfile = open(sys.argv[2], "rb")

params = list()
params.append(int.from_bytes(groupfile.read(2), "big"))
params.append(int.from_bytes(groupfile.read(2), "big"))
params.append(int.from_bytes(groupfile.read(2), "big"))
params.append(int.from_bytes(groupfile.read(2), "big"))

n = int(params[0])
g = int(params[1])
L = int(params[2])
maxValuesPerWord_groups = int(params[3])

params.clear()
params.append(int.from_bytes(testfile.read(2), "big"))
params.append(int.from_bytes(testfile.read(2), "big"))
params.append(int.from_bytes(testfile.read(2), "big"))
params.append(int.from_bytes(testfile.read(2), "big"))

if int(params[0]) != n:
    print("n values don't match. files aren't compatible.")
    exit(1)
params.clear()

s = n // g
run = 0

nextWord_test = testfile.read(WORD_SIZE_BYTES)
nextWord_group = groupfile.read(WORD_SIZE_BYTES)
row = list()
testdata = []
while nextWord_test:
    nextInt = int.from_bytes(nextWord_test, "big")
    nextBaseRep = intToRep(nextInt, 2)
    nextWord_test = testfile.read(WORD_SIZE_BYTES)
    if nextWord_test == b'' and len(row)+len(nextBaseRep) < n:
        nextBaseRep = [0] * (n - len(nextBaseRep) - len(row)) + nextBaseRep
    elif len(nextBaseRep) < 64 and nextWord_test is not None:
        nextBaseRep = [0] * (64 - len(nextBaseRep)) + nextBaseRep
    row.extend(nextBaseRep)
    while len(row) > n:
        testdata.append(row[:n])
        row = row[n:len(row)]
    if len(row) == n:
        testdata.append(row[:])
        row.clear()

print("Test Data Loaded.")
testfile.close()
row.clear()
grouptests = []
k = testdata[0].count(1)

while nextWord_group:
    nextInt = int.from_bytes(nextWord_group, "big")
    nextBaseRep = intToRep(nextInt, g)
    nextWord_group = groupfile.read(WORD_SIZE_BYTES)
    if nextWord_group == b'' and len(row) + len(nextBaseRep) < n:
        nextBaseRep = [0] * (n - len(nextBaseRep) - len(row)) + nextBaseRep
    elif len(nextBaseRep) < maxValuesPerWord_groups and nextWord_group != b'':
        nextBaseRep = [0] * (maxValuesPerWord_groups - len(nextBaseRep)) + nextBaseRep
    row.extend(nextBaseRep)

    while len(row) > n:
        grouptests.append(row[:n])
        row = row[n:len(row)]
    if len(row) == n:
        grouptests.append(row[:])
        row.clear()

groupfile.close()
print("Group Tests Loaded.")

remaining = dict()
remaining['n'] = n
remaining['k'] = k
newGroups = list()
groupTestsIndex = 0
for run in range(1000):
    print("run #" + str(run))
    groups.clear()
    partition = 0
    numRemaining = n
    remaining[run] = list()
    while numRemaining > 0:
        # Form r partitions of S into n//s groups of s people (all together there are rn//s groups)
        for newGroup in range(g):
            newGroups.append(TestGroup())

        for i in range(n):
            if i not in idPositive and i not in idNegative:
                assignment = grouptests[groupTestsIndex][i]
                newGroups[assignment].set.add(i)
        groups.extend(newGroups)
        newGroups.clear()


        # Test every new group
        for i in range(g):
            if any(testdata[run][j] == 1 for j in groups[len(groups) - i - 1].set):
                groups[len(groups) - i - 1].testsPositive = True
            else:
                groups[len(groups) - i - 1].testsPositive = False


        lenG = len(groups)
        for i in range(g):
            # if x is in a group that tested negative then
            # report that x is negative
            # remove x from all groups

            if groups[lenG - i - 1].testsPositive == False:
                idNegative = idNegative.union(groups[lenG - i - 1].set)
                groups.pop(lenG - i - 1)
        for group in groups:
            group.set = group.set.difference(idNegative)



        i = 0

        while i < len(groups):
            # if x is the only person left in a group that tested positive
            # report that x is positive
            # remove groups containing the positive (we're done with them)
            if len(groups[len(groups) - i - 1].set) == 1 and groups[len(groups) - i - 1].testsPositive:
                for x in groups[len(groups) - i - 1].set:
                    newPositives.add(x)  # x is the lone member of groups[g]
            i += 1


        for pos in newPositives:
            i = len(groups)
            while i > 0:
                i -= 1
                if pos in groups[i].set or len(groups[i].set) == 0:
                    groups.pop(i)

        idPositive = idPositive.union(newPositives)
        newPositives.clear()


        #save groups by run, by partition
        remaining[run].append(dict())
        remaining[run][partition]['idPositive'] = copy.deepcopy(idPositive)
        remaining[run][partition]['idNegative'] = copy.deepcopy(idPositive)
        remaining[run][partition]['subjects'] = list({subject for subject in range(n)}.difference(idPositive.union(idNegative)))
        numRemaining = len(remaining[run][partition]['subjects'])
        remaining[run][partition]['groups'] = list()
        for group in groups:
            remaining[run][partition]['groups'].append(group.set.copy())

        partition += 1
        groupTestsIndex += 1
        print(partition)

    idPositive.clear()
    idNegative.clear()
    run += 1

testfile.close()
groupfile.close()

out_filename = "remaining_" + str(n) + "n_" + str(s) + "s_" + str(k) + "k_" + str(run) + "runs.p"

with open(out_filename,'wb') as f:
    pickle.dump(remaining, f)
    print(out_filename+" saved.")
    f.close()
    exit(0)
