int func_mutate_rep_stmt_func(int argc, const char **argv);
int printf(const char *, ...);
int a, b, c, d = 7, e;
static void f() {
  int g = 1, h = 1;
  for (; a < 1; a++)
  L:;
    int j = 0;
  if (e)
    while (b)
      if (g)
        printf("0");
  for (; j < 3; j++)
    if (d < 1) {
      printf("%d", c);
      if (j)
        while (h++)
          ;
    }
  if (g) {
    g = 0;
    goto L;
  }
}
int main(int argc, const char **argv){
int ret = func_mutate_rep_stmt_func(argc, argv);
return ret;
}

int func_mutate_rep_stmt_func(int argc, const char **argv){
  f();
  if (a != 2)
    __builtin_abort();
  return 0;
}
