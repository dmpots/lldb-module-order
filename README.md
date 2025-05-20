# lldb-module-order

This repo is a standalone experiment to examine non-deterministic load order of
modules in lldb. The module load order in lldb is non-deterministic because they
can be loaded in parallel. If we disable parallel module loading then the order
becomes deterministic.

The purpose of this repo is to provide a collection of simple scripts for
examining the order that modules are loaded in lldb. The intent is to provide a
way to reproduce non-deterministic results in different environments.

## Technique

There are two different scripts that check for determinism. Both use the same
test executable.  The test executable is a simple program that links two shared
libraries. These libraries both contain a definition for the function `whoami`
which is called by `main`.  Since the order that shared libraries are loaded
by the dynamic linker is deterministic the output from running the program is
always the same

```
$ ./build.sh
$ ./a.out
I am libfoo
```

### Checking for deterministic module order in lldb

The `check-module-order.py` test launches lldb with a script that creates the
target and then runs `image list` to view the order of the modules in lldb.  We
can optionally toggle the parallel module loading flag.

Note that dependents are loaded in parallel regardless of the
`target.parallel-module-load` setting so we also have an option to create the
target without loading dependents which can be used to disable parallel loading
of the modules in this case.

Finally, we have an option to show the image list directly after creating the target
(and possibly loading the dependents). This is useful to catch differences in module
order caused by loading dependents in parallel.

```
settings set target.parallel-module-load <true | false>
target create [--no-dependents] a.out
[image list]
run
image list
```

If the modules are loaded in the same order by lldb every time then the output
of running lldb with this command script will be the same.

### Checking for deterministic expression evaluation in lldb

The order that modules are loaded can impact expression evaluation in lldb. When lldb
tries to resolve a function symbol it will look through the modules in the order they
were added to the target modules list. If a function is defined in multiple modules then
changing the order can change the result of the expression evaluation.

The `repro.sh` script can be used to check for non-deterministic output from expression
evaluation in lldb. The script was created as the result of an
[investigation](https://gist.github.com/dmpots/5e8d23410ea81f4cf76f8fd1f0389dd1)
into a non-deterministic failure of the TestDAP_exception_cpp.py lldb test.

It works by running the test binary under lldb until we reach the end of the main
function. Then it evaluates the expression `whoami()`, which should return
`"I am libfoo"` if it correctly matches the real execution of the program. However,
we do see cases where it instead returns `"I am libbar"` because of a difference
in module order kept by lldb and the one used in the dynamic linker.

```
$ ./repro.sh
(lldb) settings set target.parallel-module-load on
(lldb) target create ./a.out
(lldb) break set -f main.cc -l 7
(lldb) break command add -s python
(lldb) run
I am libfoo
#-------------------------------------------#
#            BUG HIT
#-------------------------------------------#
e whoami() --> (const char *) $0 = 0x00007ffff7fb7000 "I am libbar"
Process 1580593 launched: 'a.out' (x86_64)
Process 1580593 stopped
* thread #1, name = 'a.out', stop reason = breakpoint 1.1
    frame #0: 0x0000000000401147 a.out`main at main.cc:7:1
   4
   5    int main(void) {
   6        printf("%s\n", whoami());
-> 7    }
```

## Results

We ran the `check-module-order.py` script across all combinations of parallel
module loading and dependent loading on linux and darwin systems.

The results below were collected with an lldb built off of an upstream
[commit](https://github.com/llvm/llvm-project/commit/fb00fa56b51b191d026eec104905e416bf34bbda)
that will be part of a future LLVM 21 release.

For linux we only get a deterministic order when we disable parallel
loading of both dependents and modules. The remaining configurations are
non-deterministic.

Darwin has an interesting case when it comes to loading dependents in parallel.
It appears to non-deterministically load the modules when it loads dependents
(row 4), but if we only look at the module order after all the modules have been
loaded (row 3) then the order looks deterministic. It seems there is some reordering
of the module list at some point.

```
Config Dependents   Modules   ShowInitial    Linux      Darwin
------------------------------------------------------------
  1        N           N           -           D          D
  2        N           Y           -           ND         ND
  3        Y           N           N           ND         D
  4        Y           N           Y           ND         ND
  5        Y           Y           N           ND         ND
  6        Y           Y           Y           ND         ND
```

## Contents

The following scripts are included in the repo.

* build.sh - build the shared libraries and executable
* clean.sh - clean up all the build artifacts
* foo.cc, bar.cc, main.cc - source files for test executable and libraries
* check-module-order.py - check for deterministic module load order in lldb
* generate-table.py - generate a table for all combinations of check-module-order.py flags.
* repro.sh - reproduce a non-deterministic expression evaluation in lldb

## Requirements

The scripts were tested on both Linux and Darwin and assume that lldb is in the path.
