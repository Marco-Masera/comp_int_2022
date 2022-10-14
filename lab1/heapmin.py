from heapq import heappop, heappush

#Simple min heap implementation
pq = []

def add_node(node, priority):
    if (node == None):
        return
    heappush(pq, (node.cost(), priority, node))


def pop_node():
    try:
        return heappop(pq)[2]
    except:
        return None
