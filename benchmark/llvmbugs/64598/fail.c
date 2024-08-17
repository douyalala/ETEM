int printf(const char *, ...);
int a, d, e, f, h, j, t, q;
char c, s;
signed char g;
signed char *i = &g;
int *k = &h;
int **l = &k;
signed char **m = &i;
signed char ***r = &m;
static signed char ****n = &r;
long o, u;
int p[7];
void v() {
  t = 0;
  for (; t < 9; t++) {
    q = 0;
    for (; c + q; q++)
      p[q] = 3;
  }
}
void w(long x, char y) {
  for (; o;) {
    v();
    s = x;
    u = y;
  }
}
int main() {
  for (; d <= 3; d++) {
    e = 0;
    for (; e <= 3; e++) {
      int *b;
      f = 3;
      for (; f; f--) {
        w(****n, **l);
        b = &j;
        *b = **l + ***r;
      }
    }
  }
  for (; **l;)
    ;
  printf("%X\n", a);
}