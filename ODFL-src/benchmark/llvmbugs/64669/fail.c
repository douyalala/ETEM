int printf(const char *, ...);
long a, e;
int b[72];
int c, g, h;
char d;
int main() {
  int *f = &b[25], *i = &c;
  d = f != i;
  e = a * d;
  *f = e + d;
  printf("%d\n", b[25]);
}