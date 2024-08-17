int printf(const char *, ...);
int a, b, c, d;
long e;
int f(int g) {
  if (g < 68)
    return 0;
  return g < 768 ? 5 & 1 << (g - 68) : 1 << (g - 2);
}
int main() {
  for (; d < 2; d++)
    c = 1;
  a = 1;
  for (; a <= 9; a++)
    ;
  for (;;) {
    for (; f(a) + b - 30 + e; ++e)
      ;
    if (c)
      break;
  }
  printf("%d\n", (int)e);
}