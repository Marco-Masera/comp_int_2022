from heapq import heappop, heappush

#Simple min heap implementation
pq = []

def add_node(node):
    if (node == None):
        return
    heappush(pq, (node.cost(), len(node.remainingElems), node))


def pop_node():
    try:
        return heappop(pq)[2]
    except:
        return None
def get_size():
    return len(pq)
