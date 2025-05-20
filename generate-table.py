#!/usr/bin/env python3
import subprocess
import itertools

# Define the options
options = ['--no-dep', '--no-par', '--no-show']

# Generate all combinations of the options
combinations = []
for r in range(len(options) + 1):
    combinations.extend(itertools.combinations(options, r))

combinations = [
    ["--no-dep", "--no-par", "--no-show"],
    ["--no-dep", "--no-par", "--show"],
    ["--no-dep", "--par   ", "--no-show"],
    ["--no-dep", "--par   ", "--show"],
    ["--dep   ", "--no-par", "--no-show"],
    ["--dep   ", "--no-par", "--show"],
    ["--dep   ", "--par   ", "--no-show"],
    ["--dep   ", "--par   ", "--show"],
]

# Prepare the results table
results = []

# Execute the script with each combination and record the result
for combo in combinations:
    command = ['python3', 'check-module-order.py'] + [c.strip() for c in list(combo)]
    print(" ".join(command))
    try:
        subprocess.run(command, check=True)
        results.append((combo, 'D'))
    except subprocess.CalledProcessError:
        results.append((combo, 'ND'))

# Print the results table
print(f"{'Dependents':^12}{'Modules':^12}{'ShowInitial':^12}{'Result':^12}")
print("-" * 60)
for combo, result in results:
    for flag in combo:
        val = "N" if "--no" in flag else "Y"
        print(f"{val:^12}", end="")
    print(f"{result:^12}")
