int printf(const char *, ...);
char *a;
long b, c, d, m;
int e, f, j, l;
short g;
int *k = &j;
int main() {
  int *n[] = {&f, &f, &f, &f, &f, &e};
  d = 0;
  for (; d <= 1; d++) {
    g = 0;
    for (; g <= 4; g++) {
      char h[] = {0, 0, 4};
      char *i = h;
      a = i;
      do {
        a++;
        b /= 10;
      } while (b);
      c = a - i;
      while (i < a){
        *i = *(i+1);
        i++;
      }
      *k ^= c;
      k = n[d + g];
      l ^= m;
    }
  }
  printf("%d\n", e);
}