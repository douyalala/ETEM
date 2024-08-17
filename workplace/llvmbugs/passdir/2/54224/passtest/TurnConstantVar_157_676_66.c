int FL_constant_var = 1;

int a;
unsigned c;
int main() {
  unsigned char e;
  int f = 1;
  a--;
L:
  e = ~c;
  if (!f)
    while (FL_constant_var)
      ;
  c = ~(e - ~0x30);
  if (f > c)
    while (1)
      ;
  if (c > 4294967000)
    __builtin_abort();
  int h = ~a;
  f = a;
  if (h)
    goto L;
  return 0;
}