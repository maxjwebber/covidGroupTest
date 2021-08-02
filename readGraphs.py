import pickle
import networkx as nx
filename = "isoClasses_24n_4s_6k_3r_200000runs.p"
with open(filename, 'rb') as f:
    graphsList = pickle.load(f)
print(filename)
for g in range(len(graphsList)):
    print("---Graph"+str(g)+"---")
    for key in graphsList[g].graph.keys():
        print(str(key)+": "+str(graphsList[g].graph[key]))
    for node in graphsList[g].nodes(data=True):
        print(node)
