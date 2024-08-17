int a = 1, b = 1;
int main() {
short d, g, i;
int e = 34000, h;
d = b;
g = 100 | b;
L1:
i = g;
L2:
g = ~(d / e);
e = ~((2 / g) & d);
h = a;
while (!e) {
a = b;
e = ~(1L << i);
}
if (g > 0)
goto L2;
if (!g)
goto L1;
if (h < e)
__builtin_abort ();
return 0;
}