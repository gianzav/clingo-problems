import argparse
import os
import sys

class InstanceGenerator:
    def generate_instance(self, *args, **kwargs) -> str:
        raise NotImplementedError

def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Problem instance generator.")
    p.add_argument("num_instances", type=int)
    p.add_argument("output_dir", type=str)
    return p


def generate_instances(gen: InstanceGenerator, *args, **kwargs):
    p = make_parser()
    cliargs = p.parse_args()

    dirname = cliargs.output_dir.removesuffix("/")

    if cliargs.num_instances <= 0:
        sys.exit(f"Number of instances must be > 0")

    try:
        os.mkdir(dirname)

        for x in range(1, cliargs.num_instances+1):
            with open(os.path.join(dirname, f"{x}.lp"), "w") as f:
                f.write(gen.generate_instance(*args, **kwargs))

        print(f"{cliargs.num_instances} problem instances generated in directory {dirname}")

    except FileExistsError:
        sys.exit(f"Directory {dirname} already exists")

if __name__ == "__main__":
    sys.exit("This module is not meant to be called on its own.")
