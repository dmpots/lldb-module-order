#!/bin/bash
set -x -e

./build.sh
./a.out

lldb -b -o "settings set target.parallel-module-load false" -o "target create --no-dependents ./a.out" -o "b main" -o "b buzEntry" -o "b barEntry" -o "r" -o "image list" -o "e whoami()" -o "c" -o "e whoami()" -o "c" -o "e whoami()" -o "c"
