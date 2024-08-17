int func_mutate_rep_stmt_func(int argc, const char **argv);
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
int main(int argc, const char **argv){
int ret = func_mutate_rep_stmt_func(argc, argv);
return ret;
}

int func_mutate_rep_stmt_func(int argc, const char **argv){
  *d = *f = 1;
  unsigned short k = ~e >> a;
  long l = ~(~((c - 1) ^ (k - b)) | a);
  if (b > l)
    __builtin_abort();
  return 0;
}
