from clingo_problems import InstanceGenerator, generate_instances
import random


class ThreePartitionGenerator(InstanceGenerator):
    def generate_random_instance(self, *args, **kwargs) -> str:
        """Generates a completely randomized instance"""
        elems = random.randint(3, 15)
        instance = ""

        for i in range(1, elems + 1):
            rand = random.randint(1, 10)
            instance += f"elem({i}, {rand}).\n"
        return instance

    def generate_instance(self, *args, **kwargs) -> str:
        """Generates a solvable instance"""
        # generate a number of elements multiple of 3 to avoid trivial unsat
        num_elems = random.choice([3 * i for i in range(10, 20)])
        instance = ""
        target = 100

        # generate the elements 3 by 3 so that any triplet sums to the target value
        elems = [1 for _ in range(num_elems)]
        for i in range(0, num_elems, 3):
            elems[i] = random.randint(1, target - 2)  # 1;18 -> 4
            elems[i + 1] = random.randint(1, target - elems[i] - 1)
            elems[i + 2] = target - elems[i + 1] - elems[i]

        for i, elem in enumerate(elems, start=1):
            instance += f"elem({i}, {elem}).\n"

        return instance


if __name__ == "__main__":
    generate_instances(ThreePartitionGenerator())
