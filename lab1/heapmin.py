from heapq import heappop, heappush

#Implementazione di uno heap minimo
pq = []                         # list of entries arranged in a heap

def add_node(node):
    heappush(pq, (node.cost(), node))


def pop_node():
    try:
        return heappop(pq)[1]
    except:
        return None