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


class TestGroup:
    def __init__(self, set):
        self.set = set
        self.testsPositive = None


def purgeKnownNegative(person, groups):
    for group in groups:
        if person in group.set:
            group.set.remove(person)


n = 720
k = 13
s = 36

S = [TestSubject(True) if x < k else TestSubject(False) for x in range(n)]

# set initial value of r to be iterated in loop
r = 0
idPositive = 0
idNegative = 0
groups = list()

while idPositive + idNegative < n:
    # Form r partitions of S into n/s groups of s people (all together there are rn/s groups)
    r += 1
    idPositive = 0
    idNegative = 0

    for p in range(r):
        random.shuffle(S)
        for g in range(n//s):
            groups.append(TestGroup(set(S[(g*s): ((g+1)*s)])))
    # Test every group
    for group in groups:
        if any(person.hasCOVID19 for person in group.set):
            group.testsPositive = True
        else:
            group.testsPositive = False

    for x in S:
        for group in groups:
            # if x is in a group that tested negative then
            # report that x is negative
            # remove x from all groups
            if x in group.set and not group.testsPositive:
                idNegative += 1
                purgeKnownNegative(x, groups)
                break

    for x in S:
        for group in groups:
            # if x is the only person left in a group that tested positive
            # report that k is positive
            if x in group.set and len(group.set) == 1 and group.testsPositive:
                idPositive += 1
                break

    remaining = n - (idPositive + idNegative)
    groups.clear()
    print('For', r, 'partitions I found', idPositive, 'positives and', idNegative, 'negatives.', remaining, 'remain unconfirmed.')
