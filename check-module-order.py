#!/usr/bin/env python3
import argparse
import subprocess
import sys
import difflib

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument('--iteration-count', type=int, default=10, help='Number of iterations to perform')
    parser.add_argument('--parallel-module-load', action="store_const", const=True, default=True, help='Enable parallel module loading')
    parser.add_argument('--no-parallel-module-load', action="store_const", const=False, dest="parallel_module_load", help='Disable parallel module loading')
    parser.add_argument('--dependents', action="store_const", const=True, default=True, help='Load dependent modules')
    parser.add_argument('--no-dependents', action="store_const", const=False, dest="dependents", help='Do not load dependent modules')
    parser.add_argument('--lldb', help='Path to lldb binary', default='lldb')
    parser.add_argument('--inferior', help='Path to inferior binary', default='a.out')
    parser.add_argument('--script-path', help='Path to generated script', default='/tmp/check_module_order.lldb')
    parser.add_argument('--show-initial-list', help='Show initial module list', default=True, action="store_const", const=True)
    parser.add_argument('--no-show-initial-list', help='Do not show initial module list', dest="show_initial_list", action="store_false")
    return parser.parse_args()

def generate_lldb_script_contents(options):
    dependents = ""
    if not options.dependents:
        dependents = "--no-dependents"
    initial_list = "image list"
    if not options.show_initial_list:
        initial_list = ""
    script = f"""
settings set target.parallel-module-load {options.parallel_module_load}
target create {dependents} {options.inferior}
{initial_list}
run
image list
"""
    return script

def generate_lldb_script(options):
    with open(options.script_path, "w") as script_file:
        script_file.write(generate_lldb_script_contents(options))

def sanitize_output(output):
    import re
    return re.sub(r"Process \d+", "Process X", output)

def run_one_time(options):
    lldb = options.lldb
    proc = subprocess.run([lldb, "-S", options.script_path, "-b"], check=True, capture_output=True, text=True)
    return sanitize_output(proc.stdout + proc.stderr)

def generate_baseline_output(options):
    print("Generating baseline output")
    return run_one_time(options)

def check_deterministic_output(options):
    generate_lldb_script(options)
    initial_output = run_one_time(options)

    print(f"Running {options.iteration_count} iterations to check for determinism")
    for i in range(options.iteration_count):
        print(f"\r{i+1}/{options.iteration_count}", end="")
        output = run_one_time(options)
        if output != initial_output:
            print()
            print(f"Output mismatch on iteration {i+1}")
            print("======================================================")
            print("                 Initial output                       ")
            print("======================================================")
            print(f"{initial_output}")
            print()
            print("======================================================")
            print("                    New output                        ")
            print("======================================================")
            print(f"{output}")
            print("======================================================")
            print("                     Diff                             ")
            print("======================================================")
            diff = difflib.unified_diff(initial_output.splitlines(), output.splitlines(), fromfile="Initial Output", tofile="New Output")
            for line in diff:
                line = line.rstrip()
                print(line)
            return False
    print()
    return True

def build():
    print("Building test binary")
    subprocess.run(["./build.sh"], check=True)

def main():
    options = parse_arguments()
    build()
    success = check_deterministic_output(options)

    if success:
        print("All outputs match")
        sys.exit(0)
    else:
        print("Output mismatch detected")
        sys.exit(1)

if __name__ == "__main__":
    main()
    pass
