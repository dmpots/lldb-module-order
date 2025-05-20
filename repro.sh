#!/bin/bash
#set -x

# Rebuild the binary
./build.sh

INFERIOR=./a.out
LLDB=lldb

cat << EOF > /tmp/repro.lldb
settings set target.parallel-module-load on
target create $INFERIOR
break set -f main.cc -l 7
break command add -s python
    who = str(frame.EvaluateExpression("whoami()"))
    if "libfoo" not in who:
        print("#-------------------------------------------#")
        print("#            BUG HIT")
        print("#-------------------------------------------#")
        print(f"e whoami() --> {who}")
        return True
    else:
        print("#-------------------------------------------#")
        print("#            BUG NOT HIT")
        print("#-------------------------------------------#")
        # Can't figure out a better way to force lldb to quit
        import os
        os._exit(0)
        return False
DONE
run
EOF

# Will loop forever. Use `quit 1` when lldb is at a breakpoint to quit.
while $LLDB -S /tmp/repro.lldb ; do :; done
