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
import pickle
from collections import defaultdict
import networkx as nx
from os import path
import sys
import copy

class TestGroup:
    def __init__(self):
        self.set = set()
        self.testsPositive = None

# My Graph Matcher
class MGM(nx.algorithms.isomorphism.GraphMatcher):
    def get_isomorphisms_if_isomorphic(self):
        """Returns False if G1 and G2 are not isomorphic graphs.
        Else, returns a list containing a maximum of NUM_MAPPINGS mappings between the two graphs from G1 to G2.
        """
        NUM_MAPPINGS = 1
        # Check global properties
        if self.G1.order() != self.G2.order():
            return False

        # Check local properties
        d1 = sorted(d for n, d in self.G1.degree())
        d2 = sorted(d for n, d in self.G2.degree())
        if d1 != d2:
            return False

        try:
            x = list()
            for element in self.isomorphisms_iter():
                x.append(element)
                if len(x) == NUM_MAPPINGS:
                    return x
            return x
        except StopIteration:
            return False


if len(sys.argv) < 2:
    print("Input should be: generateIsoClasses.py graphs.p")
    exit(1)
if not path.exists(sys.argv[1]):
    print("File not found: " + sys.argv[1])
    exit(1)

# now that we have the training data, we can organize it by IsoClass
# then when I have a test case, I can compare it against each IsoClass until I find a match.
# then we can get statistics about the Facets in that IsoClass.
numIsoClasses = 0
isoID = 0
# classes of graphs, such that isoClasses[i][j] is the jth graph detected of the ith type identified
isoClasses = list()
# isomorphisms[i][j][k] maps a node in isoClass[i][0] to a node in isoClass[i][j]. for every k, an equivelant mapping.
isomorphisms = defaultdict(dict)

nm = nx.algorithms.isomorphism.categorical_node_match("bipartite", 0)
with open(sys.argv[1], 'rb') as f:
    graphs = pickle.load(f)

for num in range(1, len(graphs)):
    i = len(graphs) - num
    instances = 0
    subject = graphs[i]
    if 'isoID' not in subject.graph:
        subject.graph['isoID'] = isoID
        isoClasses.append(list())
        isoClasses[isoID].append(subject)
        while i > 0:
            i -= 1
            if 'isoID' not in graphs[i].graph:
                if subject.number_of_nodes() == graphs[i].number_of_nodes():
                    if subject.number_of_nodes() == 0:
                        instances += 1
                        isoClasses[isoID].append(graphs[i])
                        graphs[i].graph['isoID'] = isoID
                        isomorphisms[isoID][instances] = list()
                    else:
                        matcher = MGM(subject, graphs[i], node_match=nm)
                        newIsomorphisms = matcher.get_isomorphisms_if_isomorphic()
                        if newIsomorphisms is not False:
                            graphs[i].graph['isoID'] = isoID
                            instances += 1
                            isoClasses[isoID].append(graphs[i])
                            isomorphisms[isoID][instances] = newIsomorphisms
        print("ID "+str(isoID)+" done")
        isoID += 1
if 'isoID' not in graphs[0].graph:
    # this would only happen if this graph matched none of the others, which is quite unlikely but still possible
    graphs[0].graph['isoID'] = isoID
    isoClasses.append(list())
    isoClasses[isoID].append(graphs[0])

print("All Iso Classes identified/organized. Calculating facet infection rate probabilities.")
'''
All the graphs are sorted in the isoClasses list
We want to use the mappings of each node to get the nodes, in order, for each facet
Then we can express every isoClass as a single graph where each node contains a probability of infection for that node
'''
statsGraphs = list()

for i in range(isoID):
    statsGraphs.append(copy.deepcopy(isoClasses[i][0]))
    statsGraphs[i].graph['numInstances'] = 1
    del statsGraphs[i].graph['testdata']
    del statsGraphs[i].graph['partitions']
    for instance in isomorphisms[i].keys():
        statsGraphs[i].graph['numInstances'] += len(isomorphisms[i][instance])

    for node in statsGraphs[i].nodes(data=True):
        try:
            if node[1]['bipartite'] == 0:
                sum = node[1]['hasCOVID19']
                for instance in isomorphisms[i].keys():
                    for mapping in isomorphisms[i][instance]:
                        nextNodeID = mapping.get(node[0])
                        nextGraph = isoClasses[i][instance]
                        sum += nextGraph.nodes[nextNodeID]['hasCOVID19']
                statsGraphs[i].nodes[node[0]]['infectionProbability'] = sum / statsGraphs[i].graph['numInstances']
        except KeyError:
            print("KeyError: " + str(node))
            break


for i in range(isoID):
    for node in statsGraphs[i].nodes(data=True):
        try:
            if node[1]['bipartite'] == 0:
                del node[1]['hasCOVID19']
        except KeyError:
            print("KeyError: " + str(node))
            break

outfilename = "isoClasses"+sys.argv[1][6:]

with open(outfilename,'wb') as f:
    pickle.dump(statsGraphs, f)

print("Stats collected for all isoClasses.")
