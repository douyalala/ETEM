int a;
long b;
unsigned c;
static long *d = &b;
short e;
static short *f = &e, **g = &f, ***h = &g;
void i() {
  short *j[1];
  j[a] = &e;
  **h = j[0];
}
int main() {
  ;;
  unsigned short k = ~e >> a;
  long l = ~(~((c - 1) ^ (k - b)) | a);
  *d = *f = 1;
if (b > l)
    __builtin_abort();
  return 0;
}