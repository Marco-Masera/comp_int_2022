from collapse_state import *
import random 
import numpy as np

def test_pawns():
    for i in range(0,16):
        p = dict()
        p[0] = set([ x for x in range(0,16) if n_bit_in_common(i, x)==0 and x != i ])
        p[1] = set([ x for x in range(0,16) if n_bit_in_common(i, x)==1 and x != i])
        p[2] = set([ x for x in range(0,16) if n_bit_in_common(i, x)==2 and x != i])
        p[3] = set([ x for x in range(0,16) if n_bit_in_common(i, x)==3 and x != i])
        p[4] = set([ x for x in range(0,16) if n_bit_in_common(i, x)==4 and x != i])
        assert pawns[i][0] == p[0]
        assert pawns[i][1] == p[1]
        assert pawns[i][2] == p[2]
        assert pawns[i][3] == p[3]
        assert pawns[i][4] == p[4]


def test_n_bit_in_common():
    assert n_bit_in_common(1, 0) == 3
    assert n_bit_in_common(1, 1) == 4
    assert n_bit_in_common(15, 0) == 0
    assert n_bit_in_common(7, 8) == 0
    assert n_bit_in_common(7, 15) == 3
    assert n_bit_in_common(7, 0) == 1
    assert n_bit_in_common(5, 0) == 2

def test_flat_pawns():
    def actual_test(n):
        #generate random set of pawns
        p = set([x for x in range(0,16)])
        pawns = []
        for _ in range(0,n):
            t = (random.sample(p, 1)[0])
            pawns.append(t)
            p.remove(t)
        pawns = np.array(pawns)
        #compute relationship between them (matrix)
        r = [[]]*n
        for i in range(0,n):
            r[i] = [-1]*n
            for j in range(0,n): 
                r[i][j] = n_bit_in_common(pawns[i], pawns[j])
        #Flat
        pawns[-1] = flat_pawns(pawns[:-1], pawns[len(pawns)-1])
        #Check that relationship is still the same
        for i in range(0,n):
            for j in range(0,n): 
                assert n_bit_in_common(pawns[i], pawns[j]) == r[i][j]
    
    actual_test(6)
    """actual_test(15)
    actual_test(4)
    actual_test(13)"""

"""test_pawns()
test_n_bit_in_common()
for _ in range(0,500):
    test_flat_pawns()"""



def possibilita(elems, dipendenze, posizione):
    if (posizione>=len(dipendenze)):
        return [elems] 

    allowed_set = set([i for i in range(0,15)]) - set(elems)
    for i in range(0, len(elems)):
        n = dipendenze[i][posizione]
        allowed_set = allowed_set.intersection(set(pawns[elems[i]][n]))
    allowed_set = list(allowed_set)
    allowed_set.sort()
    for item in allowed_set:
        p = possibilita(elems + [item,], dipendenze, posizione+1)
        if (p != None):
            return p
    return None

def c_(elems):
    #costruisce lista di dipendenze
    dip = []
    for i in range(0,15):
        dip.append([ n_bit_in_common(elems[i], elems[x]) for x in range(0, 15) ])
    possibilita([], dip, 0)
    #print(possibilita([], dip, 0))


def can_swap(graph, node_a, node_b):
    if (node_a == node_b):
        return False 
    for i in range(0,16):
        if (i == node_a or i == node_b):
            continue 
        if (graph[node_a][i] != graph[node_b][i]):
            return False 
    return True


def alt_(elems):
    #costruisce grafo
    graph = []
    assign = np.array([e for e in elems])
    for i in range(0,16):
        graph.append(np.array([ n_bit_in_common(elems[i], elems[x]) for x in range(0, 15) ]))
        assign[elems[i]] = i 
    for i in range(0,15):
        #muove assegnamento il più in basso possibile
        current_node = graph[assign[i]]
        for j in range(0,16):
            if (can_swap(graph, assign[i], j)):
                assign[i] = j
                break 
    result = np.array([-1]*16)
    for i in range(0,16):
        result[assign[i]] = i 
    #print(result)
    return result    


def test_flat_pawns_alt():
    def actual_test(n):
        #generate random set of pawns
        p = set([x for x in range(0,16)])
        pawns = []
        for _ in range(0,n):
            t = (random.sample(p, 1)[0])
            pawns.append(t)
            p.remove(t)
        pawns = np.array(pawns)
        #compute relationship between them (matrix)
        r = [[]]*n
        for i in range(0,n):
            r[i] = [-1]*n
            for j in range(0,n): 
                r[i][j] = n_bit_in_common(pawns[i], pawns[j])
        #Flat
        pawns = alt_(pawns)
        #Check that relationship is still the same
        for i in range(0,n):
            for j in range(0,n): 
                assert n_bit_in_common(pawns[i], pawns[j]) == r[i][j]
    
    actual_test(16)

test_flat_pawns_alt()

"""import time
start_time = time.time()
for _ in range(1000):
    #flat_pawns([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14], 15)
    #c_([0,1,2,6,4,5,3,7,15,9,10,11,12,13,14,8])
    #Usa np array come elems
    alt_(np.array([0,1,4,3,2,5,6,7,8,9,10,11,12,13,14,15]))
print("--- %s seconds ---" % (time.time() - start_time))"""