## Solutions:
I tried two different approaches:
* A* search
* DF search with bounds and using the same heuristic function used in the A* search to anticipate branch pruning.

# Times:
* N=5: 5 elements.
* * A*: 3 nodes visited.
* * DFS: 6 nodes visited.

* N=10: 10 elements.
* * A*: 3 nodes visited.
* * DFS: 12 nodes visited.

* N=20: 23 elements.
* * A*: 27 nodes visited.
* * DFS: 34 nodes visited.

* N=50: 65 elements.
* * A*: could not finish.
* * DFS: 2879 nodes visited.

* N=100 and >100: could not finish.

The A* solution visits less nodes, but it comes at the expense of a significantly bigger memory usage and slower computation of each node.