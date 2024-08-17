int printf(const char *, ...);
int a, b, c;
long d;
const unsigned *e;
const unsigned **f[3];
static char(g)(unsigned h, int j) { return h > j ? h : h << j; }
static short k() {
  char l = 1;
  b = 0;
  for (; b <= 3; b++) {
    char *m = &l;
    int *n = &c;
    int i = 0;
    for (; i < 3; i++)
      f[i] = &e;
    *n = g((*m)--, 7);
    if (*n)
      ;
    else {
      for (; i < 9; i++)
        f[0] || (d = 2);
      if (0 < *n)
        ;
      else
        return 0;
    }
    printf("%d\n", *n);
  }
  return 1;
}
int main() {
  k();
}