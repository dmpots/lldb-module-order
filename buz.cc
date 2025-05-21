#include <stdio.h>
char *whoami(void);

// buz.cc
void buzEntry(void) {
  printf("From buz: %s\n", whoami());
} // break here
