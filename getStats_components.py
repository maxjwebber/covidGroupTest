import csv
import pickle
from os import path
import sys
import networkx as nx

if len(sys.argv) < 2:
    print("Input should be: getStats_components.py [remaining].p")
    exit(1)
if not path.exists(sys.argv[1]):
    print("File not found: " + sys.argv[1])
    exit(1)

def getConnectedComponents(groups,subjects):
    G = nx.Graph()
    for subject in subjects:
        G.add_node(subject, bipartite=1)
    for i in range(len(groups)):
        G.add_node("group" + str(i), bipartite=0)
        for nextSubject in groups[i]:
            G.add_edge(nextSubject, "group" + str(i))
    return [G.subgraph(c).copy() for c in sorted(nx.connected_components(G), key=len, reverse=True)]

with open(sys.argv[1], 'rb') as infile:
    remaining = pickle.load(infile)
    p = remaining['k']/remaining['n']
    print("a priori probability of infection is "+str(p))
    maxPartition = 0
    with open('componentsReport.csv', 'w', newline='') as reportfile:
        reportWriter = csv.writer(reportfile, delimiter=',', quotechar='|')
        reportWriter.writerow(['run','partition','groups','subjects','confirmedPos','confirmedNeg','connectedComponents','subjectsInLargestComponent'])

        for run in range(len(remaining)-2):
            for partition in range(len(remaining[run])):
                connectedComponents = getConnectedComponents(remaining[run][partition]['groups'],remaining[run][partition]['subjects'])
                reportWriter.writerow([run,partition,len(remaining[run][partition]['groups']),len(remaining[run][partition]['subjects']),len(remaining[run][partition]['idPositive']),len(remaining[run][partition]['idNegative']),len(connectedComponents),len({n for n, d in connectedComponents[0].nodes(data=True) if d["bipartite"] == 1}) if len(connectedComponents) > 0 else 0])
                if partition > maxPartition:
                    maxPartition = partition
        reportfile.close()
    infile.close()
print(maxPartition)
exit(0)
