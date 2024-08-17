int printf(const char *, ...);
int a = 1, b;
int main() {
L:
b = a;
if (a) {
unsigned c = a;
a = -1;
if (a == c)
goto L;
}
printf("%d\n", b);
return 0;
}