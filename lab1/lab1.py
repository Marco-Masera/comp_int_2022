import random 
from heapmin import add_node, pop_node
#Basic data structures
l_l = [] #List of sets

class Node:
    remainingLists = []
    remainingElems = None #Set 
    parent = None #Set 
    stepsTaken = 0
    def __init__(self, remainingLists_, remElem_, parent_, stepsTaken_): 
        self.remainingLists = remainingLists_
        self.remainingElems = remElem_
        self.parent = parent_
        self.stepsTaken = stepsTaken_
    
    def cost(self):
        remanining = len(self.remainingElems)
        n = 0
        if (remanining<=0):
            return self.stepsTaken
        for list in self.remainingLists:
            remanining -= len(list)
            n += 1
            if (remanining <= 0):
                return n+self.stepsTaken
        return float('inf')

    def get_children(self):
        i = 0
        nodes = []
        for list in self.remainingLists:
            newReminingLists = self.remainingLists[i:]
            i += 1
            newRemainingElems = self.remainingElems.copy()
            for n in list:
                try:
                    newRemainingElems.remove(n)
                except KeyError:
                    pass  
            nodes.append(Node(newReminingLists, newRemainingElems, self, self.stepsTaken + 1))
        return nodes 

    def print_node(self):
        #debug only 
        print(f"Remaining elems: {self.remainingElems}")
        print(f"Remaining lists: {self.remainingLists}")
        print(f"Steps: {self.stepsTaken}")


def execute(N, lists):
    s_n = set()
    for i in range(N):
        s_n.add(i)
    
    lists.sort(key=len, reverse=True)
    nodes_visited = 0
    add_node(Node(lists, s_n, None, 0))
    while(True):
        node = pop_node()
        if (node == None):
            print("Could not find any suitable solution.")
            exit()
        
        node.print_node()
        if (len(node.remainingElems)==0):
            print("Found a solution :)")
            print_solution(nodes_visited, node)

        for n in node.get_children():
            add_node(n)
        
        nodes_visited += 1
    

def print_solution(n, last_node):
    print(f"Nodes visited: {n}")
    print(f"Number of lists needed: {last_node.stepsTaken}")
    while(last_node != None):
        print(f"    >List: {last_node.usedList}")
        last_node = last_node.parent


def problem(N, seed=None):
    random.seed(seed)
    return [
        list(set(random.randint(0, N - 1) for n in range(random.randint(N // 5, N // 2))))
        for n in range(random.randint(N, N * 5))
    ]

def main():
    execute(3, [ [0,1], [2,3] ])


main()