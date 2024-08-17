int printf(const char *, ...);
int a, b;
short c;
unsigned short e = 65535;
static short f;
static char g[10][1][4];
static long h = -10;
unsigned short *i = &e;
long j(long k, long l) {
  long d = k + l;
  return k ? d - 1 : 9;
}
void n() {
  int m = 0;
  --g[0][0][2];
  c = 0;
  for (; c >= 0; c--)
    for (; h + *i - 65525 + m >= 0; m--) {
      f = 2;
      for (; f < 4; f++)
        g[(char)j(91, *i - 65625)][*i + c - 65535][f] = 5;
    }
}
int main() {
  n();
  printf("%d\n", g[0][0][2]);
}