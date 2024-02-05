#include <stdio.h>
#include <stdlib.h>

char* buildGreeting(char* name, int len) {
  char* greeting = malloc(sizeof(char) * (11 + len));
  sprintf(greeting, "Hi there %s!", name);
  return greeting;
}