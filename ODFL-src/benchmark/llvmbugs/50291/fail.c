int a[36], b, c, d, e, f;
int main() {
for (c = 0; c < 6; c++)
for (d = 0; d < 6; d++)
for (b = 0; b < 6; b++)
a[6 + c] = a[c * 6 + c] ^ 1;
if (a[7] != 0)
__builtin_abort ();
return 0;
}