import random 
from heapmin import add_node, pop_node


class Node:
    usedList = 0 
    remainingElems = None #Set 
    parent = None  
    stepsTaken = 0
    child_candidates = None 
    last_i = 0
    lists = []

    def __init__(self, remElem_, parent_, stepsTaken_, usedList_, lists_): 
        self.remainingElems = remElem_
        self.parent = parent_
        self.stepsTaken = stepsTaken_
        self.usedList = usedList_
        self.last_i = 0
        self.lists = []
        for l in lists_:
            x = self.remainingElems.intersection(l)
            if (len(x) > 0):
                self.lists.append(x)
        self.lists.sort(key = len, reverse=True)
    
    def cost(self):
        remanining = len(self.remainingElems)
        #If it's already the solution lets make sure it comes out first from the minheap. It helps speeding up.
        if (remanining<=0):
            return -1 
        n = 0
        
        for elem in self.lists: 
            remanining -= len(elem)
            n += 1
            if (remanining <= 0):
                if (n == 1):
                    #Its child is surely the solution, lets make sure it comes out first from the minheap
                    return self.stepsTaken
                return n + self.stepsTaken
        return float('inf')


    #Instead of generating all the children, it only generates the one with the lowest extimated cost.
    # Eventually, other children will be generated when the previous child is visited, with the gest_best_brother method                
    def get_best_child(self):
        if (len(self.lists)==0):
            return None
        l = self.lists.pop(0)
        return Node(self.remainingElems - l, self, self.stepsTaken + 1, l, self.lists)

    def get_best_brother(self):
        if (self.parent != None):
            return self.parent.get_best_child()
        else:
            return None

    #debug only 
    def print_node(self):
        print(f"Remaining elems: {self.remainingElems}")
        print(f"Used list: {lists[self.usedList]}")
        print(f"Steps: {self.stepsTaken}")
    
    #Not very clean - it prevents the heap from throwing exceptions when two nodes have the same cost() value
    def __lt__(self, other):
        return False


def execute(N, l_l):
    global lists
    l_l.sort(key=len, reverse=True)
    s_n = set([x for x in range(N)])
    
    nodes_visited = 0
    add_node(Node(s_n, None, 0, None, l_l), 1) 
    while(True):
        node = pop_node()
        if (node == None):
            print("Could not find any suitable solution.")
            exit()

        if (len(node.remainingElems)==0):
            print("Found a solution :)")
            print(f"Number of lists needed: {node.stepsTaken}")
            print(f"Number of nodes visited: {nodes_visited}")
            
            exit()
        
        #If the extimated cost is equal, nodes with higher "real path" are prioritized
        add_node(node.get_best_child(), -node.stepsTaken)
        add_node(node.get_best_brother(), -node.stepsTaken)
        nodes_visited += 1
    


def problem(N, seed=None):
    random.seed(seed)
    return [
        list(set(random.randint(0, N - 1) for n in range(random.randint(N // 5, N // 2))))
        for n in range(random.randint(N, N * 5))
    ]

def main():
    n = 180
    execute(n, problem(n,42))


main()