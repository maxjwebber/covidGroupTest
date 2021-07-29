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

def processTestedGroups(positiveGroups,negativeGroups):
    # if x is in a group that tested negative then
    # report that x is negative
    # remove x from all groups
    negativeSubjects = set()
    for negGroup in negativeGroups:
        for x in negGroup:
            negativeSubjects.add(x)
            for posGroup in positiveGroups:
                posGroup.remove(x)

    # if x is the only person left in a group that tested positive
    # report that x is positive
    positiveSubjects = set()
    remainingGroups = list()
    remainingSubjects = set()
    for posGroup in positiveGroups:
        if len(posGroup) == 1:
            for x in posGroup:
                positiveSubjects.add(x)
        else:
            remainingGroups.append(posGroup)
    for group in remainingGroups:
        for x in group:
            if x in positiveSubjects:
                group.remove(x)
            else:
                remainingSubjects.add(x)
    remainingGroups = [group for group in remainingGroups if len(group) != 0]

    return {'negatives': list(negativeSubjects), 'positives': list(positiveSubjects), 'remainingGroups': remainingGroups, 'remainingSubjects': list(remainingSubjects)}

