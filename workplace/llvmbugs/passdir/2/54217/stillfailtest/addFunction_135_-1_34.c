shift (b1, n, c)
    int *b1;
    int n;
    char c;
{
  int nn;
  int cnt = 0;
  int w1;

  for (nn = n / (4 * 4);  nn > 0;  nn--)
    {
      w1 = *b1++;
      if ((char)w1 == c)  cnt++;
      if ((char)(w1 >>= 8) == c)  cnt++;
      if ((char)(w1 >>= 8) == c)  cnt++;
      if ((char)(w1 >>= 8) == c)  cnt++;
      w1 = *b1++;
      if ((char)w1 == c)  cnt++;
      if ((char)(w1 >>= 8) == c)  cnt++;
      if ((char)(w1 >>= 8) == c)  cnt++;
      if ((char)(w1 >>= 8) == c)  cnt++;
      w1 = *b1++;
      if ((char)w1 == c)  cnt++;
      if ((char)(w1 >>= 8) == c)  cnt++;
      if ((char)(w1 >>= 8) == c)  cnt++;
      if ((char)(w1 >>= 8) == c)  cnt++;
      w1 = *b1++;
      if ((char)w1 == c)  cnt++;
      if ((char)(w1 >>= 8) == c)  cnt++;
      if ((char)(w1 >>= 8) == c)  cnt++;
      if ((char)(w1 >>= 8) == c)  cnt++;
    }
  return cnt;
}
int printf(const char *, ...);
int a, b;
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