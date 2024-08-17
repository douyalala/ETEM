int a;
int main() {
int b;
L:
b = a;
if (a <= 0) {
int c = a;
a = 1;
if (c)
goto L;
}
if (b) {
b = a;
__builtin_abort ();
}
return 0;
}