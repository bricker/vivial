#include <stdio.h>
#include <stdlib.h>

#include "./listener/listener.h"

int main(void) {
  printf("Hellow world!\n");
  char* greeting = buildGreeting("Tim", 3);

  printf("%s\n", greeting);
  free(greeting);
  return 0;
}