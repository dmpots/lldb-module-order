#include <stdio.h>

const char *whoami() {
    return "I am libbar";
}

// bar.cc
void barEntry() {
    printf("From bar: %s\n", whoami());
} // break here
