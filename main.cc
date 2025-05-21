
#include <stdio.h>
char *whoami(void);
void buzEntry(void);
void barEntry(void);

int main(void) {
    printf("From main: %s\n", whoami());
    buzEntry();
    barEntry();
}
