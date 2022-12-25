

TODO
Aggiungi distanza da soluzione per minmax!

## Generating dataset
**Why not use alpha beta pruning instead of vanilla min-max?**
Because I want to compute not only the MinMax result but a ration between possible wins/loses from this given state. Since the learning agent will be inevitably fuzzy it can be useful to have a gradient instead of fixed values do discern between more or less good states. This comes at the expense of a way slower time for computing the dataset.
