int printf(const char *, ...);
static int a, b;
char c;
int d(int e) {
  if (e < 8)
    return 0;
  return e < 8 + 32 ? 1 << (e - 68) : 48 & 1 << e;
}
int main() {
  b = 0;
  for (; b < 10; b++) {
    c = 0;
    for (; (char)(d(a) + a) + c < 7; c++)
      ;
  }
  a = 0;
  for (; a <= 32; a++)
    ;
  printf("%d\n", c);
}