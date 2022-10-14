# Times:
* N=5: 3 lists needed, 3 nodes visited.
* N=10: 3 lists needed, 3 nodes visited.
* N=20: 4 lists needed, 6 nodes visited.
* N=50: 4 lists needed, 10 nodes visited.
* N=100: 5 lists needed, 696 nodes visited.
* N=150: 6 lists needed, 11390 nodes visited.
* N=180: 5 lists needed, 20250 nodes visited.
* N=500 / N=1000: could not compute it.

The number of nodes visited is relatively small but it comes at the expense of a slower computation of each one.
It also grow exponentially so finding the best solution for big N is not doable.

# How the program works

## General strategy
The program uses an informed strategy based on the A* search.

## tree shape
The program builds the solution-space tree in this way:
Given L_L the list of lists and C the list of numbers from 0 to N-1:
* Each node contains an ordered subset of L_L of lists its children are allowed to visit and the subset of C not yet covered by its ancestors' lists.
* Each child of the node uses one list of the subset owned by the parent.
* Nodes are not allowed to use lists already used by their left brothers. Meaning a Node containing the list [A, B, C] will create three children such as:
* * The first one uses the list A and owns the subset [ B, C ]
* * The second one uses list B and owns the subset [ C ]
* * The third uses list C and cannot have children of its own.
* That way we avoid permutations of the same set of lists in the solution-space.

## Distance function
The program use a function to compute a lower bound for possible solutions given a Node n:
*lower_bound(Node) = N | the best path from Node to a solution has length >= N
The function is defined as:
* Given the set of lists owned by the Node, the intersection between their elements and the elements of Node is computed (i.e. elements not in need to be covered are discarted)
* The functions returns the smallest number of lists needed such as the sum of their length is >= the number of elements to be covered.

## Lazy tree creation
To avoid too much memory usage (it already uses a lot) the three is computed lazily. When a node is visited, instead of creating all of its children and inserting them into the min-heap, only the best child (the one with smallest lower_bound) is created. When a Node is visited, its right brother, if existing, is created.


