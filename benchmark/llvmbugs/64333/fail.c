int printf(const char *, ...);
int a;
static long b = 2065201973, c;
char d, e;
short f;
short(g)(short h, short i) { return h + i; }
int j(int h) {
  if (h < 8)
    return 0;
  return (h < 48) & (1 << (h - 2));
}
void k(long *h) {}
int main() {
  long *l = &b;
  k(l);
  for (; c >= 0; --c) {
    for (; d <= 8; d = e = g(e, 4)) {
      f = 0;
      for (; (unsigned short)(j(b - 2065201972) + b - 2065201973) + f <= 4; f++)
        ;
    }
    for (; f + (int)b - 2065201978;)
      ;
  }
  printf("%X\n", a);
}