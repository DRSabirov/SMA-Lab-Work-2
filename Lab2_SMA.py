import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from networkx.algorithms.community import girvan_newman
from networkx.algorithms.community.quality import modularity


data = pd.read_csv("witcher_network.csv")

unique_values_source = data["Source"].unique()

count = data["Target"].nunique()
print(count)
print(data)

data1 = data

G = nx.from_pandas_edgelist(data1, "Source", "Target")

largest_clique = max(nx.find_cliques(G),key=len)

communities = girvan_newman(G)

first_split = next(communities)

#Determining of network layout
##finding the best number of communities

best_modularity = -1
best_communities = None

for communities1 in girvan_newman(G): #communities1 to avoid mixing of the variable with communities
    q = modularity(G,communities1)

    if q > best_modularity:
        best_modularity = q
        best_communities = communities1

print("Best modularity:", best_modularity)
print("Number of communities:", len(best_communities))

#community table with listing of community and its members
community_table = []

for i, community2 in enumerate(best_communities):
    for node1 in community2: #node1, community2 to avoid intersection with previous code variables
        community_table.append([node1, i+1])

community_df = pd.DataFrame(community_table,columns=["Source","Community"])

##identifying nodes and edges
num_nodes = G.number_of_nodes()
num_edges = G.number_of_edges()

print("Nodes:", num_nodes)
print("Edges:", num_edges)

##Calculating the size of the main communities
###Table of community sizes
community_sizes = []

for i, community in enumerate(best_communities):
    community_sizes.append([i+1,len(community)])

community_df = pd.DataFrame(community_sizes,columns=["Community","Size"])

print(community_df)
###Largest (main) communites (N communities)
community_sizes = pd.DataFrame([(i+1, len(c)) for i, c in enumerate(best_communities)],columns=["Communities","Size"])

##top5 largest communites
top5 = community_sizes.sort_values(by="Size", ascending=False).head(5)

print(top5)

##members of each of top5 communities
sorted_communities = sorted(best_communities, key=len, reverse=True)

for i, community in enumerate(sorted_communities[:5], start=1):
    print(f"\nCommunity {i}")
    print(f"Size: {len(community)}")
    print("Members:")
    print(sorted(list(community)))

## Identifying if Are they clearly separated or strongly interconnected
###modularity

Q = modularity(G, best_communities)
print("Modularity:", Q)

###Internal and exchange edge numbers - wrong calculation
community_map = {} #listing each node and the number of community it relates to

for i, community in enumerate(best_communities):
    for node in community:
        community_map[node] = i

internal_edges = 0
external_edges = 0

for u, v in G.edges():
    if community_map[u] == community_map[v]:
        internal_edges += 1
    else:
        external_edges +=1

total_edges = internal_edges + external_edges

print("Internal edges:", internal_edges)
print("External edges:", external_edges)

print("Internal ratio:",round(100*internal_edges / total_edges, 2),"%")

print(
    "External ratio:",
    round(100 * external_edges / total_edges, 2), "%")
####Most connections remain inside communities if internal > external

###Community connection matrix - showing how many communities interact with each other
n = len(best_communities)

matrix1 = pd.DataFrame(
    0,
    index = [f"C{i+1}" for i in range(n)],
    columns=[f"C{i+1}" for i in range(n)]
)

for u, v in G.edges():
    c1 = community_map[u]
    c2 = community_map[v]

    matrix1.iloc[c1,c2] += 1

    if c1 != c2:
        matrix1.iloc[c2,c1] += 1

matrix1.to_excel("community_connection_matrix.xlsx")
print(matrix1)
####Need to interpret this matrix!!!! - most communities do not interact with each other

###Quantifying separation score
separation_score = (internal_edges / (internal_edges + external_edges))

print("Separation score:", round(separation_score, 3))

#Separation score if 0,8 then well separated

##Addressing question: are communities denser or more central than others
degree = nx.degree_centrality(G)
closeness = nx.closeness_centrality(G)
betweenness = nx.betweenness_centrality(
    G,
    normalized=False
)

results = []

for i, community_check in enumerate(best_communities):
    subgraph_check = G.subgraph(community_check)

    results.append([
        i+1,
        len(community_check),
        subgraph_check.number_of_edges(),
        nx.density(subgraph_check),
        sum(degree[n] for n in community_check) / len(community_check),
        sum(closeness[n] for n in community_check) / len(community_check),
        sum(betweenness[n] for n in community_check) / len(community_check)
    ])

community_stats = pd.DataFrame(
    results,
    columns=[
        "Community",
        "Size",
        "Edges",
        "Density",
        "Avg_Degree",
        "Avg_Closeness",
        "Avg_Betweenness"])

community_stats.sort_values("Density",ascending=False,inplace=True)

community_stats.to_excel("community_statistics.xlsx", index=False)

#Sanity check for matrix and number of nodes:
largest_check = max(best_communities, key=len)
print(largest_check)
subgraph = G.subgraph(largest_check)

print("Nodes in biggest community:",subgraph.number_of_nodes())
print("Edges in biggest community:", subgraph.number_of_edges())

##drawing the picture of the graph (no border of communities yet)

G1 = G

colors = []

for node in G1.nodes():

    if node in largest_check: #largest_clique
        colors.append("red")
    else:
        colors.append("lightblue")

plt.figure(figsize=(100,100)) #3,3

nx.draw(G,pos=nx.spring_layout(G,k=0.5,iterations=20, scale = 20, seed=42),
    node_color=colors,
    node_size=300, 
    with_labels=True,
    font_size=5) 

plt.show()



