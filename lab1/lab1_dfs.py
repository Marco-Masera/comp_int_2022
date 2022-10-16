import random 
import numpy as np
nodes_v = 0
class Node:

    remainingElems = None #Set 
    parent = None  
    total_cost = 0
    last_i = 0
    cut = 0
    lists = []

    def __init__(self, elements, lists_, parent, total_cost_, skip = -1): 
        self.total_cost = total_cost_
        self.remainingElems = elements
        self.parent = parent
        list = list = [l.intersectTo_Copy(self.remainingElems) for index, l in enumerate(lists_) if index > skip]
        list.sort(reverse=True, key=lambda x: x.gain)
        self.lists = np.array(list)
        self.last_i = 0
        self.cut = len(self.lists)
        elems = len(self.remainingElems)
        for item in self.lists[::-1]:
            elems -= len(item.transformedSet)
            if (elems <= 0):
                break
            self.cut -= 1
    
    def cost(self):
        elems = len(self.remainingElems)
        if (elems == 0):
            return self.total_cost

        cost = 0
        for i in range(0, len(self.lists)):
            elems -= len(self.lists[i].transformedSet)
            cost += self.lists[i].setCost
            if (elems <= 0):
                return self.total_cost + cost 
            if (len(self.lists[i].transformedSet) == 0):
                return float('inf')
        return float('inf')


    def get_child(self):
        if (self.last_i < self.cut):
            l = self.lists[self.last_i]
            self.last_i += 1
            return Node(
                self.remainingElems - l.transformedSet,
                self.lists,
                self,
                self.total_cost + l.setCost,
                self.last_i - 1
        )
        return None

    

class List:
    originalSet = 0 #Index
    setCost = 0 #Int
    transformedSet = None #Set
    gain = 0
    originalParent = None

    def invalidate(self):
        self.transformedSet = set()
        self.gain = 0

    def __init__(self, content, originalSetIndex, originalParent_ = None, originalCost_ = None):
        self.originalSet = originalSetIndex
        self.transformedSet = set(content)
        if (originalCost_ != None):
            self.setCost = originalCost_
        else:
             self.setCost = len(self.transformedSet)
        self.gain = len(self.transformedSet)/self.setCost
        self.originalParent = originalParent_
        if (self.originalParent == None):
            self.originalParent = self

    def createFromSet(set, index):
        return List(set, index)
    
    def intersectTo(self,newSet):
        self.transformedSet = self.transformedSet.intersection(newSet)
        self.gain = len(self.transformedSet)/self.setCost

    def intersectTo_Copy(self, newSet):
        copy = List(self.transformedSet, self.originalSet, self.originalParent, self.setCost)
        copy.intersectTo(newSet)
        return copy

def dfs_rec(node, bound):
    global nodes_v
    nodes_v += 1
    if (node == None):
            print("Could not find any suitable solution.")
            exit()
    if (len(node.remainingElems)==0):
        print(f"New bound: {node.total_cost}")
        return node.total_cost

    while(True):
        node_ = node.get_child()
        if (node_ == None):
            break 
        if (node_.cost() >= bound):
            continue 
        bound = dfs_rec(node_, bound)
    return bound
        
    

def execute(N, l):
    s_n = set([x for x in range(N)])
    l_l = [List.createFromSet(set(x), index) for index, x in enumerate(l)]

    nodes_visited = 0
    r = dfs_rec(Node(s_n, l_l, None, 0), float('inf'))
    print(f"Found a solution with {r} elements; {nodes_v} nodes visited.")



def problem(N, seed=None):
    random.seed(seed)
    return [
        list(set(random.randint(0, N - 1) for n in range(random.randint(N // 5, N // 2))))
        for n in range(random.randint(N, N * 5))
    ]

def main():
    n = 100
    execute(n, problem(n,42))


main()