void printf();
long a;
int b, d, e;
int *c;
void f(int *g) { *g = b; }
char h() {
long *i = &a;
for (;;) {
int j = 0;
for (;; a++) {
b = 2;
for (; b <= 8; b++) {
c = &j;
if (j)
break;
}
if (j)
break;
j = 1;
}
e = 3;
for (; e <= 8; e++) {
int k;
d = 3;
for (; d <= 8; d++) {
*i = k;
f(&k);
}
if (a)
return 0;
}
}
}
int main() {
h();
printf("%d\n", a);
}