int a;
unsigned c;
int main() {
  unsigned char e;
  int f = 1;
  a--;
L:
  e = ~c;
  if (!f)
    while (1)
      ;
  c = ~(e - ~0x30);
  if (f > c)
    
# pragma clang optimize off
# pragma GCC optimize(0)
while (1)
      ;
# pragma clang optimize on

  if (c > 4294967000)
    __builtin_abort();
  int h = ~a;
  f = a;
  if (h)
    goto L;
  return 0;
}