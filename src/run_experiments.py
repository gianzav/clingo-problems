#!/usr/bin/env python3
"""
Clingo Multi-Solver Experiment Runner (using Python API)

Runs multiple Clingo solvers on instances and compares their performance.

Usage:
    python clingo_experiments.py <solver_files...> -i <instances_dir> [options]

Example:
    python clingo_experiments.py solver1.lp solver2.lp solver3.lp -i instances/ -o results.csv
"""

import argparse
import csv
import sys
import threading
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass
import dataclasses
from enum import Enum, auto
import clingodl
from clingo import ast

try:
    import clingo
except ImportError:
    print("Error: clingo Python module not found.", file=sys.stderr)
    print("Install it with: pip install clingo", file=sys.stderr)
    sys.exit(1)


class TimeoutException(Exception):
    """Exception raised when solving times out."""

    pass


@dataclass
class InstanceConfig:
    solver_file: str
    instance_file: Path
    timeout: int
    constants: List[str]
    models: int
    verbose: bool
    theory: Optional[str]


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run Clingo experiments comparing multiple solvers"
    )
    parser.add_argument(
        "solvers",
        type=str,
        nargs="+",
        help="Paths to solver files (e.g., solver1.lp solver2.lp)",
    )
    parser.add_argument(
        "-i",
        "--instances",
        type=str,
        required=True,
        help="Directory containing instance files",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="results",
        help="Output file prefix (default: results). Will create results.csv and results_comparison.csv",
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
    solver: str
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


@dataclass
class ControlRef:
    ctl: Optional[clingo.Control]

    def interrupt(self):
        if self.ctl is not None:
            self.ctl.interrupt()


class SolveRunner:
    def __init__(
        self,
        instance: InstanceConfig,
        stats: Stats,
        interrupted: threading.Event,
        ctl_ref: ControlRef,
    ):
        self._ctl_ref = ctl_ref
        self._instance = instance
        self._stats = stats
        self._interrupted = interrupted

    def __call__(self, *args, **kwargs):
        """Inner function that does the actual solving."""
        try:
            # Create control object
            ctl = clingo.Control()
            self._ctl_ref.ctl = ctl  # Store reference for interruption

            # Add constants
            for const in self._instance.constants:
                if "=" in const:
                    name, value = const.split("=", 1)
                    ctl.add("base", [], f"#const {name}={value}.")

            # Load files
            if self._instance.verbose:
                print(
                    f"    Loading {self._instance.solver_file} and {self._instance.instance_file}"
                )

            thy = None
            if self._instance.theory is not None:
                if self._instance.theory == "dl":
                    thy = clingodl.ClingoDLTheory()
                    thy.register(ctl)
                    with ast.ProgramBuilder(ctl) as bld:
                        ast.parse_files(
                            [
                                self._instance.solver_file,
                                str(self._instance.instance_file),
                            ],
                            lambda stm: thy.rewrite_ast(stm, bld.add),
                        )

            else:
                ctl.load(self._instance.solver_file)
                ctl.load(str(self._instance.instance_file))

            # Check for interruption before grounding
            if self._interrupted.is_set():
                return

            # Ground
            if self._instance.verbose:
                print(f"    Grounding...")

            ctl.ground([("base", [])])

            if thy:
                thy.prepare(ctl)

            # Check for interruption after grounding
            if self._interrupted.is_set():
                return

            # Solve
            if self._instance.verbose:
                print(f"    Solving...")

            model_count = 0

            # yield an iterable returning Model objects
            if thy:
                handle = ctl.solve(yield_=True, on_model=thy.on_model, async_=True)
            else:
                handle = ctl.solve(yield_=True, async_=True)

            with handle:
                # Wait for solving with periodic interrupt checks
                while not handle.wait(0.1):  # Check every 100ms
                    if self._interrupted.is_set():
                        handle.cancel()
                        return

                for _ in handle:  # loop on models
                    model_count += 1
                    if self._instance.verbose:
                        print(f"      Found model {model_count}")
                    if (
                        self._instance.models > 0
                        and model_count >= self._instance.models
                    ):
                        break
                    if self._interrupted.is_set():
                        handle.cancel()
                        return

                solve_result = handle.get()

            # Check for interruption before collecting statistics
            if self._interrupted.is_set():
                return

            # Get statistics after solving
            statistics = ctl.statistics
            if "problem" in statistics and "lp" in statistics["problem"]:
                lp_stats = statistics["problem"]["lp"]
                if "rules" in lp_stats:
                    self._stats.rules = lp_stats["rules"]
                if "atoms" in lp_stats:
                    self._stats.atoms = lp_stats["atoms"]
                if "choices" in lp_stats:
                    self._stats.choices = lp_stats["choices"]
                if "constraints" in lp_stats:
                    self._stats.constraints = lp_stats["constraints"]

            self._stats.models_found = model_count

            # Determine result
            if solve_result.satisfiable:
                self._stats.result = Result.SAT
            elif solve_result.unsatisfiable:
                self._stats.result = Result.UNSAT
            elif solve_result.unknown:
                self._stats.result = Result.UNKNOWN

            # Get additional statistics
            self._stats.solve_time = statistics["summary"]["times"]["solve"]
            self._stats.wall_time = statistics["summary"]["times"]["total"]

            if self._instance.verbose:
                print(
                    f"    Result: {self._stats.result}, "
                    f"Wall: {self._stats.wall_time}s, "
                    f"Solve: {self._stats.solve_time}s, "
                    f"Models: {self._stats.models_found}, "
                    f"Rules: {self._stats.rules}"
                )

        except Exception as e:
            if not self._interrupted.is_set():
                self._stats.error = str(e)
                print(
                    f"Error during solving {self._instance.instance_file.name}: {e}",
                    file=sys.stderr,
                )
                if self._instance.verbose:
                    import traceback

                    traceback.print_exc()


def run_clingo_instance(instance: InstanceConfig) -> Stats:
    """Run clingo on a single instance and collect statistics."""

    solver_name = Path(instance.solver_file).stem
    stats = Stats(solver=solver_name, instance=instance.instance_file.name)

    # Shared state for timeout handling
    interrupted = threading.Event()
    ctl_ref = ControlRef(None)  # Use list to allow modification in nested scope
    solve_runner = SolveRunner(instance, stats, interrupted, ctl_ref)

    try:
        # Start solving in a separate thread
        solve_thread = threading.Thread(target=solve_runner, daemon=True)
        solve_thread.start()

        # Wait for the thread with timeout
        solve_thread.join(timeout=instance.timeout if instance.timeout > 0 else None)

        if solve_thread.is_alive():
            # Timeout occurred - interrupt the solver
            if instance.verbose:
                print(f"    Timeout reached, interrupting...")

            interrupted.set()

            # Interrupt the control object if it exists
            ctl_ref.interrupt()

            # Give it a moment to clean up
            solve_thread.join(timeout=2.0)

            # Mark as timeout
            stats.result = Result.TIMEOUT
            stats.wall_time = instance.timeout
            stats.error = f"Timeout after {instance.timeout}s"
            if instance.verbose:
                print(f"    TIMEOUT after {instance.timeout}s")

    except KeyboardInterrupt:
        # Handle Ctrl-C gracefully
        print("\n\nInterrupted by user. Cleaning up...", file=sys.stderr)
        ctl_ref.interrupt()
        raise

    except FileNotFoundError as e:
        stats.error = f"File not found: {e}"
        print(f"Error: {stats.error}", file=sys.stderr)

    except Exception as e:
        stats.error = str(e)
        print(f"Error processing {instance.instance_file.name}: {e}", file=sys.stderr)
        if instance.verbose:
            import traceback

            traceback.print_exc()

    return stats


def write_detailed_results_csv(results: List[Stats], output_file: str):
    """Write detailed results to a CSV file."""
    if not results:
        print("No results to write")
        return

    fieldnames = [
        "solver",
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

        print(f"\nDetailed results written to {output_file}")

    except Exception as e:
        print(f"Error writing results to {output_file}: {e}", file=sys.stderr)


def write_comparison_table(
    results: List[Stats], output_file: str, instances: List[Path]
):
    """Write a comparison table showing solvers side-by-side for each instance."""
    if not results:
        print("No results to write")
        return

    # Get unique solvers
    solvers = sorted(list(set(r.solver for r in results)))

    # Create a lookup: instance -> solver -> stats
    lookup: Dict[str, Dict[str, Stats]] = {}
    for stat in results:
        if stat.instance not in lookup:
            lookup[stat.instance] = {}
        lookup[stat.instance][stat.solver] = stat

    try:
        with open(output_file, "w", newline="") as csvfile:
            # Create headers: instance, then for each solver: result, wall_time, solve_time, rules
            fieldnames = ["instance"]
            for solver in solvers:
                fieldnames.extend(
                    [
                        f"{solver}_result",
                        f"{solver}_wall_time",
                        f"{solver}_solve_time",
                        f"{solver}_rules",
                    ]
                )

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Write a row for each instance
            for instance in instances:
                row = {"instance": instance.name}

                for solver in solvers:
                    if solver in lookup.get(instance.name, {}):
                        stat = lookup[instance.name][solver]
                        row[f"{solver}_result"] = str(stat.result)
                        row[f"{solver}_wall_time"] = f"{stat.wall_time:.3f}"
                        row[f"{solver}_solve_time"] = f"{stat.solve_time:.3f}"
                        row[f"{solver}_rules"] = str(stat.rules)
                    else:
                        row[f"{solver}_result"] = "N/A"
                        row[f"{solver}_wall_time"] = "N/A"
                        row[f"{solver}_solve_time"] = "N/A"
                        row[f"{solver}_rules"] = "N/A"

                writer.writerow(row)

        print(f"Comparison table written to {output_file}")

    except Exception as e:
        print(f"Error writing comparison table to {output_file}: {e}", file=sys.stderr)


def print_summary(results: List[Stats], solvers: List[str]):
    """Print a summary comparing all solvers."""
    if not results:
        return

    print("\n" + "=" * 80)
    print("EXPERIMENT SUMMARY - SOLVER COMPARISON")
    print("=" * 80)

    for solver in solvers:
        solver_results = [r for r in results if r.solver == solver]

        if not solver_results:
            continue

        total = len(solver_results)
        sat = sum(1 for r in solver_results if r.result == Result.SAT)
        unsat = sum(1 for r in solver_results if r.result == Result.UNSAT)
        timeout = sum(1 for r in solver_results if r.result == Result.TIMEOUT)
        unknown = sum(1 for r in solver_results if r.result == Result.UNKNOWN)
        errors = sum(
            1
            for r in solver_results
            if r.error is not None and r.result != Result.TIMEOUT
        )

        avg_wall_time = (
            sum(r.wall_time for r in solver_results) / total if total > 0 else 0
        )
        avg_solve_time = (
            sum(r.solve_time for r in solver_results) / total if total > 0 else 0
        )
        avg_rules = sum(r.rules for r in solver_results) / total if total > 0 else 0
        avg_atoms = sum(r.atoms for r in solver_results) / total if total > 0 else 0

        # Calculate averages only for solved instances
        solved = [r for r in solver_results if r.result in [Result.SAT, Result.UNSAT]]
        if solved:
            avg_solved_wall = sum(r.wall_time for r in solved) / len(solved)
            avg_solved_solve = sum(r.solve_time for r in solved) / len(solved)
        else:
            avg_solved_wall = 0
            avg_solved_solve = 0

        print(f"\n{solver}:")
        print("-" * 80)
        print(f"  Total instances:         {total}")
        print(f"  SAT:                     {sat} ({sat/total*100:.1f}%)")
        print(f"  UNSAT:                   {unsat} ({unsat/total*100:.1f}%)")
        print(f"  TIMEOUT:                 {timeout} ({timeout/total*100:.1f}%)")
        print(f"  UNKNOWN:                 {unknown} ({unknown/total*100:.1f}%)")
        if errors > 0:
            print(f"  ERRORS:                  {errors} ({errors/total*100:.1f}%)")
        print(f"\n  Average wall time:       {avg_wall_time:.3f}s (all instances)")
        print(f"  Average solve time:      {avg_solve_time:.3f}s (all instances)")
        if solved:
            print(f"  Average wall time:       {avg_solved_wall:.3f}s (solved only)")
            print(f"  Average solve time:      {avg_solved_solve:.3f}s (solved only)")
        print(f"\n  Average rules:           {avg_rules:.0f}")
        print(f"  Average atoms:           {avg_atoms:.0f}")

    print("\n" + "=" * 80)

    # Print head-to-head comparison
    print("\nHEAD-TO-HEAD COMPARISON (solved instances only):")
    print("-" * 80)

    for solver in solvers:
        solver_results = [r for r in results if r.solver == solver]
        solved = [r for r in solver_results if r.result in [Result.SAT, Result.UNSAT]]
        solved_count = len(solved)
        avg_time = (
            sum(r.solve_time for r in solved) / solved_count
            if solved_count > 0
            else float("inf")
        )

        print(
            f"  {solver:30s} | Solved: {solved_count:3d} | Avg Time: {avg_time:8.3f}s"
        )

    print("=" * 80)


def main():
    """Main function."""
    args = parse_arguments()

    # Check solver files exist
    for solver_file in args.solvers:
        if not Path(solver_file).exists():
            print(f"Error: Solver file '{solver_file}' does not exist", file=sys.stderr)
            sys.exit(1)

    # Find instances
    instances = find_instances(args.instances, args.extension)

    if not instances:
        sys.exit(1)

    solver_names = [Path(s).stem for s in args.solvers]

    print(f"Found {len(instances)} instance(s)")
    print(f"Solvers: {', '.join(solver_names)}")
    print(f"Timeout: {args.timeout}s per instance")
    if args.const:
        print(f"Constants: {', '.join(args.const)}")
    print(f"Models to find: {args.models if args.models > 0 else 'all'}")
    print(f"Output prefix: {args.output}")
    print()

    # Run experiments
    all_results: List[Stats] = []

    for instance_idx, instance in enumerate(instances, 1):
        print(f"[{instance_idx}/{len(instances)}] Processing {instance.name}:")

        for solver_idx, solver_file in enumerate(args.solvers, 1):
            solver_name = Path(solver_file).stem
            print(f"  [{solver_idx}/{len(args.solvers)}] {solver_name}...", end=" ")
            sys.stdout.flush()

            stats = run_clingo_instance(
                InstanceConfig(
                    solver_file,
                    instance,
                    args.timeout,
                    args.const,
                    args.models,
                    args.verbose,
                    args.theory,
                )
            )

            all_results.append(stats)

            if not args.verbose:
                print(
                    f"{stats.result} "
                    f"(wall: {stats.wall_time:.3f}s, "
                    f"solve: {stats.solve_time:.3f}s)"
                )

    # Write results
    detailed_output = f"{args.output}.csv"
    comparison_output = f"{args.output}_comparison.csv"

    write_detailed_results_csv(all_results, detailed_output)
    write_comparison_table(all_results, comparison_output, instances)

    # Print summary
    print_summary(all_results, solver_names)


if __name__ == "__main__":
    main()
