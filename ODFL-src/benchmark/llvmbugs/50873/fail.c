int a, c, d;
char e, f;
char(g)(char h, char i) { return i == 0 || h == -128 && i == 1 ? h : h % i; }
char k() {
int j;
d = 3;
for (;; d--)
for (;;) {
short b = g(d, e | d);
j = !b + 1;
f = (1 == b) * j;
c = b;
if (d)
break;
return 1;
}
}
int main() {
k();
printf("%X\n", a);
}