import random 
from heapmin import add_node, pop_node,get_size
import numpy as np

class Node:

    remainingElems = None #Set 
    parent = None  
    total_cost = 0
    last_i = 0
    lists = []

    def __init__(self, elements, lists_, parent, total_cost_, skip = -1): 
        self.total_cost = total_cost_
        self.remainingElems = elements
        self.parent = parent
        list = list = [l.intersectTo_Copy(self.remainingElems) for index, l in enumerate(lists_) if index > skip]
        list.sort(reverse=True, key=lambda x: x.gain)
        self.lists = np.array(list)
        self.last_i = 0
    
    def cost(self):
        elems = len(self.remainingElems)
        if (elems == 0):
            return self.total_cost

        cost = 0
        for i in range(self.last_i, len(self.lists)):
            elems -= len(self.lists[i].transformedSet)
            cost += self.lists[i].setCost
            if (elems <= 0):
                return self.total_cost + cost 
            if (len(self.lists[i].transformedSet) == 0):
                return float('inf')
        return float('inf')


    def get_children(self):
        cut = len(self.lists)
        elems = len(self.remainingElems)
        for item in self.lists[::-1]:
            elems -= len(item.transformedSet)
            if (elems <= 0):
                break
            cut -= 1
        return [
            Node(
                self.remainingElems - l.transformedSet,
                self.lists,
                self,
                self.total_cost + l.setCost,
                self.last_i - 1
        )
            for index,l in enumerate(self.lists)
            if index < cut
        ]

    def get_best_child(self):
        best_list = self.lists[self.last_i]
        self.last_i += 1
        return Node(
            self.remainingElems - best_list.transformedSet,
            self.lists,
            self,
            self.total_cost + best_list.setCost,
            self.last_i - 1
        )
    def get_best_brother(self):
        if (self.parent != None):
            return self.parent.get_best_child()
        return None
    
    #Not very clean - it prevents the heap from throwing exceptions when two nodes have the same cost() value
    def __lt__(self, other):
        return False

class List:
    originalSet = 0 #Index
    setCost = 0 #Int
    transformedSet = None #Set
    gain = 0
    originalParent = None

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


def execute(N, l):
    s_n = set([x for x in range(N)])
    l_l = [List.createFromSet(set(x), index) for index, x in enumerate(l)]

    nodes_visited = 0
    add_node(Node(s_n, l_l, None, 0))

    while(True):
        node = pop_node()
        if (nodes_visited % 100 == 0):
            print(f"Nodes: {nodes_visited}; size: {get_size()}")

        if (node == None):
            print("Could not find any suitable solution.")
            exit()

        if (len(node.remainingElems)==0):
            print("Found a solution :)")
            print(f"Number of elements needed: {node.total_cost}")
            print(f"Number of nodes visited: {nodes_visited}")
            exit()
        
        #If the extimated cost is equal, nodes with higher "real path" are prioritized
        """add_node(node.get_best_child())
        add_node(node.get_best_brother())"""
        for n in node.get_children():
            add_node(n)
        nodes_visited += 1
    


def problem(N, seed=None):
    random.seed(seed)
    return [
        list(set(random.randint(0, N - 1) for n in range(random.randint(N // 5, N // 2))))
        for n in range(random.randint(N, N * 5))
    ]

def main():
    n = 50
    execute(n, problem(n,42))


main()