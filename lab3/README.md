# General concept
# # Game representation
The game is represented by the class GameState.py. Which is the same provided by the professor.
The only difference is that now the nimming() function returns a MoveResult enum that contains the information on whether the game is over or not.

# # Agents implementation
Agents implement the PlayerBaseClass class, and need to override the play() method, where they decide for the move to make and call the nimming() function on the game.
An initialize() method can be overridden too if the agent needs to initialize some data before playing.

# # Main:
The main.py file allow to test the different agents. A few global variables at the start of the file allow to chose the game rules and the agents to use al player.
For each agent a constructor method is provided in the same file.


# 3.1: Evolving Rules

The biggest problem in the task of creating the evolving agent was to find a way to encode the possible rules in a way that allowed them to evolve.
After some iterations I decided to go through the route of having some hard-coded rules and let the agent evolve choosing and combining some of them.
The rules are divided into 5 categories:
* **Transformation rules**: They take all the game informations as input, and return a *transformed* list of the rows. Transformed means they can compute some function on each value.
* * transformed_list = [ f(x) for each x in original_list ]
* **Cumulative value rules**: What if we need some value to be computed on all the rows in order to make the correct decisions later? These rules allow to compute this value, which might or might not be used later.
* * cumultive_value = f(list)
* **Chose row rules**: We need a rule to decide which row we act on. These rules can use as input the transformed list values, the K value and the cumulative value previously computed.
* * chosen_row = f(transformed_list, K, cumultive_value)
* **Chose amount rules**: We need to decide how much to remove from the given row, so we have this class of functions. 
* * amount = f(chosen_row, K, cumultive_value)
* **Split rules**: what if we need to apply two different "amount rules" depending on some property of the given row? The split rules returns a boolean telling us about some property of the chosen row.

For each group, some possible rules are provided, and the evolution basically consists in chosing between them. The system allow to easily add more possible rules, increasing the space of possible solutions.
The rules provided allow, theoretically, the agent to evolve in a perfect Nim-Sum agent. It's interesting to see if it will actually reach this point.

Having the genome containing exactly one function for each category isn't a good idea because fitness function would probably be too chaotic; just compare two individuals: one have completely random and useless rules, the other have all the correct rules to act as the "NimSum perfect agent" **except for one**. Are we sure the second individuals would perform better than the first? Probably he would not, even if he's way closer to the perfect solution.
So I made the genome as a probabilistic distribution of rules. Each individual can activate any rules, but with different probabilities, and evolution consists in changing these probabilities.

# # Implementation:
The implementation should be easy to understand. First, for each category of rules, it is provided a class containing rules implementations as functions.
Than the EvolvingAgent class is provided. These objects contain the genome which is a dict in the form
{
    'Rule_Category1': { 'rule1': PROBABILITY, 'rule2': PROBABILITY ... },
    'Rule_Category2': {...}
    ...
}
The play() function use the genome and a random function to decide the rules to use and simply applies them.

# # Evolution:
The evolution of individuals is managed by the **AgentsGim** class.
* Individuals are not only playing with one another, but they are playing against a set of more or less good external agents, called **instructors**. Instructors include
* * The NinSum perfect instructor
* * Generous instructors: implementations of NimSum that sometimes give an advantage to their opponent.
* At each iteration, individuals play against a set of instructors; the fitness is given by the number of victories. The duration of the game is not used as a fitness function when agents lose, because that would simply favour individuals that removes fewer elements at each turn. If the agent lose all the games, he will have fitness 0.

Evolution is (was) divided in three epoch:
* **Epoch one**: first evolution. POPULATION_SIZE individuals are created. At each iterations only the best SURVIVING_SIZE are chosen for reproduction, with random mixing. Random mutations probability is given by the NUM_MUTATION, while MUTATION_SIZE tells how big mutations are in the probabilistic distribution of rules.
* * Individuals fight against instructors.
* * Epoch one finish when either generations surpass MAX_EPOCH_ONE_GEN or when there is no improvement for MAX_EPOCH_ONE_NOIMPROVEMENTS.

* **Epoch two**: refinement. After epoch one, individuals should be good enough to fight one another. This epoch works kind of like the previus but without instructors. Individuals fight each other, hoping to refine their rules selection. Each individual is also tested against the NimSum agent.
* * Epoch two finish when either generations surpass MAX_EPOCH_TWO_GEN or when **at least MIN_PERFECT_MATCHES individuals are able to beat the "perfect" MinSum instructor**.

* **Epoch three**: The hope is that individuals that get here are able to play effectively against the perfect player. Here they play many times only against it, in order to reduce the likelihood of mistakes and become closer to perfect.
* * Only individuals able to beat the NimSum are taken at each generation
* * Individuals play only against the perfect instructor, but they play 6 matches at each time.
* * This epoch ends when an individual is able to beat the perfect instructor all the times, or when MAX_EPOCH_THREE_GEN is surpassed, or when no individual is able to beat NimSum even once.
* * **This epoch was later removed from the program**

# # Results:
For the test I used the following parameters:
* 25 base rules to be combined by individual genomes
* Instructors are made as "generous" NimSum players, that every N moves "gift" the opponent with a favourable move for himself. There are 3 generous instructors with different probability of giving a "gift" and one non-generous NimSum player
* POPULATION_SIZE = 270
* SURVIVING_SIZE = 30
* NUM_MUTATION = 10
* MUTATION_SIZE = 13
* MAX_EPOCH_ONE_NOIMPROVEMENTS = 30

**Epoch 1:** To my own surprise, during Epoch 1 the model took only around 114 generations to learn to consistently beat all the generous instructors. But after that, it never learns to beat the NimSum agent, not even in 800 generations - which is not surprising: the perfect agent doesn't forgive errors, it needs only one suboptimal move from the avversary to beat him. Since evolving agents are probabilistic, they do make mistakes sometimes. An when they all get good enough to beat the generous instructors, there is no selective pressure to improve anymore.

**Epoch 2** is even more surprising, as individuals learn fast enough to beat the NimSum agent too. The first individual able to do that appeared after around generation 21, but it's an isolated case. It takes approximately 190 generations for individuals able to beat NimSum to appear consistently. After 212 generations many agents able to beat NimSum appears.

**Epoch 3** has been removed from the model as it - again, surprisingly - deteriorated performances. Perhaps the reason is the fitness function, that is too strict (only playing against NimSum), giving too many different individual similar fitness values, where there could be significant difference between them. Or perhaps the random mutation caused more damage than gain here. Anyway, if the goal of this epoch was to reduce the population diversity in order to have it converge on the perfect result, it actually did the complete opposite.


**Final thoughts**:  After giving up on epoch three and extending epoch 2, it was possible to generate individuals that behaved exactly like NimSum. It's interesting to see that these individual doesn't necessarily get a better fitness function than other similar-to-optimal ones (like 99.5% of probability of acting like NimSum), as they can happen to win all the games too. This could be probably fixed by having a fitness function that simulate way many games each time: this way it's likely that similar-to-optimal individuals will soon or later commit a mistake and be penalized. But the cost would be a massive increase in computing time.

It's also important noting that there is a big variability in how fast the model converges to a good result. In Point 1 I wrote that during Epoch 1 individuals never learn to beat the NimSum, but in another run later they learned to do that in around 200 generations. In some iterations I didn't get any individual with a perfect set of rues (tho they always get close), other times I got many. Randomness seems to play a very big role in how fast the model converges.

Finally, the set of possible rules isn't massive and the rules able to play as NimSum were added on purpose. If someone with no idea on how NimSum work would try to find a solution with this strategy, he would have to provide a way bigger set of rules, hoping to include the useful ones. This would surely make the model much slower to improve, and it'd be interesting to see if it could converge with around 100x the number of rules it has now.