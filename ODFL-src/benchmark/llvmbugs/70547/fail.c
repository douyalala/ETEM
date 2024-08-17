int printf(const char *, ...);
int a;
static int b;
short(c)(short d, int e) { return d >> e; }
char *f(int d, char *e) {
  if ((d & 1) == 0)
    return e;
  switch (d) {
  case 7:
  case 49:
  case 1:
    return "";
  case 11:
    return "0";
  case 3:
    return "0";
  }
  return "1";
}
char g(int d) {
  char h = 0, i = *f(d, &h);
  return i;
}
char j(int d) {
  for (;;) {
    if (g(d + 7) + d)
      return 0;
    for (; b - 30; b+=0)
      ;
  }
}
void k() {
  int l = -8, m = c(l, 8);
  j(m);
}
int main() {
  k();
  printf("%X\n", a);
}