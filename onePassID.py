'''
One-Round Group Testing Algorithm

n = number of people to be tested
p = prevalence (estimated fraction of infected people in our test group)
p = k / n where k is the number of infected people
s = group size
r = number of partitions to perform

S = the set of people to be tested
Form r partitions of S into n/s groups of s people (all together there are rn/s groups)
Test every group
for each person x
     if x is in a group that tested negative then
    report that x is negative
    remove x from all groups
for each person x
     if x is the only person left in a group that tested positive
           report that x is positive
'''
import random


class TestSubject:
    def __init__(self, hasCOVID19):
        self.hasCOVID19 = hasCOVID19
        self.confirmedStatus = None


class TestGroup:
    def __init__(self, set):
        self.set = set
        self.testsPositive = None


def markAndPurgeNegatives(groupToCheck, allGroups):
    if groupToCheck.testsPositive:
        return 0
    else:
        negatives = groupToCheck.set.copy()
        for x in negatives:
            x.confirmedStatus = False
        for thisG in allGroups:
            thisG.set = thisG.set.difference(negatives)
        return len(negatives)


def markUnmarkedPositive(groupToTest):
    if groupToTest.testsPositive and len(group.set) == 1:
        for x in groupToTest.set:
            if x.confirmedStatus:
                return 0
            else:
                x.confirmedStatus = True
                return 1
    else:
        return 0


n = 720
k = 13
s = 36

S = [TestSubject(True) if x < k else TestSubject(False) for x in range(n)]

r = 0
partitions = list()
# if desired, set r > 0 to generate initial partitions before loop starts.
# regardless of the initial choice, ALL PARTITIONS WILL BE SAVED ACROSS LOOPS.
for p in range(r):
    random.shuffle(S)
    partitions.append(S.copy())

idPositive = 0
idNegative = 0
groups = list()

while idPositive + idNegative < n:
    # Form r partitions of S into n//s groups of s people (all together there are rn//s groups)
    r += 1
    idPositive = 0
    idNegative = 0

    random.shuffle(S)
    partitions.append(S.copy())
    for p in partitions:
        for g in range(n//s):
            groups.append(TestGroup(set(p[(g*s): ((g+1)*s)])))

    # Test every group
    for group in groups:
        if any(person.hasCOVID19 for person in group.set):
            group.testsPositive = True
        else:
            group.testsPositive = False

    for group in groups:
        # if x is in a group that tested negative then
        # report that x is negative
        # remove x from all groups
        idNegative += markAndPurgeNegatives(group, groups)

    for group in groups:
        # if x is the only person left in a group that tested positive
        # report that x is positive
        idPositive += markUnmarkedPositive(group)

    remaining = n - (idPositive + idNegative)
    # before wiping, write subject status/group affiliation to file if desired
    # wipe test groups and unmark subjects for next repetition
    groups.clear()
    for subject in S:
        subject.confirmedStatus = None

    print('For', r, 'partition(s) I found', idPositive, 'positives and', idNegative, 'negatives.', remaining, 'remain(s) unconfirmed.')
