import random 
import numpy as np

lists = []
best_sol = None 
nodes_v = 0

#Alternative version that uses dfs strategy with bounds and lower bound cost extimates. Slower than the other one.

class Node:
    usedList = 0 #Index of list used 
    remainingElems = None #Set 
    parent = None  
    stepsTaken = 0
    child_candidates = None 
    last_i = 0 #Index of last visited list

    def __init__(self, remElem_, parent_, stepsTaken_, usedList_): 
        self.remainingElems = remElem_
        self.parent = parent_
        self.stepsTaken = stepsTaken_
        self.usedList = usedList_
        self.last_i = usedList_ + 1

    #Generate a list of child candidates sorted by the gain in the extimate cost of the solution
    def get_child_candidates(self):
        self.child_candidates = []
        for i in range(self.last_i, len(lists)):
            gain_ext = len(self.remainingElems.intersection(lists[i]))
            self.child_candidates.append((gain_ext,i))
        self.child_candidates.sort()
    
    def get_child(self):
        if (self.child_candidates == None):
            self.get_child_candidates()
        if (len(self.child_candidates)==0):
            return None
        best_candidate = self.child_candidates.pop()
        newRemainingElems = self.remainingElems - lists[best_candidate[1]]
        return Node(newRemainingElems, self, self.stepsTaken + 1, best_candidate[1])


    def cost_ext(self):
        remanining = len(self.remainingElems)
        if (remanining<=0):
            return self.stepsTaken
        n = 0
        l = []
        for i in range(self.last_i, len(lists)):
            l.append(len(self.remainingElems.intersection(lists[i])))
        l.sort(reverse=True)
        for elem in l:
            remanining -= elem
            n += 1
            if (remanining <= 0):
                return n+self.stepsTaken
        return float('inf')

    def print_node(self):
        #debug only 
        print(f"Remaining elems: {self.remainingElems}")
        print(f"Used list: {lists[self.usedList]}")
        print(f"Steps: {self.stepsTaken}")
    

def df_s(node, bound):
    global best_sol; global nodes_v
    nodes_v += 1
    cost = node.cost_ext()
    if (cost >= bound):
        return bound
    if (len(node.remainingElems) == 0):
        bound = node.stepsTaken
        best_sol = node 
        print(f"New bound: {bound}")
        return bound 
    while(True):
        node_c = node.get_child()
        if (node_c != None):
            bound = df_s(node_c, bound)
        else:
            return bound 


def execute(N, l_l):
    global lists; global best_sol; global nodes_v
    l_l.sort(key=len, reverse=True)
    lists = np.array([set(l) for l in l_l], dtype=object)
    s_n = set([x for x in range(N)])
    
    df_s(Node(s_n, None, 0, -1),float('inf'))
    if (best_sol != None):
        print_solution(nodes_v, best_sol)

def print_solution(n, last_node):
    print(f"Number of lists needed: {last_node.stepsTaken}")
    print(f"Nodes visited: {n}")
    """while(last_node != None and last_node.usedList >= 0):
        print(f"    >List: {lists[last_node.usedList]}")
        last_node = last_node.parent"""


def problem(N, seed=None):
    random.seed(seed)
    return [
        list(set(random.randint(0, N - 1) for n in range(random.randint(N // 5, N // 2))))
        for n in range(random.randint(N, N * 5))
    ]

def main():
    n = 100
    lists = problem(n,42)
    execute(n, lists)


main()