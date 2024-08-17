int func_mutate_rep_stmt_func(int argc, const char **argv);
int printf(const char *, ...);
int a, b;
int main(int argc, const char **argv){
int ret = func_mutate_rep_stmt_func(argc, argv);
return ret;
}

int func_mutate_rep_stmt_func(int argc, const char **argv){
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
