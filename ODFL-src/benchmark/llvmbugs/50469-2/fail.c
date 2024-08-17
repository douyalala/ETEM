#include <stdio.h>
int a = 1;
int main() {
int b;
L:
b = a;
if (a) {
unsigned c = a;
a = -1;
if (a == c)
goto L;
}
printf("%d\n", b);
return 0;
}