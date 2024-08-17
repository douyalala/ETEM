int printf(const char *, ...);
int a, b;

# pragma clang optimize off
# pragma GCC optimize(0)
int main() {
  int *c, d = -1;
  while (b)
    d++;
  if (a) {
    printf("0");
    if (d)
      *c = 1;
  }
  if (!d)
    __builtin_abort();
  return 0;
}
# pragma clang optimize on
