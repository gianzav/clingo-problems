# Basic encoding

- The number of partitions is computed by the solver
- No specific ordering of the assignment of elements to parititions
- No specific ordering of partitions
- Enforcement of the number of elements in each partition using a constraint and the `#count` aggregate

# Optmizations

[opt1](./solver-opt1.lp)

- Constraints to derive quickly UNSAT if it is not possible to partition the elements in triplets or if the sum of the elements is not divided by 3
- Partitions are filled in order based on their id
- Elements are chosen in order based on their id
- The number of elements of each partition is fixed, so no need to use `#count`


[opt2](./solver-opt2.lp)

- The target sum for each partition is derived, so there is no need to compare each pair of partitions

[opt3](./solver-opt3.lp)

- Elements in a partition are ordered. This removes some symmetric solutions

In the clingo[DL] versions, the constraint on the sum of the elements of each partition is encoded with a difference constraint.
