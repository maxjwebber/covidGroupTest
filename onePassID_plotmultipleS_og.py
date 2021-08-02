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

import random
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize


from statistics import mean
import openpyxl

wb = openpyxl.Workbook()


class TestSubject:
    def __init__(self, id, hasCOVID19):
        self.id = id
        self.hasCOVID19 = hasCOVID19


class TestGroup:
    def __init__(self, set):
        self.set = set
        self.testsPositive = None


n = 24
k = 3
runs = 20000
filename = str(n)+"n_"+str(k)+"k_"+str(runs)+"runsPerGroupSize.xlsx"

S = [TestSubject(x, True) if x < k else TestSubject(x, False) for x in range(n)]


nextPartition = list()
idPositive = set()
idNegative = set()
groups = list()
newPositives = set()


ddNumConfirmedPositive = defaultdict(list)
ddNumConfirmedNegative = defaultdict(list)

ws_pos = wb['Sheet']
ws_pos.title = 'Positive'
ws_neg = wb.create_sheet('Negative')


smin = n//(4*k) if n//(4*k) > 1 else 2
smax = (2*n)//k if (2*n)//k < n else n//2

fig_pos = plt.figure()
fig_neg = plt.figure()
#ax = fig.add_subplot(111,projection='3d')
ax_pos = fig_pos.add_subplot(111)
ax_pos.set_ylabel('avg # confirmed positive')
ax_pos.set_xlabel('# of tests')
ax_neg = fig_neg.add_subplot(111)
ax_neg.set_ylabel('avg # confirmed negative')
ax_neg.set_xlabel('# of tests')


#list the s values to help normalize the color map
sList = list()
for size in range(smin,smax+1):
    if n%size==0:
        sList.append(size)

norm = Normalize(vmin=0, vmax=len(sList)-1)
cmap = cm.ScalarMappable(Normalize(0,1), 'brg').get_cmap()

for sIndex in range(len(sList)):
    print("color val is "+str(norm(sIndex))+"\n")
    for run in range(runs):
        r = 0
        idPositive.clear()
        idNegative.clear()
        groups.clear()

        while len(idPositive) + len(idNegative) < n:
            # Form partition partitions of S into n//s groups of s people (all together there are rn//s groups)

            r += 1
            random.shuffle(S)
            nextPartition = S.copy()
            #add groups from new partition, cull those confirmed
            for g in range(n//sList[sIndex]):
                nextSet = set(
                    nextPartition[(g*sList[sIndex]): ((g+1)*sList[sIndex])]).difference(idNegative.union(idPositive))
                if len(nextSet)>0:
                    groups.append(TestGroup(str(r)+"-"+str(g), nextSet))

            # Test every group
            for g in range(len(groups)):
                if any(person.hasCOVID19 for person in groups[g].set):
                    groups[g].testsPositive = True
                else:
                    groups[g].testsPositive = False


            for g in range(len(groups)):
                # if x is in a group that tested negative then
                # report that x is negative
                # remove x from all groups
                if groups[g].testsPositive==False:
                    idNegative = idNegative.union(groups[g].set)
                    purgeSet = groups[g].set.copy()
                    for group in groups:
                        group.set = group.set.difference(purgeSet)

            numGroups = len(groups)
            g=0

            while g<numGroups:
                # if x is the only person left in a group that tested positive
                # report that x is positive
                # remove groups containing the positive (we're done with them)
                if groups[g].testsPositive and len(groups[g].set) == 1:
                    for x in groups[g].set:
                        newPositives.add(x) # x is the lone member of groups[g]
                g+=1

            for pos in newPositives:
                i = len(groups)
                while i > 0:
                    i-=1
                    if pos in groups[i].set:
                        groups.pop(i)

            idPositive=idPositive.union(newPositives)
            newPositives.clear()
            groups = [group for group in groups if len(group.set) > 0]

            ddNumConfirmedPositive[r].append(len(idPositive))
            ddNumConfirmedNegative[r].append(len(idNegative))


    #do this after all runs of a valid s

    for r in ddNumConfirmedPositive.keys():
        if r==1:
            ax_pos.scatter(x=n//sList[sIndex], y=mean(ddNumConfirmedPositive[r]), color=cmap(norm(sIndex)), label='s = '+str(sList[sIndex]))
            ax_neg.scatter(x=n//sList[sIndex], y=mean(ddNumConfirmedNegative[r]), color=cmap(norm(sIndex)), label='s = '+str(sList[sIndex]))
        else:
            for fill in range(len(ddNumConfirmedPositive[r]),runs):
                ddNumConfirmedPositive[r].append(k)
            for fill in range(len(ddNumConfirmedNegative[r]),runs):
                ddNumConfirmedNegative[r].append(n-k)
            ax_pos.scatter(x=r*(n//sList[sIndex]), y=mean(ddNumConfirmedPositive[r]), color=cmap(norm(sIndex)))
            ax_neg.scatter(x=r*(n//sList[sIndex]), y=mean(ddNumConfirmedNegative[r]), color=cmap(norm(sIndex)))

    ddNumConfirmedPositive.clear()
    ddNumConfirmedNegative.clear()
    #end of s value

#do stuff with data
ax_pos.legend(loc='lower right')
ax_neg.legend(loc='lower right')
fig_pos.savefig("pos.png", dpi=175)
img = openpyxl.drawing.image.Image('pos.png')
img.anchor='A1'
ws_pos.add_image(img)
fig_neg.savefig("neg.png", dpi=175)
img = openpyxl.drawing.image.Image('neg.png')
img.anchor='A1'
ws_neg.add_image(img)
print("All runs complete. Scatter plot complete.")

wb.save(filename)
