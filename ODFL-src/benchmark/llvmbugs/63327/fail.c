int printf(const char *, ...);
short a;
int b = 6, d;
short *c = &a;
int main() {
  d = (b & -b ^ b) < 0;
  *c = d;
  printf("%d\n", a);
}