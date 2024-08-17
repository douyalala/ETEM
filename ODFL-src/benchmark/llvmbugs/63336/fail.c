int a, e, *f;
char b;
volatile int c, d;
int main() {
  int g = 1;
 L:
  if (!b)
    while (d && a)
      g++;
  if (c) {
    if (g) {
      int *i;
      *i = e;
    }
    *f = 0;
    goto L;
  }
  if (!g)
    __builtin_abort();
  return 0;
}