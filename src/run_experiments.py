#!/usr/bin/env python3
"""
Clingo Experiment Runner (using Python API)

Runs a Clingo solver on multiple instances and collects performance metrics.

Usage:
    python clingo_experiments.py <solver_file> <instances_dir> [options]

Example:
    python clingo_experiments.py bpcp_solver.lp instances/ -o results.csv -t 60
"""

import argparse
import csv
import signal
import sys
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
import dataclasses
from enum import Enum, auto
from typing import Optional, List
import clingodl

try:
    import clingo
except ImportError:
    print("Error: clingo Python module not found.", file=sys.stderr)
    print("Install it with: pip install clingo", file=sys.stderr)
    sys.exit(1)


class TimeoutException(Exception):
    """Exception raised when solving times out."""

    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout."""
    raise TimeoutException("Solving timeout")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run Clingo experiments on multiple instances using Python API"
    )
    parser.add_argument(
        "solver", type=str, help="Path to the solver file (e.g., solver.lp)"
    )
    parser.add_argument(
        "instances", type=str, help="Directory containing instance files"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="results.csv",
        help="Output CSV file (default: results.csv)",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=300,
        help="Timeout per instance in seconds (default: 300)",
    )
    parser.add_argument(
        "-e",
        "--extension",
        type=str,
        default=".lp",
        help="Instance file extension (default: .lp)",
    )
    parser.add_argument(
        "-c",
        "--const",
        type=str,
        action="append",
        default=[],
        help="Constants to pass to Clingo (e.g., -c bound=10). Can be used multiple times.",
    )
    parser.add_argument(
        "-n",
        "--models",
        type=int,
        default=1,
        help="Number of models to find (default: 1, use 0 for all)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print verbose output"
    )
    parser.add_argument(
        "--theory",
        help="Use a theory propagator. (dl == Difference Logic)",
        choices=["dl"],
        default=None,
    )

    return parser.parse_args()


def find_instances(instances_dir: str, extension: str) -> List[Path]:
    """Find all instance files in the given directory."""
    instances_path = Path(instances_dir)

    if not instances_path.exists():
        print(f"Error: Directory '{instances_dir}' does not exist", file=sys.stderr)
        sys.exit(1)

    if not instances_path.is_dir():
        print(f"Error: '{instances_dir}' is not a directory", file=sys.stderr)
        sys.exit(1)

    instances = sorted(instances_path.glob(f"*{extension}"))

    if not instances:
        print(
            f"Warning: No files with extension '{extension}' found in '{instances_dir}'"
        )

    return instances


class Result(Enum):
    UNKNOWN = auto()
    SAT = auto()
    UNSAT = auto()
    TIMEOUT = auto()

    def __str__(self):
        return f"{self.name}"


@dataclass(kw_only=True)
class Stats:
    instance: str
    result: Result = Result.UNKNOWN
    wall_time: float = 0.0
    solve_time: float = 0.0
    models_found: int = 0
    rules: int = 0
    atoms: int = 0
    choices: int = 0
    constraints: int = 0
    error: Optional[str] = None


def run_clingo_instance(
    solver_file: str,
    instance_file: Path,
    timeout: int,
    constants: List[str],
    models: int,
    verbose: bool,
    theory: Optional[str],
) -> Stats:

    stats = Stats(instance=instance_file.name)

    try:
        # Create control object
        ctl = clingo.Control()

        thy = None
        if theory is not None:
            if theory == "dl":
                thy = clingodl.ClingoDLTheory()
                thy.register(ctl)
                thy.prepare(ctl)

        # Add constants
        for const in constants:
            if "=" in const:
                name, value = const.split("=", 1)
                ctl.add("base", [], f"#const {name}={value}.")

        # Load files
        if verbose:
            print(f"  Loading {solver_file} and {instance_file}")

        ctl.load(solver_file)
        ctl.load(str(instance_file))

        # Ground
        if verbose:
            print(f"  Grounding...")

        if timeout > 0 and hasattr(signal, "SIGALRM"):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)

        ctl.ground([("base", [])])

        # Solve
        if verbose:
            print(f"  Solving...")

        model_count = 0

        # yeild an iterable returning Model objects
        if thy:
            handle = ctl.solve(yield_=True, on_model=thy.on_model)
        else:
            handle = ctl.solve(yield_=True)

        with handle:
            for _ in handle:  # loop on models
                model_count += 1
                if verbose:
                    print(f"    Found model {model_count}")
                if models > 0 and model_count >= models:
                    break

            solve_result = handle.get()

        # Get statistics after solving
        statistics = ctl.statistics
        if "problem" in statistics and "lp" in statistics["problem"]:
            lp_stats = statistics["problem"]["lp"]
            if "rules" in lp_stats:
                stats.rules = lp_stats["rules"]
            if "atoms" in lp_stats:
                stats.atoms = lp_stats["atoms"]
            if "choices" in lp_stats:
                stats.choices = lp_stats["choices"]
            if "constraints" in lp_stats:
                stats.constraints = lp_stats["constraints"]

        stats.models_found = model_count

        # Cancel timeout
        if timeout > 0 and hasattr(signal, "SIGALRM"):
            signal.alarm(0)

        # Determine result
        if solve_result.satisfiable:
            stats.result = Result.SAT
        elif solve_result.unsatisfiable:
            stats.result = Result.UNSAT
        elif solve_result.unknown:
            stats.result = Result.UNKNOWN

        # Get additional statistics

        stats.solve_time = statistics["summary"]["times"]["solve"]
        stats.wall_time = statistics["summary"]["times"]["total"]

        if verbose:
            print(
                f"  Result: {stats.result}, "
                f"Wall: {stats.wall_time}s, "
                f"Solve: {stats.solve_time}s, "
                f"Models: {stats.models_found}, "
                f"Rules: {stats.rules}"
            )

    except TimeoutException:
        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)
        stats.result = Result.TIMEOUT
        stats.wall_time = timeout
        stats.error = f"Timeout after {timeout}s"
        if verbose:
            print(f"  TIMEOUT after {timeout}s")

    except FileNotFoundError as e:
        stats.error = f"File not found: {e}"
        print(f"Error: {stats.error}", file=sys.stderr)

    except Exception as e:
        stats.error = str(e)
        print(f"Error processing {instance_file.name}: {e}", file=sys.stderr)
        if verbose:
            import traceback

            traceback.print_exc()

    return stats


def write_results_csv(results: List[Stats], output_file: str):
    """Write results to a CSV file."""
    if not results:
        print("No results to write")
        return

    fieldnames = [
        "instance",
        "result",
        "wall_time",
        "solve_time",
        "models_found",
        "rules",
        "atoms",
        "choices",
        "constraints",
        "error",
    ]

    try:
        with open(output_file, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows([dataclasses.asdict(r) for r in results])

        print(f"\nResults written to {output_file}")

    except Exception as e:
        print(f"Error writing results to {output_file}: {e}", file=sys.stderr)


def print_summary(results: List[Stats]):
    """Print a summary of the results."""
    if not results:
        return

    total = len(results)
    sat = sum(1 for r in results if r.result == Result.SAT)
    unsat = sum(1 for r in results if r.result == Result.UNSAT)
    timeout = sum(1 for r in results if r.result == Result.TIMEOUT)
    unknown = sum(1 for r in results if r.result == Result.UNKNOWN)
    errors = sum(
        1 for r in results if r.error is not None and r.result != Result.TIMEOUT
    )

    avg_wall_time = sum(r.wall_time for r in results) / total if total > 0 else 0
    avg_solve_time = sum(r.solve_time for r in results) / total if total > 0 else 0
    avg_rules = sum(r.rules for r in results) / total if total > 0 else 0
    avg_atoms = sum(r.atoms for r in results) / total if total > 0 else 0

    # Calculate averages only for solved instances
    solved = [r for r in results if r.result in ["SAT", "UNSAT"]]
    if solved:
        avg_solved_wall = sum(r.wall_time for r in solved) / len(solved)
        avg_solved_solve = sum(r.solve_time for r in solved) / len(solved)
    else:
        avg_solved_wall = 0
        avg_solved_solve = 0

    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    print(f"Total instances:         {total}")
    print(f"SAT:                     {sat} ({sat/total*100:.1f}%)")
    print(f"UNSAT:                   {unsat} ({unsat/total*100:.1f}%)")
    print(f"TIMEOUT:                 {timeout} ({timeout/total*100:.1f}%)")
    print(f"UNKNOWN:                 {unknown} ({unknown/total*100:.1f}%)")
    if errors > 0:
        print(f"ERRORS:                  {errors} ({errors/total*100:.1f}%)")
    print(f"\nAverage wall time:       {avg_wall_time:.3f}s (all instances)")
    print(f"Average solve time:      {avg_solve_time:.3f}s (all instances)")
    if solved:
        print(f"Average wall time:       {avg_solved_wall:.3f}s (solved only)")
        print(f"Average solve time:      {avg_solved_solve:.3f}s (solved only)")
    print(f"\nAverage rules:           {avg_rules:.0f}")
    print(f"Average atoms:           {avg_atoms:.0f}")
    print("=" * 60)


def main():
    """Main function."""
    args = parse_arguments()

    # Check solver file exists
    if not Path(args.solver).exists():
        print(f"Error: Solver file '{args.solver}' does not exist", file=sys.stderr)
        sys.exit(1)

    # Find instances
    instances = find_instances(args.instances, args.extension)

    if not instances:
        sys.exit(1)

    print(f"Found {len(instances)} instance(s)")
    print(f"Solver: {args.solver}")
    print(f"Timeout: {args.timeout}s per instance")
    if args.const:
        print(f"Constants: {', '.join(args.const)}")
    print(f"Models to find: {args.models if args.models > 0 else 'all'}")
    print(f"Output: {args.output}")
    print()

    # Run experiments
    results: List[Stats] = []
    for i, instance in enumerate(instances, 1):
        print(f"[{i}/{len(instances)}] Processing {instance.name}...", end=" ")
        sys.stdout.flush()

        stats = run_clingo_instance(
            args.solver,
            instance,
            args.timeout,
            args.const,
            args.models,
            args.verbose,
            args.theory,
        )

        results.append(stats)

        if not args.verbose:
            print(
                f"{stats.result} "
                f"(wall: {stats.wall_time}s, "
                f"solve: {stats.solve_time}s, "
                f"models: {stats.models_found})"
            )

    # Write results
    write_results_csv(results, args.output)

    # Print summary
    print_summary(results)


if __name__ == "__main__":
    main()
