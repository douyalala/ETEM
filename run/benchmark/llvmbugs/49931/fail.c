int a, b, c;
void f() {
  int d = 1, e = 1;
  while (1)
    for (; c < 1; c++) {
      if (!d && e)
        continue;
      if (a < 1) {
        if (e)
          b++;
        return;
      }
      d = 0;
      while (b)
        e++;
    }
}
int main() {
  f();
  if (b != 1)
    __builtin_abort ();
  return 0;
}