short a, b, *c = &b;
unsigned d = 4294967295U;
int e() {
  while (1) {
    while (d <= 1 && b <= d)
      *c = 1;
    int f = d;
    d = a / f;
    if (f < 4294967295U)
      continue;
    return 1;
  }
}
int main() {
  e();
  return 0;
}