from clingo_problems import InstanceGenerator, generate_instances
import random

class ThreePartitionGenerator(InstanceGenerator):
    def generate_instance(self, *args, **kwargs) -> str:
        elems = random.randint(10,10)
        instance = ""

        for i in range(1,elems+1):
            rand = random.randint(1,100)
            instance += f"elem({i}, {rand}).\n"
        return instance

if __name__ == "__main__":
    generate_instances(ThreePartitionGenerator())
