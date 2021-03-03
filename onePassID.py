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
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
wb = Workbook()


class TestSubject:
    def __init__(self, id, hasCOVID19):
        self.id = id
        self.hasCOVID19 = hasCOVID19
        self.confirmedStatus = None


class TestGroup:
    def __init__(self, id, set):
        self.id = id
        self.set = set
        self.testsPositive = None


def markAndPurgeNegatives(groupToCheck, allGroups):
    if groupToCheck.testsPositive:
        return 0
    else:
        newNegatives = 0
        negatives = groupToCheck.set.copy()
        for x in negatives:
            if x.confirmedStatus is None:
                newNegatives += 1
                x.confirmedStatus = False
        for thisG in allGroups:
            thisG.set = thisG.set.difference(negatives)
        return newNegatives


def markUnmarkedPositive(groupToTest):
    if groupToTest.testsPositive and len(groupToTest.set) == 1:
        for x in groupToTest.set:
            if x.confirmedStatus:
                return 0
            else:
                x.confirmedStatus = True
                return 1
    else:
        return 0


n = 42
k = 4
s = 6

S = [TestSubject(x, True) if x < k else TestSubject(x, False) for x in range(n)]

r = 0
partitions = list()
idPositive = 0
idNegative = 0
groups = list()

while idPositive + idNegative < n:
    # Form r partitions of S into n//s groups of s people (all together there are rn//s groups)

    r += 1
    sheetName = str(r)+" partition(s)"
    ws = wb.create_sheet(sheetName)

    random.shuffle(S)
    partitions.append(S.copy())
    for p in range(len(partitions)):
        cell = ws.cell(row=(p * (n // s+1)) + 1, column=1, value="PARTITION " + str(p + 1) + " STARTS HERE")
        for g in range(n//s):
            groups.append(TestGroup(str(p)+"-"+str(g), set(partitions[p][(g*s): ((g+1)*s)])))
            i=0
            for person in groups[(p*(n//s))+g].set:
                i+=1
                cell = ws.cell(row=(p*(n//s+1))+g+2, column=i, value=person.id)
                if person.hasCOVID19:
                    cell.font = Font(bold=True)
                if person.confirmedStatus:
                    cell.fill = PatternFill("solid", fgColor="00FF0000")
                elif person.confirmedStatus==False:
                    cell.fill = PatternFill("solid", fgColor="0099CC00")

    # Test every group
    for g in range(len(groups)):
        offset = g//(n//s) + 2
        if any(person.hasCOVID19 for person in groups[g].set):
            groups[g].testsPositive = True
            cell = ws.cell(row=g+offset, column=s + 1, value="(+) Positive")
        else:
            groups[g].testsPositive = False
            cell = ws.cell(row=g+offset, column=s + 1, value="(-) Negative")


    cell = ws.cell(row=1, column=s+3, value="ID/PURGE NEGATIVES")
    for group in groups:
        # if x is in a group that tested negative then
        # report that x is negative
        # remove x from all groups
        idNegative += markAndPurgeNegatives(group, groups)

    for g in range(len(groups)):
        col = s+2
        offset = g // (n // s) + 2
        for person in groups[g].set:
            col+=1
            cell = ws.cell(row=g + offset, column=col, value=person.id)
            if person.hasCOVID19:
                cell.font = Font(bold=True)
            if person.confirmedStatus:
                cell.fill = PatternFill("solid", fgColor="00FF0000")
            elif person.confirmedStatus == False:
                cell.fill = PatternFill("solid", fgColor="00C0C0C0")

    for group in groups:
        # if x is the only person left in a group that tested positive
        # report that x is positive
        idPositive += markUnmarkedPositive(group)

    cell = ws.cell(row=1, column=2*s+4, value="ID SINGLETON POSITIVES")
    for g in range(len(groups)):
        col = 2*s+3
        offset = g // (n // s) + 2
        for person in groups[g].set:
            col += 1
            cell = ws.cell(row=g + offset, column=col, value=person.id)
            if person.hasCOVID19:
                cell.font = Font(bold=True)
            if person.confirmedStatus:
                cell.fill = PatternFill("solid", fgColor="00FF0000")
            elif person.confirmedStatus == False:
                cell.fill = PatternFill("solid", fgColor="0099CC00")

    remaining = n - (idPositive + idNegative)
    # before wiping, write subject status/group affiliation to file if desired
    # wipe test groups and unmark subjects for next repetition
    groups.clear()

    print('For', r, 'partition(s) I found', idPositive, 'positives and', idNegative, 'negatives.', remaining, 'remain(s) unconfirmed.')
del wb['Sheet']
wb.save("infographic.xlsx")
