int printf (const char *, ...);
static int *a, **b = &a;
int c, d = 1, e;
int main() {
  int f, g;
  f = d;
  for (g = 0; g < 2; g++) {
    if (e) {
      printf("%d", e);
      if (f)
        c = **b;
    }
    if (!f)
      while (1)
        while (g)
          ;
  }
  return 0;
}